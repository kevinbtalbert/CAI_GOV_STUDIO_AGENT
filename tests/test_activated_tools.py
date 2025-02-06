import pytest 
from unittest.mock import patch, MagicMock
from studio.db import model as db_model
from studio.models.models import (
    ListActivatedToolsRequest,
    ListActivatedToolsResponse,
    GetToolTemplateResponse
)
from studio.tools.activated_tools import *

from unittest.mock import patch, MagicMock
from studio.models.models import (
    ListActivatedToolsRequest,
    ListActivatedToolsResponse,
    GetToolTemplateResponse,
    ToolTemplate,
)
from studio.db import model as db_model
from studio.models.models import (
    GetActivatedToolRequest,
    GetActivatedToolResponse,
    GetToolTemplateResponse,
    ToolTemplate,
)

@patch("studio.tools.tool_template.get_tool_template")
@patch("os.path.exists")
@patch("os.environ")
@patch("studio.db.dao.AgentStudioDao")
@patch("cmlapi.CMLServiceApi")
def test_list_activated_tools_success(mock_cml_api, mock_dao, mock_environ, mock_path_exists, mock_get_tool_template):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    mock_environ.__getitem__.side_effect = lambda key: "mock_project_id" if key == "CDSW_PROJECT_ID" else None

    # Mock database query to return activated tools
    mock_tool1 = db_model.ActivatedTool(
        id="tool1",
        name="Activated Tool 1",
        tool_template_id="template1",
        status="active",
        user_parameters='{"param1": "value1"}',
        source_folder_path="/path/to/tool1",
        python_code_model_file_path="model.py",
        signature_json_file_path="signature.json",
        cml_deployed_model_id="mock_model_id",
        cml_deployed_model_build_id="mock_build_id"
    )
    mock_tool2 = db_model.ActivatedTool(
        id="tool2",
        name="Activated Tool 2",
        tool_template_id="template2",
        status="deactivated",
        user_parameters=None,
        source_folder_path="/path/to/tool2",
        python_code_model_file_path="model.py",
        signature_json_file_path="signature.json",
        cml_deployed_model_id="mock_model_id_2",
        cml_deployed_model_build_id="mock_build_id_2"
    )
    test_session.query.return_value.all.return_value = [mock_tool1, mock_tool2]

    # Mock file existence checks
    mock_path_exists.side_effect = lambda path: True

    # Mock GetToolTemplateResponse with a valid ToolTemplate object
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(
            is_valid=True,
            tool_metadata=json.dumps({"user arguments": ["param1"]}),
        )
    )

    # Mock CML model deployment methods
    mock_cml = mock_cml_api.return_value

    # Mock list_model_deployments response
    mock_list_deployments_response = MagicMock()
    mock_list_deployments_response.model_deployments = [MagicMock(id="deployment1")]
    mock_cml.list_model_deployments.return_value = mock_list_deployments_response

    # Mock get_model_deployment response
    mock_get_deployment_response = MagicMock()
    mock_get_deployment_response.status = "deployed"
    mock_cml.get_model_deployment.return_value = mock_get_deployment_response

    # Create the request object
    req = ListActivatedToolsRequest()

    # Call the function
    res = list_activated_tools(req, cml=mock_cml, dao=test_dao)

    # Validate the response
    assert isinstance(res, ListActivatedToolsResponse)
    assert len(res.activated_tools) == 2

    tool1 = res.activated_tools[0]
    tool2 = res.activated_tools[1]

    # Validate tool 1 details
    assert tool1.id == "tool1"
    assert tool1.name == "Activated Tool 1"
    assert tool1.status == "deployed"  # Correctly mocked status
    assert tool1.is_valid

    # Validate tool 2 details
    assert tool2.id == "tool2"
    assert tool2.name == "Activated Tool 2"
    assert tool2.status == "deactivated"  # No deployment, status remains deactivated
    assert tool2.is_valid

