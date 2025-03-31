"""
The justification for this module is to address the following issue:
* Each event is typically tied to a span (for example, crew kickoffs, tasks, tool usages, etc., all have spans).
* Spans can have child spans (for example, a crew kickoff span contains all child event spans).
* Phoenix's GraphQL node "descendants" property is used to extract child spans from our crew kickoff span.
* However, the endpoint does not extract out descendants until the span has "ended".
* OpenInference's CrewAIInstrumentor wrapper classes only end the span after the event is complete.

To get around this, we follow this pattern:
* We monkey-patch the original wrapper classes used for instrumentation
* We purposefully "end" the span early so Phoenix's graphQL client can return these nested spans

"""

# Manual patch required for CrewAI compatability
from crewai.tools import BaseTool
from opentelemetry.trace import SpanKind
from typing import Any, Optional, List
from crewai import Agent
from openinference.semconv.trace import (
    OpenInferenceSpanKindValues,
    SpanAttributes,
)
from openinference.instrumentation import (
    get_attributes_from_context,
)
from typing import Any, Callable, Iterator, Mapping, Tuple
from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes
from openinference.instrumentation import get_attributes_from_context, safe_json_dumps
from opentelemetry.util.types import AttributeValue
from opentelemetry import trace as trace_api
from opentelemetry import context as context_api
from typing import Any, Callable, Iterator, List, Mapping, Optional, Tuple
from inspect import signature
from enum import Enum
import json
import sys

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")


class SafeJSONEncoder(json.JSONEncoder):
    """
    Safely encodes non-JSON-serializable objects.
    """

    def default(self, o: Any) -> Any:
        try:
            return super().default(o)
        except TypeError:
            if hasattr(o, "dict") and callable(o.dict):  # pydantic v1 models, e.g., from Cohere
                return o.dict()
            return repr(o)


def _flatten(mapping: Optional[Mapping[str, Any]]) -> Iterator[Tuple[str, AttributeValue]]:
    if not mapping:
        return
    for key, value in mapping.items():
        if value is None:
            continue
        if isinstance(value, Mapping):
            for sub_key, sub_value in _flatten(value):
                yield f"{key}.{sub_key}", sub_value
        elif isinstance(value, List) and any(isinstance(item, Mapping) for item in value):
            for index, sub_mapping in enumerate(value):
                for sub_key, sub_value in _flatten(sub_mapping):
                    yield f"{key}.{index}.{sub_key}", sub_value
        else:
            if isinstance(value, Enum):
                value = value.value
            yield key, value


