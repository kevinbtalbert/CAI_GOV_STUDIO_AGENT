from typing import List
from uuid import uuid4
from google.protobuf.json_format import MessageToDict

from cmlapi import CMLServiceApi

from studio.db.dao import AgentStudioDao
from studio.api import *
from studio.db import model as db_model, DbSession
from studio.proto.utils import is_field_set


def list_task_templates(
    request: ListTaskTemplatesRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> ListTaskTemplatesResponse:
    with dao.get_session() as session:
        task_templates: List[db_model.TaskTemplate] = session.query(db_model.TaskTemplate).all()

        # Filter by workflow template
        if is_field_set(request, "workflow_template_id"):
            task_templates = list(
                filter(lambda x: x.workflow_template_id == request.workflow_template_id, task_templates)
            )

        return ListTaskTemplatesResponse(
            task_templates=[task_template.to_protobuf() for task_template in task_templates]
        )


def get_task_template(
    request: GetTaskTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> GetTaskTemplateResponse:
    with dao.get_session() as session:
        task_template: db_model.TaskTemplate = (
            session.query(db_model.TaskTemplate).filter_by(id=request.id).one_or_none()
        )
        return GetTaskTemplateResponse(task_template=task_template.to_protobuf())


def add_task_template(
    request: AddTaskTemplateRequest,
    cml: CMLServiceApi = None,
    dao: AgentStudioDao = None,
    preexisting_db_session: DbSession = None,
) -> AddTaskTemplateResponse:
    try:
        if dao is not None:
            with dao.get_session() as session:
                return _add_task_template_impl(request, session)
        else:
            session = preexisting_db_session
            return _add_task_template_impl(request, session)
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")


def _add_task_template_impl(request: AddTaskTemplateRequest, session: DbSession = None) -> AddTaskTemplateResponse:
    task_template_dict = {"id": str(uuid4())}
    task_template_dict.update(MessageToDict(request, preserving_proto_field_name=True))
    task_template: db_model.TaskTemplate = db_model.TaskTemplate.from_dict(task_template_dict)
    session.add(task_template)
    return AddTaskTemplateResponse(id=task_template.id)


def remove_task_template(
    request: RemoveTaskTemplateRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> RemoveTaskTemplateResponse:
    with dao.get_session() as session:
        task_template: db_model.TaskTemplate = (
            session.query(db_model.TaskTemplate).filter_by(id=request.id).one_or_none()
        )
        session.delete(task_template)
        return RemoveTaskTemplateResponse()