@patch("studio.tools.tool_template.get_tool_template")
@patch("os.path.exists")
@patch("os.environ.get")
@patch("studio.db.dao.AgentStudioDao")
@patch("cmlapi.CMLServiceApi")
def test_list_activated_tools_no_tools(mock_cml_api, mock_dao, mock_env_get, mock_path_exists, mock_get_tool_template):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock environment variable
    mock_env_get.return_value = "mock_project_id"

    # Mock database query to return no activated tools
    test_session.query.return_value.all.return_value = []

    # Mock file existence checks
    mock_path_exists.side_effect = lambda path: True

    # Call the function
    req = ListActivatedToolsRequest()
    res = list_activated_tools(req, cml=MagicMock(), dao=test_dao)

    # Validate the response
    assert isinstance(res, ListActivatedToolsResponse)
    assert len(res.activated_tools) == 0

@patch("studio.tools.tool_template.get_tool_template")
@patch("os.path.exists")
@patch("os.environ.get")
@patch("studio.db.dao.AgentStudioDao")
@patch("cmlapi.CMLServiceApi")
def test_list_activated_tools_deployment_failure(mock_cml_api, mock_dao, mock_env_get, mock_path_exists, mock_get_tool_template):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock environment variable
    mock_env_get.return_value = "mock_project_id"

    # Mock database query to return activated tools
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Activated Tool 1",
        tool_template_id="template1",
        status="active",
        user_parameters='{"param1": "value1"}',
        source_folder_path="/path/to/tool1",
        python_code_model_file_path="model.py",
        signature_json_file_path="signature.json",
        cml_deployed_model_id="mock_model_id",
        cml_deployed_model_build_id="mock_build_id"
    )
    test_session.query.return_value.all.return_value = [mock_tool]

    # Mock file existence checks
    mock_path_exists.side_effect = lambda path: True

    # Mock GetToolTemplateResponse with a valid ToolTemplate object
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(
            is_valid=True,
            tool_metadata=json.dumps({"user arguments": ["param1"]}),
        )
    )

    # Mock CML model deployment methods
    mock_cml = mock_cml_api.return_value

    # Mock list_model_deployments to raise an exception
    mock_cml.list_model_deployments.side_effect = Exception("Deployment not found")

    # Call the function
    req = ListActivatedToolsRequest()
    res = list_activated_tools(req, cml=mock_cml, dao=test_dao)

    # Validate the response
    assert isinstance(res, ListActivatedToolsResponse)
    assert len(res.activated_tools) == 1

    tool = res.activated_tools[0]
    assert tool.id == "tool1"
    assert tool.status == "unknown"  # Deployment failure should result in unknown status

from unittest.mock import patch, MagicMock, mock_open
import json
from studio.models.models import GetActivatedToolRequest, GetActivatedToolResponse, GetToolTemplateResponse, ToolTemplate
from studio.db import model as db_model


@patch("studio.tools.tool_template.get_tool_template")
@patch("os.path.exists")
@patch("studio.db.dao.AgentStudioDao")
@patch("studio.cross_cutting.utils.get_cml_model_deployment_status")
@patch("studio.tools.activated_tools.open", new_callable=mock_open, read_data='{"signature": "test_signature"}')
def test_get_activated_tool_success(
    mock_open_func,
    mock_get_deployment_status,
    mock_dao,
    mock_path_exists,
    mock_get_tool_template,
):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return the activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Activated Tool 1",
        tool_template_id="template1",
        status="active",
        user_parameters='{"param1": "value1"}',
        source_folder_path="/path/to/tool1",
        python_code_model_file_path="model.py",
        signature_json_file_path="signature.json",
        cml_deployed_model_id="mock_model_id",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock file existence checks
    mock_path_exists.side_effect = lambda path: True

    # Mock tool template validation
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(
            is_valid=True,
            tool_metadata=json.dumps({"user arguments": ["param1"]}),
        )
    )

    # Mock deployment status
    mock_get_deployment_status.return_value = "deployed"

    # Mock request
    req = GetActivatedToolRequest(activated_tool_id="tool1")

    # Call the function
    res = get_activated_tool(req, cml=MagicMock(), dao=test_dao)

    # Validate response
    assert isinstance(res, GetActivatedToolResponse)
    tool = res.tool

    # Debugging outputs
    print(f"Tool status: {tool.status}")  # Debugging: Check tool status
    print(f"Deployment status mock: {mock_get_deployment_status.return_value}")  # Debugging: Verify mock return value
    print(f"Tool signature JSON: {tool.tool_signature_json}")  # Debugging: Check signature JSON

    # Validate attributes
    assert tool.id == "tool1"
    assert tool.name == "Activated Tool 1"
    assert tool.status == "deployed"
    assert tool.tool_signature_json == '{"signature": "test_signature"}'  # Validate mocked signature JSON
    assert tool.is_valid
    assert "param1" in tool.user_parameters

