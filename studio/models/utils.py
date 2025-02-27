# No top level studio.db imports allowed to support wokrflow model deployment

from typing import Tuple, Annotated, Union
from pydantic import Field
from crewai import LLM as CrewAILLM
from studio import consts
from studio.cross_cutting.input_types import Input__LanguageModel


def get_crewai_llm_object_direct(language_model: Input__LanguageModel) -> CrewAILLM:
    model_config = language_model.config
    if not model_config:
        raise ValueError("Model config is required for direct LLM creation.")
    if model_config.model_type == "OPENAI":
        return CrewAILLM(
            model="openai/" + model_config.provider_model,
            api_key=model_config.api_key,
            temperature=language_model.generation_config.get("temperature"),
            max_completion_tokens=language_model.generation_config.get("max_new_tokens"),
            seed=0,
        )
    elif model_config.model_type == "OPENAI_COMPATIBLE":
        return CrewAILLM(
            model="openai/" + model_config.provider_model,
            api_key=model_config.api_key,
            base_url=model_config.api_base,
            temperature=language_model.generation_config.get("temperature"),
            max_completion_tokens=language_model.generation_config.get("max_new_tokens"),
            seed=0,
        )
    elif model_config.model_type == "AZURE_OPENAI":
        return CrewAILLM(
            model="azure/" + model_config.provider_model,
            api_key=model_config.api_key,
            base_url=model_config.api_base,
            temperature=language_model.generation_config.get("temperature"),
            max_completion_tokens=language_model.generation_config.get("max_new_tokens"),
            seed=0,
        )
    else:
        raise ValueError(f"Model type {model_config.model_type} is not supported.")


def get_crewai_llm_object_proxied(language_model: Input__LanguageModel, preexisting_db_session=None) -> CrewAILLM:
    from studio.db import DbSession, model as db_model

    session: DbSession = preexisting_db_session
    model = session.query(db_model.Model).filter_by(model_id=language_model.model_id).one_or_none()
    if not model:
        raise ValueError(f"Model with ID '{language_model.model_id}' not found.")
    return CrewAILLM(
        model=f"litellm_proxy/{model.model_name}",
        base_url=f"http://0.0.0.0:{consts.DEFAULT_LITELLM_SERVER_PORT}/v1",
        api_key="dummy-api-key",
        temperature=language_model.generation_config.get("temperature"),
        max_completion_tokens=language_model.generation_config.get("max_new_tokens"),
        seed=0,
    )


def get_studio_default_model_id(
    dao=None,
    preexisting_db_session=None,
) -> Tuple[
    Annotated[bool, Field(description="Is default set")], Union[Annotated[str, Field(description="Model ID")], None]
]:
    """
    Get the default model ID for the studio.
    """

    from studio.db import DbSession, model as db_model

    session: DbSession = preexisting_db_session or dao.get_session()
    model = session.query(db_model.Model).filter_by(is_studio_default=True).one_or_none()
    if not model:
        if not preexisting_db_session:
            session.close()
        return False, None

    if not preexisting_db_session:
        session.close()
    return True, model.model_id
