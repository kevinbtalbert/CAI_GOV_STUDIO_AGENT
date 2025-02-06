import pytest
from unittest.mock import patch, MagicMock
from studio.db.dao import AgentStudioDao
from studio.db import model as db_model
from studio.api import *
from studio.models.models import *

# Mock requests for test_model

def test_refresh_litellm_models():
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.Model(
            model_id="m1",
            model_name="model1",
            provider_model="provider1",
            model_type="type1",
            api_base="http://api.base1",
            api_key="api_key1"
        ))
        session.add(db_model.Model(
            model_id="m2",
            model_name="model2",
            provider_model="provider2",
            model_type="type2",
            api_base="http://api.base2",
            api_key="api_key2"
        ))
        session.commit()

    with patch("studio.models.litellm_proxy_utils.refresh_models_to_config") as refresh_mock, \
         patch("studio.models.litellm_proxy_utils.restart_litellm_server") as restart_mock:
        refresh_litellm_models(test_dao)
        refresh_mock.assert_called_once()
        restart_mock.assert_called_once()


@patch("studio.models.litellm_proxy_utils.refresh_models_to_config")
@patch("studio.models.litellm_proxy_utils.restart_litellm_server")
def test_list_models(mock_restart, mock_refresh):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.Model(
            model_id="m1",
            model_name="model1",
            provider_model="provider1",
            model_type="type1",
            api_base="http://api.base1",
            api_key="api_key1"
        ))
        session.add(db_model.Model(
            model_id="m2",
            model_name="model2",
            provider_model="provider2",
            model_type="type2",
            api_base="http://api.base2",
            api_key="api_key2"
        ))
        session.commit()

    req = ListModelsRequest()
    res = list_models(req, dao=test_dao)
    assert len(res.model_details) == 2
    assert res.model_details[0].model_name == "model1"
    mock_refresh.assert_not_called()
    mock_restart.assert_not_called()


@patch("studio.models.litellm_proxy_utils.refresh_models_to_config")
@patch("studio.models.litellm_proxy_utils.restart_litellm_server")
def test_add_model(mock_restart, mock_refresh):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    req = AddModelRequest(
        model_name="new_model",
        provider_model="provider1",
        model_type="type1",
        api_base="http://api.base",
        api_key="api_key"
    )

    res = add_model(req, dao=test_dao)
    assert res.model_id is not None

    with test_dao.get_session() as session:
        model = session.query(db_model.Model).filter_by(model_name="new_model").one_or_none()
        assert model is not None
        assert model.provider_model == "provider1"

    mock_refresh.assert_called_once()
    mock_restart.assert_called_once()


@patch("studio.models.litellm_proxy_utils.refresh_models_to_config")
@patch("studio.models.litellm_proxy_utils.restart_litellm_server")
def test_remove_model(mock_restart, mock_refresh):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.Model(
            model_id="m1",
            model_name="model1",
            provider_model="provider1",
            model_type="type1",
            api_base="http://api.base1",
            api_key="api_key1"
        ))
        session.commit()

    req = RemoveModelRequest(model_id="m1")
    remove_model(req, dao=test_dao)

    with test_dao.get_session() as session:
        model = session.query(db_model.Model).filter_by(model_id="m1").one_or_none()
        assert model is None

    mock_refresh.assert_called_once()
    mock_restart.assert_called_once()


@patch("studio.models.litellm_proxy_utils.refresh_models_to_config")
@patch("studio.models.litellm_proxy_utils.restart_litellm_server")
def test_update_model(mock_restart, mock_refresh):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.Model(
            model_id="m1",
            model_name="old_model",
            provider_model="provider1",
            model_type="type1",
            api_base="http://api.base1",
            api_key="old_key"
        ))
        session.commit()

    req = UpdateModelRequest(
        model_id="m1",
        model_name="new_model",
        api_key="new_key"
    )

    res = update_model(req, dao=test_dao)
    assert res.model_id == "m1"

    with test_dao.get_session() as session:
        model = session.query(db_model.Model).filter_by(model_id="m1").one_or_none()
        assert model.model_name == "new_model"
        assert model.api_key == "new_key"

    mock_refresh.assert_called_once()
    mock_restart.assert_called_once()


@patch("studio.models.litellm_proxy_utils.refresh_models_to_config")
@patch("studio.models.litellm_proxy_utils.restart_litellm_server")
def test_get_model_happy(mock_restart, mock_refresh):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.Model(
            model_id="m1",
            model_name="model1",
            provider_model="provider1",
            model_type="type1",
            api_base="http://api.base1",
            api_key="api_key1"
        ))
        session.commit()

    req = GetModelRequest(model_id="m1")
    res = get_model(req, dao=test_dao)
    assert res.model_details.model_name == "model1"

    mock_refresh.assert_not_called()
    mock_restart.assert_not_called()


@patch("studio.models.litellm_proxy_utils.refresh_models_to_config")
@patch("studio.models.litellm_proxy_utils.restart_litellm_server")
def test_get_model_not_found(mock_restart, mock_refresh):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    req = GetModelRequest(model_id="nonexistent")
    with pytest.raises(ValueError) as excinfo:
        get_model(req, dao=test_dao)
    assert "Model with ID 'nonexistent' not found" in str(excinfo.value)

    mock_refresh.assert_not_called()
    mock_restart.assert_not_called()

@patch("requests.post")
def test_test_model_happy(mock_post):
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {
        "choices": [{"message": {"content": "Test successful"}}]
    })

    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)
    with test_dao.get_session() as session:
        session.add(db_model.Model(
            model_id="m1",
            model_name="model1",
            provider_model="provider1",
            model_type="type1",
            api_base="http://api.base1",
            api_key="api_key"
        ))
        session.commit()

    req = TestModelRequest(
        model_id="m1",
        completion_role="user",
        completion_content="Test content"
    )

    res = model_test(req, dao=test_dao)
    assert res.response == "Test successful"


@patch("requests.post")
def test_test_model_failure(mock_post):
    mock_post.return_value = MagicMock(status_code=500, text="Server error")

    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)
    with test_dao.get_session() as session:
        session.add(db_model.Model(
            model_id="m1",
            model_name="model1",
            provider_model="provider1",
            model_type="type1",
            api_base="http://api.base1",
            api_key="api_key"
        ))
        session.commit()

    req = TestModelRequest(
        model_id="m1",
        completion_role="user",
        completion_content="Test content"
    )

    res = model_test(req, dao=test_dao)
    assert "Model Test Failed with status code 500" in res.response