@patch("studio.db.dao.AgentStudioDao")
def test_get_activated_tool_not_found(mock_dao):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return None
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = None

    # Mock request
    req = GetActivatedToolRequest(activated_tool_id="non_existent_tool")

    # Call the function and validate exception
    try:
        get_activated_tool(req, cml=MagicMock(), dao=test_dao)
        assert False, "Expected RuntimeError for missing tool"
    except RuntimeError as e:
        assert str(e) == "Unexpected error while retrieving activated tool: Activated tool with ID 'non_existent_tool' not found."

@patch("studio.tools.tool_template.get_tool_template")
@patch("os.path.exists")
@patch("studio.db.dao.AgentStudioDao")
@patch("studio.tools.activated_tools.open", new_callable=mock_open, read_data='{"signature": "test_signature"}')
def test_get_activated_tool_invalid_template(mock_open_func, mock_dao, mock_path_exists, mock_get_tool_template):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return the activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Activated Tool 1",
        tool_template_id="template1",
        status="active",
        user_parameters='{"param1": "value1"}',
        source_folder_path="/path/to/tool1",
        python_code_model_file_path="model.py",
        signature_json_file_path="signature.json",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock file existence checks
    mock_path_exists.side_effect = lambda path: True

    # Mock tool template validation failure
    mock_get_tool_template.side_effect = Exception("Invalid template")

    # Mock request
    req = GetActivatedToolRequest(activated_tool_id="tool1")

    # Call the function
    res = get_activated_tool(req, cml=MagicMock(), dao=test_dao)

    # Validate response
    assert isinstance(res, GetActivatedToolResponse)
    tool = res.tool
    assert not tool.is_valid

@patch("studio.tools.tool_template.get_tool_template")
@patch("os.path.exists")
@patch("studio.db.dao.AgentStudioDao")
def test_get_activated_tool_missing_signature_file(mock_dao, mock_path_exists, mock_get_tool_template):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return the activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Activated Tool 1",
        tool_template_id="template1",
        status="active",
        user_parameters='{"param1": "value1"}',
        source_folder_path="/path/to/tool1",
        python_code_model_file_path="model.py",
        signature_json_file_path="missing_signature.json",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock file existence checks to fail for signature file
    def path_exists_mock(path):
        if "missing_signature.json" in path:
            return False
        return True

    mock_path_exists.side_effect = path_exists_mock

    # Mock tool template validation
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(is_valid=True)
    )

    # Mock request
    req = GetActivatedToolRequest(activated_tool_id="tool1")

    # Call the function
    res = get_activated_tool(req, cml=MagicMock(), dao=test_dao)

    # Validate response
    assert isinstance(res, GetActivatedToolResponse)
    tool = res.tool
    assert not tool.is_valid
    assert tool.tool_signature_json == ""

