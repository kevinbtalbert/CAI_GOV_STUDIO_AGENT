import sys

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

from engine.utils import get_appliction_by_name
from engine.consts import AGENT_STUDIO_OPS_APPLICATION_NAME
from cmlapi import Application
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from phoenix.otel import register
import cmlapi
import os

# Monkey-patch the _wrappers module
import openinference.instrumentation.crewai as crewaiinst
import engine.tracing as tracing

crewaiinst._ToolUseWrapper = tracing._ToolUseWrapper
crewaiinst._ExecuteCoreWrapper = tracing._ExecuteCoreWrapper
crewaiinst._KickoffWrapper = tracing._KickoffWrapper


def get_ops_provider() -> str:
    return os.getenv("AGENT_STUDIO_OPS_PROVIDER", "phoenix")


def get_ops_endpoint() -> str:
    """
    Get the current operational endpoint of the
    Agent observability server. This can be overridden
    by an endpoint specified in an environment variable. If this
    env variable does not exist, extract the endpoint information
    from the running ops application directly. This env var override
    option is to make sure CML models can also reach the ops endpoint.
    """
    if os.getenv("AGENT_STUDIO_OPS_ENDPOINT"):
        return os.getenv("AGENT_STUDIO_OPS_ENDPOINT")

    cml = cmlapi.default_client()
    application: Application = get_appliction_by_name(cml, AGENT_STUDIO_OPS_APPLICATION_NAME)
    return f"https://{application.subdomain}.{os.getenv('CDSW_DOMAIN')}"


def get_phoenix_ops_tracer_provider(workflow_name: str):
    """
    Register a tracing provider to route to the phoenix
    observability endpoint. This will ensure the crew and the
    corresponding agents/tasks will report to phoenix.

    https://docs.arize.com/phoenix/tracing/integrations-tracing/crewai
    """

    ops_addr = get_ops_endpoint()

    tracer_provider = register(
        project_name=workflow_name,
        endpoint=f"{ops_addr}/v1/traces",
        headers={"Authorization": f"Bearer {os.getenv('CDSW_APIV2_KEY')}"},
    )
    return tracer_provider


def instrument_workflow(workflow_name: str):
    """
    Instrument agents, crews and tasks within a given model to report
    to the observability platform.
    """
    tracer_provider = get_phoenix_ops_tracer_provider(workflow_name)
    crewaiinst.CrewAIInstrumentor().instrument(tracer_provider=tracer_provider)
    LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)
    return tracer_provider


def reset_instrumentation():
    # Add logic to un-instrument or reset the instrumentors
    crewaiinst.CrewAIInstrumentor().uninstrument()  # Check if this method exists
    LiteLLMInstrumentor().uninstrument()  # Check if this method exists
