from uuid import uuid4
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from studio.db.dao import AgentStudioDao
from studio.db import model as db_model
from studio.api import *
from studio.tools.tool_instance import get_tool_instance
from studio.tools.tool_template import get_tool_template
from cmlapi import CMLServiceApi
from studio.workflow.utils import invalidate_workflow
from studio.proto.utils import is_field_set
from studio.tools.tool_instance import create_tool_instance, remove_tool_instance


def list_agents(
    request: ListAgentsRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> ListAgentsResponse:
    """
    List all agents with metadata.
    """
    try:
        with dao.get_session() as session:
            agents: List[db_model.Agent] = session.query(db_model.Agent).all()
            if not agents:
                return ListAgentsResponse(agents=[])

            # Filter by workflow id
            if is_field_set(request, "workflow_id"):
                agents = list(filter(lambda x: x.workflow_id == request.workflow_id, agents))

            agent_list = []
            for agent in agents:
                # Check if llm_provider_model_id exists in models table
                is_valid = (
                    session.query(db_model.Model).filter_by(model_id=agent.llm_provider_model_id).one_or_none()
                    is not None
                )

                # Validate tools associated with the agent
                tools_valid = True
                for tool_id in agent.tool_ids or []:
                    try:
                        tool_request = GetToolInstanceRequest(tool_instance_id=tool_id)
                        tool_response = get_tool_instance(tool_request, cml, dao=None, preexisting_db_session=session)
                        tool_template_id = tool_response.tool_instance.tool_template_id
                        tool_template = get_tool_template(
                            GetToolTemplateRequest(tool_template_id=tool_template_id), cml, dao
                        ).template
                        if not tool_template.is_valid:
                            tools_valid = False
                            break
                    except Exception:
                        tools_valid = False
                        break

                is_valid = is_valid and tools_valid

                agent_list.append(
                    AgentMetadata(
                        id=agent.id,
                        workflow_id=agent.workflow_id,
                        name=agent.name,
                        llm_provider_model_id=agent.llm_provider_model_id,
                        tools_id=agent.tool_ids or [],
                        crew_ai_agent_metadata=CrewAIAgentMetadata(
                            role=agent.crew_ai_role,
                            backstory=agent.crew_ai_backstory,
                            goal=agent.crew_ai_goal,
                            allow_delegation=agent.crew_ai_allow_delegation,
                            verbose=agent.crew_ai_verbose,
                            cache=agent.crew_ai_cache,
                            temperature=agent.crew_ai_temperature,
                            max_iter=agent.crew_ai_max_iter,
                        ),
                        is_valid=is_valid,
                    )
                )

            return ListAgentsResponse(agents=agent_list)
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to list agents: {str(e)}")


def get_agent(request: GetAgentRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None) -> GetAgentResponse:
    """
    Get details of a specific agent by its ID.
    """
    try:
        if not request.agent_id:
            raise ValueError("Agent ID is required.")

        with dao.get_session() as session:
            agent = session.query(db_model.Agent).filter_by(id=request.agent_id).one_or_none()
            if not agent:
                raise ValueError(f"Agent with ID '{request.agent_id}' not found.")

            # Check if llm_provider_model_id exists in models table
            is_valid = (
                session.query(db_model.Model).filter_by(model_id=agent.llm_provider_model_id).one_or_none() is not None
            )

            # Validate tools associated with the agent
            tools_valid = True
            for tool_id in agent.tool_ids or []:
                try:
                    tool_request = GetToolInstanceRequest(tool_instance_id=tool_id)
                    tool_response = get_tool_instance(tool_request, cml, dao=None, preexisting_db_session=session)
                    tool_template_id = tool_response.tool_instance.tool_template_id
                    tool_template = get_tool_template(
                        GetToolTemplateRequest(tool_template_id=tool_template_id), cml, dao
                    ).template
                    if not tool_template.is_valid:
                        tools_valid = False
                        break
                except Exception:
                    tools_valid = False
                    break

            is_valid = is_valid and tools_valid

            agent_metadata = AgentMetadata(
                id=agent.id,
                workflow_id=agent.workflow_id,
                name=agent.name,
                llm_provider_model_id=agent.llm_provider_model_id,
                tools_id=agent.tool_ids or [],
                crew_ai_agent_metadata=CrewAIAgentMetadata(
                    role=agent.crew_ai_role,
                    backstory=agent.crew_ai_backstory,
                    goal=agent.crew_ai_goal,
                    allow_delegation=agent.crew_ai_allow_delegation,
                    verbose=agent.crew_ai_verbose,
                    cache=agent.crew_ai_cache,
                    temperature=agent.crew_ai_temperature,
                    max_iter=agent.crew_ai_max_iter,
                ),
                is_valid=is_valid,
            )
            return GetAgentResponse(agent=agent_metadata)
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to get agent: {str(e)}")


def add_agent(request: AddAgentRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None) -> AddAgentResponse:
    """
    Add a new agent based on the request parameters.
    """
    try:
        if not request.name:
            raise ValueError("Agent name is required.")

        with dao.get_session() as session:
            # Fetch default LLM model if llm_provider_model_id is not provided or is empty
            llm_provider_model_id = request.llm_provider_model_id

            # Validate if llm_provider_model_id exists
            if llm_provider_model_id:
                if not session.query(db_model.Model).filter_by(model_id=llm_provider_model_id).one_or_none():
                    raise ValueError(f"Model with ID '{llm_provider_model_id}' does not exist.")

            tool_instance_ids = []
            # If we have tool templates, create tool instances from these templates
            if request.tool_template_ids:
                for tool_template_id in list(request.tool_template_ids):
                    tool_template: db_model.ToolTemplate = (
                        session.query(db_model.ToolTemplate).filter_by(id=tool_template_id).one()
                    )
                    response: CreateToolInstanceResponse = create_tool_instance(
                        CreateToolInstanceRequest(
                            workflow_id=request.workflow_id, name=tool_template.name, tool_template_id=tool_template_id
                        ),
                        cml=cml,
                        dao=None,
                        preexisting_db_session=session,
                    )
                    tool_instance_ids.append(response.tool_instance_id)
            # If we have tool instance IDs, validate them
            elif request.tools_id:
                tools_ids = list(request.tools_id)
                for tool_id in tools_ids:
                    try:
                        tool_request = GetToolInstanceRequest(tool_instance_id=tool_id)
                        tool_response = get_tool_instance(tool_request, cml, dao=None, preexisting_db_session=session)
                        # TODO : Check if Tool Instance is valid
                        tool_instance_ids.append(tool_id)
                    except Exception as e:
                        raise ValueError(f"Validation failed for tool ID '{tool_id}': {str(e)}")

            # Create a new agent
            agent = db_model.Agent(
                id=str(uuid4()),
                workflow_id=request.workflow_id,
                name=request.name,
                llm_provider_model_id=llm_provider_model_id,
                tool_ids=tool_instance_ids,
                crew_ai_role=request.crew_ai_agent_metadata.role,
                crew_ai_backstory=request.crew_ai_agent_metadata.backstory,
                crew_ai_goal=request.crew_ai_agent_metadata.goal,
                crew_ai_allow_delegation=request.crew_ai_agent_metadata.allow_delegation,
                crew_ai_verbose=request.crew_ai_agent_metadata.verbose,
                crew_ai_cache=request.crew_ai_agent_metadata.cache,
                crew_ai_temperature=request.crew_ai_agent_metadata.temperature,
                crew_ai_max_iter=request.crew_ai_agent_metadata.max_iter,
            )
            session.add(agent)
            session.commit()

            return AddAgentResponse(agent_id=agent.id)
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to add agent: {str(e)}")


def update_agent(
    request: UpdateAgentRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> UpdateAgentResponse:
    """
    Update the configuration of an existing agent.
    """
    try:
        if not request.agent_id:
            raise ValueError("Agent ID is required.")

        with dao.get_session() as session:
            agent = session.query(db_model.Agent).filter_by(id=request.agent_id).one_or_none()
            if not agent:
                raise ValueError(f"Agent with ID '{request.agent_id}' not found.")

            # Validate if llm_provider_model_id exists
            if request.llm_provider_model_id:
                if not session.query(db_model.Model).filter_by(model_id=request.llm_provider_model_id).one_or_none():
                    raise ValueError(f"Model with ID '{request.llm_provider_model_id}' does not exist.")
                agent.llm_provider_model_id = request.llm_provider_model_id

            # Handle tool updates
            if is_field_set(request, "tool_template_ids") and request.tool_template_ids:
                # Remove existing tool instances
                for existing_tool_instance_id in list(agent.tool_ids):
                    remove_tool_instance(
                        RemoveToolInstanceRequest(tool_instance_id=existing_tool_instance_id),
                        cml=cml,
                        dao=None,
                        preexisting_db_session=session,
                    )
                # Create new tool instances from templates
                tool_instance_ids = []
                for tool_template_id in list(request.tool_template_ids):
                    tool_template: db_model.ToolTemplate = (
                        session.query(db_model.ToolTemplate).filter_by(id=tool_template_id).one()
                    )
                    response: CreateToolInstanceResponse = create_tool_instance(
                        CreateToolInstanceRequest(
                            workflow_id=agent.workflow_id, name=tool_template.name, tool_template_id=tool_template_id
                        ),
                        cml=cml,
                        dao=None,
                        preexisting_db_session=session,
                    )
                    tool_instance_ids.append(response.tool_instance_id)
                agent.tool_ids = tool_instance_ids
            # Handle tool instance updates
            elif request.tools_id is not None:  # Handle empty lists explicitly
                tools_ids = list(request.tools_id)
                validated_tool_ids = []
                for tool_id in tools_ids:
                    try:
                        tool_request = GetToolInstanceRequest(tool_instance_id=tool_id)
                        tool_response = get_tool_instance(tool_request, cml, dao=None, preexisting_db_session=session)
                        # TODO : Check if Tool Instance is valid
                        validated_tool_ids.append(tool_id)
                    except Exception as e:
                        raise ValueError(f"Validation failed for tool ID '{tool_id}': {str(e)}")
                agent.tool_ids = validated_tool_ids

            # Update other fields only if provided in the request
            if request.name:
                agent.name = request.name
            if request.crew_ai_agent_metadata:
                metadata = request.crew_ai_agent_metadata
                if metadata.role:
                    agent.crew_ai_role = metadata.role
                if metadata.backstory:
                    agent.crew_ai_backstory = metadata.backstory
                if metadata.goal:
                    agent.crew_ai_goal = metadata.goal
                if metadata.allow_delegation is not None:
                    agent.crew_ai_allow_delegation = metadata.allow_delegation
                if metadata.verbose is not None:
                    agent.crew_ai_verbose = metadata.verbose
                if metadata.cache is not None:
                    agent.crew_ai_cache = metadata.cache
                if metadata.temperature is not None:
                    agent.crew_ai_temperature = metadata.temperature
                if metadata.max_iter is not None:
                    agent.crew_ai_max_iter = metadata.max_iter

            invalidate_workflow(dao, db_model.Workflow.crew_ai_agents.contains([agent.id]))

            session.commit()

        return UpdateAgentResponse()
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to update agent: {str(e)}")


def remove_agent(
    request: RemoveAgentRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> RemoveAgentResponse:
    """
    Remove an existing agent by its ID.
    """
    try:
        if not request.agent_id:
            raise ValueError("Agent ID is required.")

        with dao.get_session() as session:
            agent = session.query(db_model.Agent).filter_by(id=request.agent_id).one_or_none()
            if not agent:
                raise ValueError(f"Agent with ID '{request.agent_id}' not found.")

            invalidate_workflow(dao, db_model.Workflow.crew_ai_agents.contains([agent.id]))

            # Try to remove tool instances but continue even if they fail
            for tool_instance_id in agent.tool_ids:
                try:
                    remove_tool_instance(
                        RemoveToolInstanceRequest(tool_instance_id=tool_instance_id),
                        cml,
                        dao=None,
                        preexisting_db_session=session,
                    )
                except Exception as e:
                    # Log the error but continue with agent deletion
                    print(f"Failed to remove tool instance {tool_instance_id}: {str(e)}")
                    continue

            session.delete(agent)
            session.commit()

        return RemoveAgentResponse()
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to remove agent: {str(e)}")