@patch("studio.tools.tool_template.get_tool_template")
@patch("os.path.exists")
@patch("studio.db.dao.AgentStudioDao")
@patch("studio.cross_cutting.utils.get_cml_model_deployment_status")
@patch("studio.tools.activated_tools.open", new_callable=mock_open, read_data='{"signature": "test_signature"}')
def test_get_activated_tool_deployment_status_error(
    mock_open_func,
    mock_get_deployment_status,
    mock_dao,
    mock_path_exists,
    mock_get_tool_template,
):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return the activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Activated Tool 1",
        tool_template_id="template1",
        status="active",
        user_parameters='{"param1": "value1"}',
        source_folder_path="/path/to/tool1",
        python_code_model_file_path="model.py",
        signature_json_file_path="signature.json",
        cml_deployed_model_id="mock_model_id",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock file existence checks
    mock_path_exists.side_effect = lambda path: True

    # Mock tool template validation
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(is_valid=True)
    )

    # Mock deployment status error
    mock_get_deployment_status.side_effect = Exception("Deployment status unavailable")

    # Mock request
    req = GetActivatedToolRequest(activated_tool_id="tool1")

    # Call the function
    res = get_activated_tool(req, cml=MagicMock(), dao=test_dao)

    # Validate response
    assert isinstance(res, GetActivatedToolResponse)
    tool = res.tool

    # Debugging outputs
    print(f"Tool status: {tool.status}")  # Debugging output
    print(f"Deployment status side effect: {mock_get_deployment_status.side_effect}")  # Verify exception

    # Validate tool attributes
    assert tool.id == "tool1"
    assert tool.name == "Activated Tool 1"
    assert tool.status == "unknown"  # Ensure the status is correctly set to "unknown"
    assert tool.is_valid
    assert "param1" in tool.user_parameters

@patch("studio.tools.tool_template.get_tool_template")
@patch("studio.db.dao.AgentStudioDao")
@patch("studio.tools.activated_tools.os.makedirs")
@patch("studio.tools.activated_tools.shutil.copy2")
@patch("studio.tools.activated_tools.generate_model_file_for_tool")
@patch("studio.tools.activated_tools.generate_signature_from_file")
@patch("studio.tools.activated_tools.cc_utils.deploy_cml_model")
@patch("studio.tools.activated_tools.open", new_callable=mock_open, read_data='{"signature": "test_signature"}')
@patch("os.path.exists")
def test_activate_tool_success(
    mock_exists,
    mock_open_func,
    mock_deploy_cml_model,
    mock_generate_signature,
    mock_generate_model_file,
    mock_copy2,
    mock_makedirs,
    mock_dao,
    mock_get_tool_template
):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database queries
    # No duplicate tool name exists
    test_session.query.return_value.filter_by.return_value.first.side_effect = [
        None,  # For checking existing tool name
        MagicMock(  # For fetching the tool template
            id="mock_template_id",
            source_folder_path="/mock/source",
            python_code_file_name="mock_code.py",
            python_requirements_file_name="mock_requirements.txt",
        )
    ]

    # Mock file existence
    mock_exists.side_effect = lambda path: True

    # Mock tool template validation
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(is_valid=True, tool_metadata=json.dumps({}))
    )

    # Mock CML deployment
    mock_deploy_cml_model.return_value = ("mock_model_id", "mock_build_id")

    # Mock request
    req = ActivateToolRequest(
        name="Test Tool",
        tool_template_id="mock_template_id",
        user_parameters={"param1": "value1"},
        resources=ToolResourceRequest(cpu=1, memory=2, replicas=1),  # Corrected memory to a real number
    )

    # Call the function
    res = activate_tool(req, cml=MagicMock(), dao=test_dao)

    # Validate response
    assert isinstance(res, ActivateToolResponse)
    assert res.activated_tool_id is not None

    # Validate that the CML model was deployed
    mock_deploy_cml_model.assert_called_once()

@patch("studio.tools.tool_template.get_tool_template")
@patch("studio.db.dao.AgentStudioDao")
def test_activate_tool_name_already_exists(mock_dao, mock_get_tool_template):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database queries
    test_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()  # Duplicate tool exists

    # Mock tool template validation
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(is_valid=True, tool_metadata=json.dumps({}))
    )

    # Mock request
    req = ActivateToolRequest(
        name="Test Tool",
        tool_template_id="mock_template_id",
        user_parameters={"param1": "value1"},
        resources=ToolResourceRequest(cpu=1, memory=2, replicas=1),
    )

    # Call the function and validate the exception
    with pytest.raises(ValueError, match="Tool with name 'Test Tool' already exists in the database"):
        activate_tool(req, cml=MagicMock(), dao=test_dao)

