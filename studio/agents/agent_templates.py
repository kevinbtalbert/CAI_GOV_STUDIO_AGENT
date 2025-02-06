from typing import List
from uuid import uuid4
from google.protobuf.json_format import MessageToDict

from cmlapi import CMLServiceApi

from studio.db.dao import AgentStudioDao
from studio.api import *
from studio.db import model as db_model
from studio.proto.utils import is_field_set


def list_agent_templates(
    request: ListAgentTemplatesRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> ListAgentTemplatesResponse:
    with dao.get_session() as session:
        agent_templates: List[db_model.AgentTemplate] = session.query(db_model.AgentTemplate).all()

        # Filter by specific agent template
        if is_field_set(request, "workflow_template_id"):
            agent_templates = list(
                filter(lambda x: x.workflow_template_id == request.workflow_template_id, agent_templates)
            )

        return ListAgentTemplatesResponse(
            agent_templates=[agent_template.to_protobuf() for agent_template in agent_templates]
        )


def get_agent_template(
    request: GetAgentTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> GetAgentTemplateResponse:
    with dao.get_session() as session:
        agent_template: db_model.AgentTemplate = (
            session.query(db_model.AgentTemplate).filter_by(id=request.id).one_or_none()
        )
        return GetAgentTemplateResponse(agent_template=agent_template.to_protobuf())


def add_agent_template(
    request: AddAgentTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> AddAgentTemplateResponse:
    with dao.get_session() as session:
        agent_template_dict = {"id": str(uuid4())}
        agent_template_dict.update(MessageToDict(request, preserving_proto_field_name=True))
        agent_template: db_model.AgentTemplate = db_model.AgentTemplate.from_dict(agent_template_dict)
        session.add(agent_template)
        return AddAgentTemplateResponse(id=agent_template.id)


def update_agent_template(
    request: UpdateAgentTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> UpdateAgentTemplateResponse:
    with dao.get_session() as session:
        agent_template: db_model.AgentTemplate = (
            session.query(db_model.AgentTemplate).filter_by(id=request.agent_template_id).one_or_none()
        )
        if not agent_template:
            raise ValueError(f"Agent template with id {request.id} not found")
        if agent_template.pre_packaged:
            raise ValueError("Cannot update pre-packaged agent templates")

        agent_template_dict = MessageToDict(
            request, preserving_proto_field_name=True, always_print_fields_with_no_presence=True
        )
        agent_template_dict.pop("agent_template_id", None)
        for key, value in agent_template_dict.items():
            if hasattr(agent_template, key) and value is not None:
                setattr(agent_template, key, value)

        session.commit()
        return UpdateAgentTemplateResponse(id=agent_template.id)


def remove_agent_template(
    request: RemoveAgentTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> RemoveAgentTemplateResponse:
    with dao.get_session() as session:
        agent_template: db_model.AgentTemplate = (
            session.query(db_model.AgentTemplate).filter_by(id=request.id).one_or_none()
        )
        if not agent_template:
            raise ValueError(f"Agent template with id {request.id} not found")
        if agent_template.pre_packaged:
            raise ValueError("Cannot remove pre-packaged agent templates")
        session.delete(agent_template)
        return RemoveAgentTemplateResponse()
