from typing import List
from crewai import Agent as CrewAIAgent
from crewai.tools import tool, BaseTool

from studio.db import model as db_model, DbSession
import studio.tools.utils as tool_utils
import studio.models.utils as model_utils


def get_crewai_agent_instance(agent_id: str, preexisting_db_session: DbSession = None) -> CrewAIAgent:
    """
    Get a CrewAI agent instance from a database agent model.
    """
    session = preexisting_db_session

    agent_model = session.query(db_model.Agent).filter_by(id=agent_id).one_or_none()
    if not agent_model:
        raise ValueError(f"Agent with ID '{agent_id}' not found.")
    tool_instance_ids = agent_model.tool_ids or []
    crewai_tools: List[BaseTool] = list()
    for t_id in tool_instance_ids:
        tool_proxy_callable = tool_utils.get_tool_instance_proxy(
            t_id, dao=dao, preexisting_db_session=preexisting_db_session
        )
        crewai_tools.append(tool(tool_proxy_callable))
    crewai_llm = model_utils.get_crewai_llm_object(
        agent_model.llm_provider_model_id, dao=dao, preexisting_db_session=preexisting_db_session
    )
    agent = CrewAIAgent(
        role=agent_model.crew_ai_role,
        backstory=agent_model.crew_ai_backstory,
        goal=agent_model.crew_ai_goal,
        allow_delegation=agent_model.crew_ai_allow_delegation,
        verbose=agent_model.crew_ai_verbose,
        cache=agent_model.crew_ai_cache,
        max_iter=agent_model.crew_ai_max_iter,
        tools=crewai_tools or None,
        llm=crewai_llm,
    )

    return agent