@patch("studio.tools.tool_template.get_tool_template")
@patch("studio.db.dao.AgentStudioDao")
def test_activate_tool_invalid_tool_template(mock_dao, mock_get_tool_template):
    # Mock tool template validation
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(is_valid=False, tool_metadata=json.dumps({"status": "Invalid template"}))
    )

    # Mock request
    req = ActivateToolRequest(
        name="Test Tool",
        tool_template_id="mock_template_id",
        user_parameters={"param1": "value1"},
        resources=ToolResourceRequest(cpu=1, memory=2, replicas=1),
    )

    # Call the function and validate the exception
    with pytest.raises(ValueError, match="Validation error: ToolTemplate with id mock_template_id is not valid. Validation error: Invalid template"):
        activate_tool(req, cml=MagicMock(), dao=MagicMock())

@patch("studio.tools.tool_template.get_tool_template")
@patch("studio.db.dao.AgentStudioDao")
def test_activate_tool_template_not_found(mock_dao, mock_get_tool_template):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database queries
    test_session.query.return_value.filter_by.return_value.first.side_effect = [
        None,  # No duplicate tool name
        None,  # Tool template not found
    ]

    # Mock tool template validation
    mock_get_tool_template.return_value = GetToolTemplateResponse(
        template=ToolTemplate(is_valid=True, tool_metadata=json.dumps({}))
    )

    # Mock request
    req = ActivateToolRequest(
        name="Test Tool",
        tool_template_id="mock_template_id",
        user_parameters={"param1": "value1"},
        resources=ToolResourceRequest(cpu=1, memory=2, replicas=1),
    )

    # Call the function and validate the exception
    with pytest.raises(ValueError, match="Validation error: ToolTemplate with id mock_template_id not found"):
        activate_tool(req, cml=MagicMock(), dao=test_dao)


@patch("studio.tools.tool_template.get_tool_template")
@patch("os.environ.get")
@patch("studio.db.dao.AgentStudioDao")
def test_activate_tool_invalid_name_format(mock_dao, mock_env_get, mock_get_tool_template):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock environment variable
    mock_env_get.side_effect = lambda key, default=None: (
        "mock_project_id" if key == "CDSW_PROJECT_ID" else "mock.cdsw.domain"
    )

    # Mock database queries
    test_session.query.return_value.filter_by.return_value.first.side_effect = [None, MagicMock()]

    # Mock tool template validation
    mock_get_tool_template.return_value = MagicMock(
        template=MagicMock(
            is_valid=True,
            tool_metadata=json.dumps({})
        )
    )

    # Mock request with an invalid name
    req = MagicMock()
    req.name = "Invalid/Name!"  # Invalid name containing special characters
    req.tool_template_id = "mock_template_id"
    req.user_parameters = {"param1": "value1"}
    req.resources = MagicMock(cpu=1, memory=2, replicas=1)

    # Call the function and validate the exception
    with pytest.raises(ValueError, match="Tool name must only contain alphabets, numbers, and spaces"):
        activate_tool(req, cml=MagicMock(), dao=test_dao)