def _get_input_value(method: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """
    Parses a method call's inputs into a JSON string. Ensures a consistent
    output regardless of whether the those inputs are passed as positional or
    keyword arguments.
    """

    # For typical class methods, the corresponding instance of inspect.Signature
    # does not include the self parameter. However, the inspect.Signature
    # instance for __call__ does include the self parameter.
    method_signature = signature(method)
    first_parameter_name = next(iter(method_signature.parameters), None)
    signature_contains_self_parameter = first_parameter_name in ["self"]
    bound_arguments = method_signature.bind(
        *(
            # the value bound to the method's self argument is discarded below, so pass None
            [None] if signature_contains_self_parameter else []  # no self parameter, so no need to pass a value
        ),
        *args,
        **kwargs,
    )
    return safe_json_dumps(
        {
            **{
                argument_name: argument_value
                for argument_name, argument_value in bound_arguments.arguments.items()
                if argument_name not in ["self", "kwargs"]
            },
            **bound_arguments.arguments.get("kwargs", {}),
        },
        cls=SafeJSONEncoder,
    )


class _ExecuteCoreWrapper:
    def __init__(self, tracer: trace_api.Tracer) -> None:
        self._tracer = tracer

    def __call__(
        self,
        wrapped: Callable[..., Any],
        instance: Any,
        args: Tuple[Any, ...],
        kwargs: Mapping[str, Any],
    ) -> Any:
        if context_api.get_value(context_api._SUPPRESS_INSTRUMENTATION_KEY):
            return wrapped(*args, **kwargs)
        if instance:
            span_name = f"{instance.__class__.__name__}.{wrapped.__name__}"
        else:
            span_name = wrapped.__name__
        with self._tracer.start_as_current_span(
            span_name,
            attributes=dict(
                _flatten(
                    {
                        OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.AGENT,
                        SpanAttributes.INPUT_VALUE: _get_input_value(
                            wrapped,
                            *args,
                            **kwargs,
                        ),
                    }
                )
            ),
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            agent = args[0] if args else None
            crew = agent.crew if agent else None
            task = instance

            if crew:
                span.set_attribute("crew_key", crew.key)
                span.set_attribute("crew_id", str(crew.id))
            span.set_attribute("task_key", task.key)
            span.set_attribute("task_id", str(task.id))

            if crew and crew.share_crew:
                span.set_attribute("formatted_description", task.description)
                span.set_attribute("formatted_expected_output", task.expected_output)

            # Try ending the span early
            # print("ENDING SPAN EARLY")
            span.end()

            try:
                response = wrapped(*args, **kwargs)
            except Exception as exception:
                span.set_status(trace_api.Status(trace_api.StatusCode.ERROR, str(exception)))
                span.record_exception(exception)
                raise
            span.set_status(trace_api.StatusCode.OK)
            span.set_attribute(OUTPUT_VALUE, response)
            span.set_attributes(dict(get_attributes_from_context()))
        return response


class _KickoffWrapper:
    def __init__(self, tracer: trace_api.Tracer) -> None:
        self._tracer = tracer

    def __call__(
        self,
        wrapped: Callable[..., Any],
        instance: Any,
        args: Tuple[Any, ...],
        kwargs: Mapping[str, Any],
    ) -> Any:
        if context_api.get_value(context_api._SUPPRESS_INSTRUMENTATION_KEY):
            return wrapped(*args, **kwargs)
        span_name = f"{instance.__class__.__name__}.kickoff"
        with self._tracer.start_as_current_span(
            span_name,
            record_exception=False,
            set_status_on_exception=False,
            attributes=dict(
                _flatten(
                    {
                        OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.CHAIN,
                    }
                )
            ),
        ) as span:
            crew = instance
            inputs = kwargs.get("inputs", None) or (args[0] if args else None)

            span.set_attribute("crew_key", crew.key)
            span.set_attribute("crew_id", str(crew.id))
            span.set_attribute("crew_inputs", json.dumps(inputs) if inputs else "")
            span.set_attribute(
                "crew_agents",
                json.dumps(
                    [
                        {
                            "key": agent.key,
                            "id": str(agent.id),
                            "role": agent.role,
                            "goal": agent.goal,
                            "backstory": agent.backstory,
                            "verbose?": agent.verbose,
                            "max_iter": agent.max_iter,
                            "max_rpm": agent.max_rpm,
                            "i18n": agent.i18n.prompt_file,
                            "delegation_enabled": agent.allow_delegation,
                            "tools_names": [tool.name.casefold() for tool in agent.tools or []],
                        }
                        for agent in crew.agents
                    ]
                ),
            )
            span.set_attribute(
                "crew_tasks",
                json.dumps(
                    [
                        {
                            "id": str(task.id),
                            "description": task.description,
                            "expected_output": task.expected_output,
                            "async_execution?": task.async_execution,
                            "human_input?": task.human_input,
                            "agent_role": task.agent.role if task.agent else "None",
                            "agent_key": task.agent.key if task.agent else None,
                            "context": [task.description for task in task.context] if task.context else None,
                            "tools_names": [tool.name.casefold() for tool in task.tools or []],
                        }
                        for task in crew.tasks
                    ]
                ),
            )

            # Try ending the span early
            # print("ENDING SPAN EARLY")
            span.end()

            try:
                crew_output = wrapped(*args, **kwargs)
                usage_metrics = crew.usage_metrics
                if isinstance(usage_metrics, dict):
                    if (prompt_tokens := usage_metrics.get("prompt_tokens")) is not None:
                        span.set_attribute(LLM_TOKEN_COUNT_PROMPT, int(prompt_tokens))
                    if (completion_tokens := usage_metrics.get("completion_tokens")) is not None:
                        span.set_attribute(LLM_TOKEN_COUNT_COMPLETION, int(completion_tokens))
                    if (total_tokens := usage_metrics.get("total_tokens")) is not None:
                        span.set_attribute(LLM_TOKEN_COUNT_TOTAL, int(total_tokens))
                else:
                    # version 0.51 and onwards
                    span.set_attribute(LLM_TOKEN_COUNT_PROMPT, usage_metrics.prompt_tokens)
                    span.set_attribute(LLM_TOKEN_COUNT_COMPLETION, usage_metrics.completion_tokens)
                    span.set_attribute(LLM_TOKEN_COUNT_TOTAL, usage_metrics.total_tokens)

            except Exception as exception:
                span.set_status(trace_api.Status(trace_api.StatusCode.ERROR, str(exception)))
                span.record_exception(exception)
                raise
            span.set_status(trace_api.StatusCode.OK)
            if crew_output_dict := crew_output.to_dict():
                span.set_attribute(OUTPUT_VALUE, json.dumps(crew_output_dict))
                span.set_attribute(OUTPUT_MIME_TYPE, "application/json")
            else:
                span.set_attribute(OUTPUT_VALUE, str(crew_output))
            span.set_attributes(dict(get_attributes_from_context()))

        # We need a signal that our crew has completed. We can't check the
        # attributes of the previous span because we're ending the span early
        # (so technically all of those attributes after the fact are not being added
        # to the span). To facilitate a signal that a span is complete, we are
        # manually sending a Crew.complete span.
        with self._tracer.start_as_current_span(
            "Crew.complete",
            record_exception=False,
            kind=SpanKind.INTERNAL,
            set_status_on_exception=False,
        ) as span:
            span.set_status(trace_api.StatusCode.OK)
            span.set_attribute("crew_output", crew_output.raw)
            span.end()

        return crew_output


class _ToolUseWrapper:
    def __init__(self, tracer: trace_api.Tracer) -> None:
        self._tracer = tracer

    def __call__(
        self,
        wrapped: Callable[..., Any],
        instance: Any,
        args: Tuple[Any, ...],
        kwargs: Mapping[str, Any],
    ) -> Any:
        if context_api.get_value(context_api._SUPPRESS_INSTRUMENTATION_KEY):
            return wrapped(*args, **kwargs)
        if instance:
            span_name = f"{instance.__class__.__name__}.{wrapped.__name__}"
        else:
            span_name = wrapped.__name__
        with self._tracer.start_as_current_span(
            span_name,
            attributes=dict(
                _flatten(
                    {
                        OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.TOOL,
                        SpanAttributes.INPUT_VALUE: _get_input_value(
                            wrapped,
                            *args,
                            **kwargs,
                        ),
                    }
                )
            ),
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            tool = kwargs.get("tool")
            tool_name = ""
            if tool:
                tool_name = tool.name
            span.set_attribute("function_calling_llm", instance.function_calling_llm)
            span.set_attribute(SpanAttributes.TOOL_NAME, tool_name)

            # End span early
            span.end()

            try:
                response = wrapped(*args, **kwargs)
            except Exception as exception:
                span.set_status(trace_api.Status(trace_api.StatusCode.ERROR, str(exception)))
                span.record_exception(exception)
                raise
            span.set_status(trace_api.StatusCode.OK)
            span.set_attribute(OUTPUT_VALUE, response)
            span.set_attributes(dict(get_attributes_from_context()))

        # Start a parent span for the task execution
        with self._tracer.start_as_current_span(
            name="ToolUsage._end_use",
            kind=SpanKind.INTERNAL,
            attributes={
                "tool.name": tool_name,
                OUTPUT_VALUE: response,
            },
        ) as parent_span:
            # End the span right away
            parent_span.end()

        return response


INPUT_VALUE = SpanAttributes.INPUT_VALUE
OPENINFERENCE_SPAN_KIND = SpanAttributes.OPENINFERENCE_SPAN_KIND
OUTPUT_VALUE = SpanAttributes.OUTPUT_VALUE
OUTPUT_MIME_TYPE = SpanAttributes.OUTPUT_MIME_TYPE
LLM_TOKEN_COUNT_PROMPT = SpanAttributes.LLM_TOKEN_COUNT_PROMPT
LLM_TOKEN_COUNT_COMPLETION = SpanAttributes.LLM_TOKEN_COUNT_COMPLETION
LLM_TOKEN_COUNT_TOTAL = SpanAttributes.LLM_TOKEN_COUNT_TOTAL


class WrappedAgent(Agent):
    agent_studio_id: Optional[str] = None
    _tracer = None

    def __init__(self, agent_studio_id: str, tracer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_studio_id = agent_studio_id
        self._tracer = tracer

    def execute_task(
        self,
        task: Any,
        context: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
    ) -> str:
        print("HELLO THERE I AM DOING SOMETHING")

        # Start a parent span for the task execution
        with self._tracer.start_as_current_span(
            name="Agent._start_task",
            kind=SpanKind.INTERNAL,
            attributes={
                "agent_studio_id": self.agent_studio_id,
                "agent_role": self.role,
                "task.context": getattr(task, "context", None),
                "task.description": getattr(task, "description", None),
                "task.expected_output": getattr(task, "expected_output", None),
                "context": context,
            },
        ) as parent_span:
            try:
                # End the span right away
                parent_span.end()

                # Execute the task and capture the result
                result = super().execute_task(task, context, tools)
            except Exception as e:
                raise

        # Start a parent span for the task execution
        with self._tracer.start_as_current_span(
            name="Agent._end_task",
            kind=SpanKind.INTERNAL,
            attributes={
                "agent_studio_id": self.agent_studio_id,
                "agent_role": self.role,
                "task.context": getattr(task, "context", None),
                "task.description": getattr(task, "description", None),
                "task.expected_output": getattr(task, "expected_output", None),
                "context": context,
            },
        ) as parent_span:
            # End the span right away
            parent_span.end()

        return result
