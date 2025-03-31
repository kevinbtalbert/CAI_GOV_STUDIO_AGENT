# No top level studio.db imports allowed to support wokrflow model deployment

from typing import List, Dict, Optional, Any, Type
from pydantic import BaseModel
import sys
from contextlib import contextmanager
import os
import importlib
from opentelemetry.context import attach, detach
import asyncio
from crewai import Task, Crew, LLM as CrewAILLM, Agent
from crewai.tools import BaseTool

import engine.types as input_types
from engine.utils import extract_tool_class_name
from engine.crewai.llms import get_crewai_llm_object_direct
from engine.tracing import WrappedAgent


def _import_module_with_isolation(module_name: str, module_path: str):
    """
    Import a module while ensuring isolation from previously imported modules,
    while properly handling relative imports within the module.

    Args:
        module_name: Name of the module to import (without .py extension)
        module_path: Absolute path to the directory containing the module
    """

    @contextmanager
    def temporary_sys_path(path):
        """Temporarily add a path to sys.path"""
        sys.path.insert(0, path)
        try:
            yield
        finally:
            if path in sys.path:
                sys.path.remove(path)

    # Generate a unique name for the module to avoid namespace conflicts
    unique_module_name = f"{module_name}_{hash(module_path)}"

    # Remove any existing module with the same name from sys.modules
    for key in list(sys.modules.keys()):
        if key == unique_module_name or key.startswith(f"{unique_module_name}."):
            del sys.modules[key]

    # Create the full path to the module file
    full_path = os.path.join(module_path, f"{module_name}.py")

    # Load the module specification
    spec = importlib.util.spec_from_file_location(unique_module_name, full_path)
    if spec is None:
        raise ImportError(f"Could not load module specification from {full_path}")

    # Create the module
    module = importlib.util.module_from_spec(spec)

    # Add the module path to sys.modules to handle relative imports
    sys.modules[unique_module_name] = module

    # Add the module's directory to sys.path temporarily and execute the module
    with temporary_sys_path(module_path):
        if spec.loader is None:
            raise ImportError(f"Could not load module from {full_path}")
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            # Clean up sys.modules in case of an error
            if unique_module_name in sys.modules:
                del sys.modules[unique_module_name]
            raise e

    return module


def _get_embedded_crewai_tool(
    tool_instance: input_types.Input__ToolInstance, user_params_kv: Dict[str, str]
) -> BaseTool:
    relative_module_dir = os.path.abspath(tool_instance.source_folder_path)
    module = _import_module_with_isolation(tool_instance.python_code_file_name.replace(".py", ""), relative_module_dir)
    with open(os.path.join(relative_module_dir, tool_instance.python_code_file_name), "r") as code_file:
        tool_code = code_file.read()
        tool_class_name = extract_tool_class_name(tool_code)
    studio_tool_class: Type[BaseModel] = getattr(module, tool_class_name)
    user_param_base_model: Type[BaseModel] = getattr(module, "UserParameters")
    user_params = user_param_base_model(**user_params_kv)
    studio_tool_instance = studio_tool_class(user_parameters=user_params)

    class EmbeddedCrewAITool(BaseTool):
        name: str = studio_tool_instance.name
        description: str = studio_tool_instance.description
        args_schema: Type[BaseModel] = studio_tool_instance.args_schema

        def _run(self, *args, **kwargs):
            return studio_tool_instance._run(*args, **kwargs)

    crewai_tool: BaseTool = EmbeddedCrewAITool()

    # This is a workaround to use DB-specific name in the tool rather
    # than the "mandatory" field set within the tool code.
    crewai_tool.name = tool_instance.name
    crewai_tool._generate_description()
    # Force Python to reload module paths
    importlib.invalidate_caches()
    return crewai_tool


def _get_crewai_agent(
    agent: input_types.Input__Agent,
    crewai_tools: Optional[List[BaseTool]] = None,
    llm_model: Optional[CrewAILLM] = None,
    tracer=None,
) -> Agent:
    return WrappedAgent(
        agent_studio_id=agent.id,
        tracer=tracer,
        role=agent.crew_ai_role,
        backstory=agent.crew_ai_backstory,
        goal=agent.crew_ai_goal,
        allow_delegation=agent.crew_ai_allow_delegation,
        verbose=agent.crew_ai_verbose,
        cache=agent.crew_ai_cache,
        max_iter=10 if agent.crew_ai_max_iter <= 0 else agent.crew_ai_max_iter,
        tools=crewai_tools or list(),
        llm=llm_model,
    )


def create_crewai_objects(
    collated_input: input_types.CollatedInput,
    tool_user_params: Dict[str, Dict[str, str]],
    tracer=None,
) -> input_types.CrewAIObjects:
    language_models: Dict[str, CrewAILLM] = {}
    for language_model in collated_input.language_models:
        language_models[language_model.model_id] = get_crewai_llm_object_direct(language_model)

    tools: Dict[str, BaseTool] = {}
    for t_ in collated_input.tool_instances:
        tools[t_.id] = _get_embedded_crewai_tool(t_, tool_user_params.get(t_.id, {}))

    agents: Dict[str, Agent] = {}
    for agent in collated_input.agents:
        crewai_tools = [tools[tool_id] for tool_id in agent.tool_instance_ids]
        model_id = agent.llm_provider_model_id
        if not model_id:
            model_id = collated_input.default_language_model_id
        agents[agent.id] = _get_crewai_agent(agent, crewai_tools, language_models[model_id], tracer)

    tasks: Dict[str, Task] = {}
    for task_input in collated_input.tasks:
        agent_for_task: Agent = agents[task_input.assigned_agent_id] if task_input.assigned_agent_id else None
        tasks[task_input.id] = Task(
            description=task_input.description,
            expected_output=task_input.expected_output,
            agent=agent_for_task,
            tools=agent_for_task.tools if agent_for_task else None,
        )

    workflow_input = collated_input.workflow
    crew = Crew(
        name=workflow_input.name,
        process=workflow_input.crew_ai_process,
        agents=[agents[agent_id] for agent_id in workflow_input.agent_ids],
        tasks=[tasks[task_id] for task_id in workflow_input.task_ids],
        manager_agent=agents[workflow_input.manager_agent_id] if workflow_input.manager_agent_id else None,
        manager_llm=language_models[workflow_input.llm_provider_model_id]
        if workflow_input.llm_provider_model_id
        else None,
        verbose=True,
    )

    return input_types.CrewAIObjects(
        language_models=language_models,
        tools=tools,
        agents=agents,
        tasks=tasks,
        crews={workflow_input.id: crew},
    )


async def run_workflow_async(
    collated_input: Any,
    tool_user_params: Dict[str, Dict[str, str]],
    inputs: Dict[str, Any],
    parent_context: Any,  # Use the parent context
    tracer=None,
) -> None:
    """
    Run the workflow task in the background using the parent context.
    """

    def executor_task():
        # Attach the parent context in the background thread
        token = attach(parent_context)

        try:
            # Run the actual workflow logic within the propagated context
            crewai_objects = create_crewai_objects(collated_input, tool_user_params, tracer)
            crew = crewai_objects.crews[collated_input.workflow.id]

            # Perform the kickoff
            crew.kickoff(inputs=dict(inputs))

        finally:
            # Detach the context when done
            detach(token)

    # Run the task in a dedicated thread
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, executor_task)