@patch("studio.tools.activated_tools.requests.post")
@patch("os.environ")
@patch("studio.db.dao.AgentStudioDao")
def test_activated_tool_test_success(mock_dao, mock_environ, mock_requests_post):
    # Mock environment variables
    mock_environ.__getitem__.side_effect = lambda key: {
        "CDSW_PROJECT_ID": "mock_project_id",
        "CDSW_DOMAIN": "mock.cdsw.domain"
    }.get(key)
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Test Tool",
        cml_deployed_model_id="mock_model_id",
        cml_deployed_model_build_id="mock_build_id",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock CML service model details
    mock_model_details = MagicMock()
    mock_model_details.access_key = "mock_access_key"
    mock_cml = MagicMock()
    mock_cml.get_model.return_value = mock_model_details

    # Mock POST request to model service
    mock_requests_post.return_value = MagicMock(
        status_code=200, json=lambda: {"output": "test_output"}
    )

    # Create the request
    req = TestActivatedToolRequest(
        activated_tool_id="tool1",
        tool_payload=json.dumps({"input": "test_input"})
    )

    # Call the function
    res = activated_tool_test(req, cml=mock_cml, dao=test_dao)

    # Validate response
    assert isinstance(res, TestActivatedToolResponse)
    assert json.loads(res.tool_response) == {"output": "test_output"}

    # Validate POST request payload
    mock_requests_post.assert_called_once_with(
        "https://modelservice.mock.cdsw.domain/model",
        data=json.dumps({
            "accessKey": "mock_access_key",
            "request": {"input": "test_input"}
        }),
        headers={'Content-Type': 'application/json'}
    )

@patch("os.environ")
@patch("studio.db.dao.AgentStudioDao")
def test_activated_tool_test_invalid_payload(mock_dao, mock_environ):
    # Mock environment variables
    mock_environ.__getitem__.side_effect = lambda key: "mock_project_id" if key == "CDSW_PROJECT_ID" else None

    # Mock DAO and session
    test_dao = mock_dao.return_value

    # Create the request with invalid JSON
    req = TestActivatedToolRequest(
        activated_tool_id="tool1",
        tool_payload="invalid_json"
    )

    # Validate the exception
    with pytest.raises(ValueError, match="Invalid JSON in tool payload"):
        activated_tool_test(req, cml=MagicMock(), dao=test_dao)


@patch("studio.tools.activated_tools.requests.post")
@patch("os.environ")
@patch("studio.db.dao.AgentStudioDao")
def test_activated_tool_test_http_error(mock_dao, mock_environ, mock_requests_post):
    # Mock environment variables
    mock_environ.__getitem__.side_effect = lambda key: (
        "mock_project_id" if key == "CDSW_PROJECT_ID" else "mock.cdsw.domain"
    )

    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Test Tool",
        cml_deployed_model_id="mock_model_id",
        cml_deployed_model_build_id="mock_build_id",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock CML service model details
    mock_model_details = MagicMock()
    mock_model_details.access_key = "mock_access_key"
    mock_cml = MagicMock()
    mock_cml.get_model.return_value = mock_model_details

    # Mock POST request to return an HTTP error
    mock_requests_post.return_value = MagicMock(status_code=500, text="Internal Server Error")

    # Create the request
    req = TestActivatedToolRequest(
        activated_tool_id="tool1",
        tool_payload=json.dumps({"input": "test_input"})
    )

    # Validate the exception
    with pytest.raises(RuntimeError, match="Error testing tool: 500 - Internal Server Error"):
        activated_tool_test(req, cml=mock_cml, dao=test_dao)


@patch("studio.tools.activated_tools.os.getenv")
@patch("studio.tools.activated_tools.AgentStudioDao")
@patch("studio.tools.activated_tools.CMLServiceApi")
def test_deactivate_tool_success(mock_cml, mock_dao, mock_getenv):
    # Mock environment variables
    mock_getenv.side_effect = lambda key: "mock_project_id" if key == "CDSW_PROJECT_ID" else None

    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Test Tool",
        status="active",
        cml_deployed_model_id="mock_model_id",
        cml_deployed_model_build_id="mock_build_id",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock CML service list_model_deployments
    mock_cml.return_value.list_model_deployments.return_value = MagicMock(
        model_deployments=[MagicMock(id="deployment1")]
    )

    # Mock CML service stop_model_deployment
    mock_cml.return_value.stop_model_deployment.return_value = None

    # Create the request
    req = DeactivateToolRequest(activated_tool_id="tool1")

    # Call the function
    res = deactivate_tool(req, cml=mock_cml.return_value, dao=test_dao)

    # Validate the response
    assert isinstance(res, DeactivateToolResponse)

    # Ensure the tool's status was updated to "deactivated"
    assert mock_tool.status == "deactivated"

    # Validate CML service calls with correct arguments
    mock_cml.return_value.list_model_deployments.assert_called_once_with(
        project_id="mock_project_id",
        model_id="mock_model_id",
        build_id="mock_build_id",
    )
    mock_cml.return_value.stop_model_deployment.assert_called_once_with(
        project_id="mock_project_id",
        model_id="mock_model_id",
        build_id="mock_build_id",
        deployment_id="deployment1",
    )

