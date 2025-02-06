from typing import List
from uuid import uuid4
from google.protobuf.json_format import MessageToDict

from cmlapi import CMLServiceApi

from studio.db.dao import AgentStudioDao
from studio.api import *
from studio.db import model as db_model
from studio.agents.agent_templates import remove_agent_template
from studio.task.task_templates import remove_task_template, add_task_template
from studio.tools.tool_template import remove_tool_template
from studio.proto.utils import is_field_set
from crewai import Process
import studio.consts as consts
import os
import shutil


def list_workflow_templates(
    request: ListWorkflowTemplatesRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> ListWorkflowTemplatesResponse:
    with dao.get_session() as session:
        workflow_templates: List[db_model.WorkflowTemplate] = session.query(db_model.WorkflowTemplate).all()
        return ListWorkflowTemplatesResponse(
            workflow_templates=[workflow_template.to_protobuf() for workflow_template in workflow_templates]
        )


def get_workflow_template(
    request: GetWorkflowTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> GetWorkflowTemplateResponse:
    with dao.get_session() as session:
        workflow_template: db_model.WorkflowTemplate = (
            session.query(db_model.WorkflowTemplate).filter_by(id=request.id).one_or_none()
        )
        return GetWorkflowTemplateResponse(workflow_template=workflow_template.to_protobuf())


def add_workflow_template_from_workflow(
    workflow_id: str, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> AddWorkflowTemplateResponse:
    """
    Add a new workflow template explictly from an existing workflow.
    """

    workflow_template_id: str = str(uuid4())

    with dao.get_session() as session:
        # Get the actual workflow
        workflow: db_model.Workflow = session.query(db_model.Workflow).filter_by(id=workflow_id).one()

        # Create a baseline workflow template
        workflow_template: db_model.WorkflowTemplate = db_model.WorkflowTemplate(id=workflow_template_id)
        # TODO: might want to override name with the request in some way
        workflow_template.name = f"Template: {workflow.name}"
        workflow_template.description = workflow.description
        workflow_template.is_conversational = workflow.is_conversational
        workflow_template.process = workflow.crew_ai_process

        # If we have a default manager, mark a default manager in the workflow template.
        if workflow.crew_ai_process == Process.hierarchical and not workflow.crew_ai_manager_agent:
            workflow_template.use_default_manager = True

        # If we have a custom manager, add that manager as an agent template
        # and add it to the workflow template.
        # NOTE: manager agents do not have tools, so no need to check.
        if workflow.crew_ai_manager_agent and not workflow.crew_ai_llm_provider_model_id:
            agent: db_model.Agent = session.query(db_model.Agent).filter_by(id=workflow.crew_ai_manager_agent).one()
            agent_template_id = str(uuid4())
            agent_template: db_model.AgentTemplate = db_model.AgentTemplate(
                id=agent_template_id,
                allow_delegation=agent.crew_ai_allow_delegation,
                backstory=agent.crew_ai_backstory,
                cache=agent.crew_ai_cache,
                description=agent.name,  # TODO: add description to agent
                goal=agent.crew_ai_goal,
                max_iter=agent.crew_ai_max_iter,
                name=agent.name,
                pre_packaged=False,
                role=agent.crew_ai_role,
                temperature=agent.crew_ai_temperature,
                verbose=agent.crew_ai_verbose,
                workflow_template_id=workflow_template_id,
            )
            session.add(agent_template)
            workflow_template.manager_agent_template_id = agent_template_id
            workflow_template.use_default_manager = False

        # Add all of the tool instances as tool templates
        agent_template_ids = []
        agent_to_agent_template = {}
        for agent_id in list(workflow.crew_ai_agents):
            agent: db_model.Agent = session.query(db_model.Agent).filter_by(id=agent_id).one()
            agent_template_id = str(uuid4())
            agent_template: db_model.AgentTemplate = db_model.AgentTemplate(
                id=agent_template_id,
                allow_delegation=agent.crew_ai_allow_delegation,
                backstory=agent.crew_ai_backstory,
                cache=agent.crew_ai_cache,
                description=agent.name,  # TODO: add description to agent
                goal=agent.crew_ai_goal,
                max_iter=agent.crew_ai_max_iter,
                name=agent.name,
                pre_packaged=False,
                role=agent.crew_ai_role,
                temperature=agent.crew_ai_temperature,
                verbose=agent.crew_ai_verbose,
                workflow_template_id=workflow_template_id,
            )

            # Add tools
            tool_template_ids = []
            for tool_instance_id in list(agent.tool_ids):
                tool_instance: db_model.ToolInstance = (
                    session.query(db_model.ToolInstance).filter_by(id=tool_instance_id).one()
                )

                tool_template_id = str(uuid4())

                tool_template_dir = os.path.join(consts.TOOL_TEMPLATE_CATALOG_LOCATION, tool_template_id)
                os.makedirs(tool_template_dir, exist_ok=True)

                shutil.copy(
                    os.path.join(tool_instance.source_folder_path, tool_instance.python_code_file_name),
                    os.path.join(tool_template_dir, "tool.py"),
                )
                shutil.copy(
                    os.path.join(tool_instance.source_folder_path, tool_instance.python_requirements_file_name),
                    os.path.join(tool_template_dir, "requirements.txt"),
                )

                tool_image_path = ""
                if tool_instance.tool_image_path:
                    _, ext = os.path.splitext(tool_instance.tool_image_path)
                    os.makedirs(consts.TOOL_TEMPLATE_ICONS_LOCATION, exist_ok=True)
                    tool_image_path = os.path.join(consts.TOOL_TEMPLATE_ICONS_LOCATION, f"{tool_template_id}_icon{ext}")
                    shutil.copy(tool_instance.tool_image_path, tool_image_path)

                tool_template: db_model.ToolTemplate = db_model.ToolTemplate(
                    id=tool_template_id,
                    workflow_template_id=workflow_template_id,
                    name=tool_instance.name,
                    python_code_file_name="tool.py",
                    python_requirements_file_name="requirements.txt",
                    source_folder_path=tool_template_dir,
                    tool_image_path=tool_image_path,
                )

                tool_template_ids.append(tool_template_id)
                session.add(tool_template)

            # Add all new tool templates to the agent template
            agent_template.tool_template_ids = tool_template_ids

            # Append agent template id
            session.add(agent_template)
            agent_template_ids.append(agent_template.id)
            agent_to_agent_template[agent_id] = agent_template_id

        # Add agent template ids to the workflow
        workflow_template.agent_template_ids = agent_template_ids

        # Add all tasks as task templates that are owned by this workflow template
        task_template_ids = []
        for task_id in list(workflow.crew_ai_tasks):
            task: db_model.Task = session.query(db_model.Task).filter_by(id=task_id).one()
            response: AddTaskTemplateResponse = add_task_template(
                AddTaskTemplateRequest(
                    name=task.name,
                    description=task.description,
                    expected_output=task.expected_output,
                    assigned_agent_template_id=agent_to_agent_template.get(task.assigned_agent_id, None),
                    workflow_template_id=workflow_template_id,
                ),
                cml=cml,
                dao=None,
                preexisting_db_session=session,
            )
            task_template_ids.append(response.id)
        workflow_template.task_template_ids = task_template_ids

        workflow_template.pre_packaged = False  # Not shipped with the studio
        # Finally, add the workflow template
        session.add(workflow_template)
        return AddWorkflowTemplateResponse(id=workflow_template_id)


def add_workflow_template(
    request: AddWorkflowTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> AddWorkflowTemplateResponse:
    """
    Add a new workflow template.

    NOTE: this RPC call is explicitly designed for workflow templates that
    use GLOBAL task templates, tool templates, and agent templates that exist
    outside of the scope of a workflow template. When creating a workflow template
    from a previously existing workflow, containing pre-instantiated agents, tools
    and tasks, dedicated logic is provided where agent templates, tool templates and
    task templates are created and tied explicitly to this new workflow template.
    """

    # Create a workflow template from a pre-existing workflow.
    if is_field_set(request, "workflow_id"):
        workflow_id: str = request.workflow_id
        return add_workflow_template_from_workflow(workflow_id, cml, dao)

    with dao.get_session() as session:
        workflow_template_dict = {"id": str(uuid4())}
        workflow_template_dict.update(MessageToDict(request, preserving_proto_field_name=True))
        workflow_template_dict["pre_packaged"] = False  # Not shipped with the studio
        workflow_template: db_model.WorkflowTemplate = db_model.WorkflowTemplate.from_dict(workflow_template_dict)
        session.add(workflow_template)
        return AddWorkflowTemplateResponse(id=workflow_template.id)


def remove_workflow_template(
    request: RemoveWorkflowTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> RemoveWorkflowTemplateResponse:
    with dao.get_session() as session:
        workflow_template: db_model.WorkflowTemplate = (
            session.query(db_model.WorkflowTemplate).filter_by(id=request.id).one_or_none()
        )
        if not workflow_template:
            raise ValueError(f"Workflow template with ID '{request.id}' does not exist.")
        if workflow_template.pre_packaged:
            raise ValueError(f"Workflow template with ID '{request.id}' is pre-packaged and cannot be removed.")

        # Delete all agent templates, task templates and tool templates
        # explicitly tied to this workflow template. Note that global templates
        # will not be removed here if they are not explicitly tied to a workflow
        # template.
        agent_templates: list[db_model.AgentTemplate] = (
            session.query(db_model.AgentTemplate).filter_by(workflow_template_id=request.id).all()
        )
        for agent_template in agent_templates:
            remove_agent_template(RemoveAgentTemplateRequest(id=agent_template.id), cml, dao)
        task_templates: list[db_model.TaskTemplate] = (
            session.query(db_model.TaskTemplate).filter_by(workflow_template_id=request.id).all()
        )
        for task_template in task_templates:
            remove_task_template(RemoveTaskTemplateRequest(id=task_template.id), cml, dao)
        tool_templates: list[db_model.ToolTemplate] = (
            session.query(db_model.ToolTemplate).filter_by(workflow_template_id=request.id).all()
        )
        for tool_template in tool_templates:
            remove_tool_template(RemoveToolTemplateRequest(tool_template_id=tool_template.id), cml, dao)

        # Finally, remove the workflow template
        session.delete(workflow_template)
        return RemoveWorkflowTemplateResponse()
