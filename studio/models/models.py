from uuid import uuid4
from typing import List
from cmlapi import CMLServiceApi

from studio.db.dao import AgentStudioDao
from studio.db import model as db_model
import studio.models.litellm_proxy_utils as litellm_utils
from studio.api import *
import requests
import urllib
from studio import consts


def refresh_litellm_models(dao: AgentStudioDao = None):
    with dao.get_session() as session:
        all_models: List[db_model.Model] = session.query(db_model.Model).all()
        litellm_utils.refresh_models_to_config(all_models)
        litellm_utils.restart_litellm_server()


def list_models(
    request: ListModelsRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> ListModelsResponse:
    """
    List all models. Future extensions may include filtering based on request attributes.
    """
    with dao.get_session() as session:
        models: List[db_model.Model] = session.query(db_model.Model).all()
        return ListModelsResponse(model_details=[model.to_protobuf(Model) for model in models])


def get_model(request: GetModelRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None) -> GetModelResponse:
    """
    Get details of a specific model by its ID.
    """
    with dao.get_session() as session:
        model = session.query(db_model.Model).filter_by(model_id=request.model_id).one_or_none()
        if not model:
            raise ValueError(f"Model with ID '{request.model_id}' not found.")
        return GetModelResponse(model_details=model.to_protobuf(Model))


def add_model(request: AddModelRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None) -> AddModelResponse:
    """
    Add a new model based on the request parameters.
    If no models exist, set the added model as the default.
    """
    with dao.get_session() as session:
        # Validate if a model with the same name already exists
        if session.query(db_model.Model).filter_by(model_name=request.model_name).first():
            raise ValueError(f"Model with name '{request.model_name}' already exists.")

        # Check if there are existing models in the database
        existing_model_count = session.query(db_model.Model).count()

        # Create the new model
        m_ = db_model.Model(
            model_id=str(uuid4()),
            model_name=request.model_name,
            provider_model=request.provider_model,
            model_type=request.model_type,
            api_base=request.api_base,
            api_key=request.api_key,
            # Set as default if no models exist
            is_studio_default=(existing_model_count == 0),
        )
        session.add(m_)
        session.commit()
        model_id_generated = m_.model_id

    # Refresh litellm models cache
    refresh_litellm_models(dao)

    return AddModelResponse(model_id=model_id_generated)


def remove_model(
    request: RemoveModelRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> RemoveModelResponse:
    """
    Remove an existing model by its ID.
    """
    with dao.get_session() as session:
        m_ = session.query(db_model.Model).filter_by(model_id=request.model_id).one_or_none()
        if not m_:
            raise ValueError(f"Model with ID '{request.model_id}' not found.")
        session.delete(m_)
        session.commit()
    refresh_litellm_models(dao)
    return RemoveModelResponse()


def update_model(
    request: UpdateModelRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> UpdateModelResponse:
    """
    Update the configuration of an existing model.
    """
    with dao.get_session() as session:
        m_ = session.query(db_model.Model).filter_by(model_id=request.model_id).one_or_none()
        if not m_:
            raise ValueError(f"Model with ID '{request.model_id}' not found.")

        # Update fields only if provided in the request
        if request.model_name:
            m_.model_name = request.model_name
        if request.provider_model:
            m_.provider_model = request.provider_model
        if request.api_base:
            m_.api_base = request.api_base
        if request.api_key:
            m_.api_key = request.api_key
        model_id = m_.model_id
        session.commit()
    refresh_litellm_models(dao)
    return UpdateModelResponse(model_id=model_id)


def model_test(request: TestModelRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None) -> TestModelResponse:
    """
    Tests an existing model by sending a test request to the LiteLLM server.

    Args:
        request (TestModelRequest): The request containing the model ID, role, and test content.
        cml (CMLServiceApi): Optional. The CMLServiceApi instance.
        dao (AgentStudioDao): Optional. The AgentStudioDao instance for database interaction.

    Returns:
        TestModelResponse: The response containing the test result.
    """
    with dao.get_session() as session:
        # Retrieve the model using the model_id from the request
        model = session.query(db_model.Model).filter_by(model_id=request.model_id).one_or_none()
        if not model:
            raise ValueError(f"Model with ID '{request.model_id}' not found.")

        # Prepare the test payload
        completions_url = urllib.parse.urljoin(
            f"http://0.0.0.0:{consts.DEFAULT_LITELLM_SERVER_PORT}/v1", "chat/completions"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer dummy_api_key",
        }
        payload = {
            "model": model.model_name,
            "messages": [
                {
                    "role": request.completion_role,
                    "content": request.completion_content,
                }
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        # Send the request to the LiteLLM server and handle the response
        try:
            response = requests.post(completions_url, headers=headers, json=payload, timeout=2)
            if response.status_code == 200:
                completion = (
                    response.json().get("choices", [{}])[0].get("message", {}).get("content", "No content returned")
                )
                return TestModelResponse(response=completion)
            else:
                error_message = f"Model Test Failed with status code {response.status_code}: {response.text}"
                return TestModelResponse(response=error_message)
        except requests.exceptions.ConnectionError:
            return TestModelResponse(response="Model Test Failed: Unable to connect to the server")
        except requests.exceptions.ReadTimeout:
            return TestModelResponse(response="Model Test Failed: Request timed out")
        except requests.exceptions.RequestException as e:
            return TestModelResponse(response=f"Model Test Failed: {str(e)}")


def set_studio_default_model(
    request: SetStudioDefaultModelRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> SetStudioDefaultModelResponse:
    """
    Set a model as the default model for the Studio.
    """
    with dao.get_session() as session:
        # Reset the existing default model
        session.query(db_model.Model).filter_by(is_studio_default=True).update({"is_studio_default": False})
        # Set the new default model
        m_ = session.query(db_model.Model).filter_by(model_id=request.model_id).one_or_none()
        if not m_:
            raise ValueError(f"Model with ID '{request.model_id}' not found.")
        m_.is_studio_default = True
        session.commit()
    return SetStudioDefaultModelResponse()


def get_studio_default_model(
    request: GetStudioDefaultModelRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> GetStudioDefaultModelResponse:
    """
    Get the default model for the Studio.
    """
    with dao.get_session() as session:
        m_ = session.query(db_model.Model).filter_by(is_studio_default=True).one_or_none()
        if not m_:
            return GetStudioDefaultModelResponse(
                is_default_model_configured=False,
            )
        return GetStudioDefaultModelResponse(
            is_default_model_configured=True,
            model_details=m_.to_protobuf(Model),
        )