@patch("studio.tools.activated_tools.os.getenv")
@patch("studio.tools.activated_tools.AgentStudioDao")
@patch("studio.tools.activated_tools.CMLServiceApi")
def test_deactivate_tool_not_found(mock_cml, mock_dao, mock_getenv):
    # Mock environment variables
    mock_getenv.side_effect = lambda key: "mock_project_id" if key == "CDSW_PROJECT_ID" else None

    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return no tool
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = None

    # Create the request
    req = DeactivateToolRequest(activated_tool_id="nonexistent_tool")

    # Call the function and validate the exception
    with pytest.raises(RuntimeError, match="Unexpected error while deactivating tool: Activated tool with ID 'nonexistent_tool' not found."):
        deactivate_tool(req, cml=mock_cml.return_value, dao=test_dao)

@patch("studio.tools.activated_tools.os.getenv")
@patch("studio.tools.activated_tools.AgentStudioDao")
@patch("studio.tools.activated_tools.CMLServiceApi")
def test_deactivate_tool_failed_deployment_stop(mock_cml, mock_dao, mock_getenv):
    # Mock environment variables
    mock_getenv.side_effect = lambda key: "mock_project_id" if key == "CDSW_PROJECT_ID" else None

    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Test Tool",
        status="active",
        cml_deployed_model_id="mock_model_id",
        cml_deployed_model_build_id="mock_build_id",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock CML service list_model_deployments
    mock_cml.return_value.list_model_deployments.return_value = MagicMock(
        model_deployments=[MagicMock(id="deployment1")]
    )

    # Mock CML service stop_model_deployment to raise an exception
    mock_cml.return_value.stop_model_deployment.side_effect = Exception("Failed to stop deployment")

    # Create the request
    req = DeactivateToolRequest(activated_tool_id="tool1")

    # Call the function and validate exception
    with pytest.raises(RuntimeError, match="Unexpected error while deactivating tool: Failed to stop or delete model deployment: Failed to stop deployment"):
        deactivate_tool(req, cml=mock_cml.return_value, dao=test_dao)

@patch("studio.tools.activated_tools.os.getenv")
@patch("studio.tools.activated_tools.AgentStudioDao")
@patch("studio.tools.activated_tools.CMLServiceApi")
def test_deactivate_tool_no_deployment_found(mock_cml, mock_dao, mock_getenv):
    # Mock environment variables
    mock_getenv.side_effect = lambda key: "mock_project_id" if key == "CDSW_PROJECT_ID" else None

    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock database query to return activated tool
    mock_tool = db_model.ActivatedTool(
        id="tool1",
        name="Test Tool",
        status="active",
        cml_deployed_model_id="mock_model_id",
        cml_deployed_model_build_id="mock_build_id",
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool

    # Mock CML service list_model_deployments to return no deployments
    mock_cml.return_value.list_model_deployments.return_value = MagicMock(model_deployments=[])

    # Create the request
    req = DeactivateToolRequest(activated_tool_id="tool1")

    # Call the function
    res = deactivate_tool(req, cml=mock_cml.return_value, dao=test_dao)

    # Validate the response
    assert isinstance(res, DeactivateToolResponse)

    # Ensure the tool's status was updated to "deactivated"
    assert mock_tool.status == "deactivated"

    # Validate CML service calls
    mock_cml.return_value.list_model_deployments.assert_called_once_with(
        project_id="mock_project_id",
        model_id="mock_model_id",
        build_id="mock_build_id",
    )
    mock_cml.return_value.stop_model_deployment.assert_not_called()
