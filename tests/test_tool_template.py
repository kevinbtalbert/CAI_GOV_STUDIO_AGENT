import pytest
from unittest.mock import patch, MagicMock
from studio.db.dao import AgentStudioDao
from studio.db import model as db_model
from studio.tools.tool_template import *
from studio.models.models import (
    ListToolTemplatesRequest,
    ListToolTemplatesResponse,
    GetToolTemplateRequest,
    GetToolTemplateResponse,
)
import json


# Tests for extract_user_params_from_code
def test_extract_user_params_from_code_valid():
    python_code = """
def tool_example_wrapper(param1: str, param2: int):
    def example_tool():
        return "dummy"
    return example_tool
"""
    params = extract_user_params_from_code(python_code)
    assert params == ["param1", "param2"]

def test_extract_user_params_from_code_no_wrapper():
    python_code = """
def another_function(param1: str, param2: int):
    return None
"""
    params = extract_user_params_from_code(python_code)
    assert params == []

def test_extract_user_params_from_code_syntax_error():
    python_code = """
def tool_example_wrapper(param1: str, param2: int
    def example_tool():
        return "dummy"
    return example_tool
"""
    with pytest.raises(ValueError) as excinfo:
        extract_user_params_from_code(python_code)
    assert "Error parsing Python code" in str(excinfo.value)


# Tests for extract_wrapper_function_name
def test_extract_wrapper_function_name_valid():
    python_code = """
def tool_example_wrapper():
    return None
"""
    wrapper_name = extract_wrapper_function_name(python_code)
    assert wrapper_name == "tool_example_wrapper"

def test_extract_wrapper_function_name_no_wrapper():
    python_code = """
def another_function():
    return None
"""
    wrapper_name = extract_wrapper_function_name(python_code)
    assert wrapper_name == ""

def test_extract_wrapper_function_name_syntax_error():
    python_code = """
def tool_example_wrapper(param1: str, param2: int
    return None
"""
    with pytest.raises(ValueError) as excinfo:
        extract_wrapper_function_name(python_code)
    assert "Error parsing Python code" in str(excinfo.value)


# Tests for list_tool_templates
@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join")
def test_list_tool_templates(mock_join, mock_open):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.ToolTemplate(
            id="t1",
            name="template1",
            source_folder_path="/path/t1",
            python_code_file_name="code.py",
            python_requirements_file_name="requirements.txt",
            tool_function_name="tool_template1_function"
        ))
        session.add(db_model.ToolTemplate(
            id="t2",
            name="template2",
            source_folder_path="/path/t2",
            python_code_file_name="code.py",
            python_requirements_file_name="requirements.txt",
            tool_function_name="tool_template2_function"
        ))
        session.commit()

    # Mock os.path.join
    mock_join.side_effect = lambda *args: "/".join(args)

    # Mock file reads
    mock_open.return_value.__enter__.return_value.read.side_effect = [
        "def tool_example_wrapper(): return None",  # Content of the first file
        "def tool_example_wrapper(): return None"   # Content of the second file
    ]

    req = ListToolTemplatesRequest()
    res = list_tool_templates(req, cml=None, dao=test_dao)

    assert isinstance(res, ListToolTemplatesResponse)
    assert len(res.templates) == 2
    assert res.templates[0].name == "template1"
    assert res.templates[1].name == "template2"

@patch("studio.db.dao.AgentStudioDao")
def test_list_tool_templates_empty_db(mock_dao):
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock the database to return an empty list
    test_session.query.return_value.all.return_value = []

    req = ListToolTemplatesRequest()
    res = list_tool_templates(req, cml=None, dao=test_dao)

    # Validate the response
    assert isinstance(res, ListToolTemplatesResponse)
    assert len(res.templates) == 0

@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join")
def test_list_tool_templates_invalid_code(mock_join, mock_open, mock_validate):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.ToolTemplate(
            id="t1",
            name="template1",
            source_folder_path="/path/t1",
            python_code_file_name="code.py",
            python_requirements_file_name="requirements.txt",
            tool_function_name="tool_template_function"
        ))
        session.commit()

    # Mock file paths
    mock_join.side_effect = lambda *args: "/".join(args)

    # Mock file reads
    mock_open.return_value.__enter__.return_value.read.side_effect = [
        "invalid python code",  # Invalid Python code
        "package==1.0"  # Mocked requirements.txt content
    ]

    # Mock validation to return invalid
    mock_validate.return_value = (False, ["Syntax error"])

    req = ListToolTemplatesRequest()
    res = list_tool_templates(req, cml=None, dao=test_dao)

    # Validate the response
    assert isinstance(res, ListToolTemplatesResponse)
    assert len(res.templates) == 1
    assert not res.templates[0].is_valid  # Should be invalid due to syntax error

@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join")
def test_list_tool_templates_file_read_error(mock_join, mock_open):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.ToolTemplate(
            id="t1",
            name="template1",
            source_folder_path="/path/t1",
            python_code_file_name="code.py",
            python_requirements_file_name="requirements.txt",
            tool_function_name="tool_template_function"
        ))
        session.commit()

    # Mock file paths
    mock_join.side_effect = lambda *args: "/".join(args)

    # Simulate file read errors
    mock_open.side_effect = IOError("File read error")

    req = ListToolTemplatesRequest()
    res = list_tool_templates(req, cml=None, dao=test_dao)

    # Validate the response
    assert isinstance(res, ListToolTemplatesResponse)
    assert len(res.templates) == 1
    assert not res.templates[0].is_valid  # Should be invalid due to file read error

# Tests for get_tool_template
@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join")
def test_get_tool_template(mock_join, mock_open, mock_validate):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    # Insert a mock tool template into the database
    with test_dao.get_session() as session:
        session.add(db_model.ToolTemplate(
            id="t1",
            name="template1",
            source_folder_path="/path/t1",
            python_code_file_name="code.py",
            python_requirements_file_name="requirements.txt",
            tool_function_name="tool_template_function"
        ))
        session.commit()

    # Mock file paths
    mock_join.side_effect = lambda *args: "/".join(args)

    # Mock file reads
    mock_open.return_value.__enter__.return_value.read.side_effect = [
        "def tool_example_wrapper(param1: str): return None",  # Mocked Python code content
        "package==1.0"  # Mocked requirements.txt content
    ]

    # Mock validate_tool_template_code to return True
    mock_validate.return_value = (True, [])

    # Create a request for the tool template
    req = GetToolTemplateRequest(tool_template_id="t1")
    
    # Call the function being tested
    res = get_tool_template(req, cml=None, dao=test_dao)

    # Validate the response
    assert isinstance(res, GetToolTemplateResponse)
    assert res.template.name == "template1"
    assert res.template.is_valid  # Ensure it is valid since the mocked content is correct
    assert "param1" in json.loads(res.template.tool_metadata)["user arguments"]

@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join")
def test_get_tool_template_missing_python_file(mock_join, mock_open):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.ToolTemplate(
            id="t1",
            name="template1",
            source_folder_path="/path/t1",
            python_code_file_name="code.py",
            python_requirements_file_name="requirements.txt",
            tool_function_name="tool_template_function"
        ))
        session.commit()

    # Mock file paths
    mock_join.side_effect = lambda *args: "/".join(args)

    # Simulate missing Python file
    mock_open.side_effect = [IOError("File not found"), "package==1.0"]

    req = GetToolTemplateRequest(tool_template_id="t1")
    res = get_tool_template(req, cml=None, dao=test_dao)

    # Validate the response
    assert isinstance(res, GetToolTemplateResponse)
    assert not res.template.is_valid  # Should be invalid due to missing Python file

@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join")
def test_get_tool_template_syntax_error(mock_join, mock_open, mock_validate):
    test_dao = AgentStudioDao(engine_url="sqlite:///:memory:", echo=False)

    with test_dao.get_session() as session:
        session.add(db_model.ToolTemplate(
            id="t1",
            name="template1",
            source_folder_path="/path/t1",
            python_code_file_name="code.py",
            python_requirements_file_name="requirements.txt",
            tool_function_name="tool_template_function"
        ))
        session.commit()

    # Mock file paths
    mock_join.side_effect = lambda *args: "/".join(args)

    # Mock file reads
    mock_open.return_value.__enter__.return_value.read.side_effect = [
        "def tool_example_wrapper(param1: str): invalid_syntax",  # Invalid Python code
        "package==1.0"  # Mocked requirements.txt content
    ]

    # Mock validation to return invalid
    mock_validate.return_value = (False, ["Syntax error in code"])

    req = GetToolTemplateRequest(tool_template_id="t1")
    res = get_tool_template(req, cml=None, dao=test_dao)

    # Validate the response
    assert isinstance(res, GetToolTemplateResponse)
    assert not res.template.is_valid  # Should be invalid due to syntax error

@patch("os.makedirs")
@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join")
@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("studio.db.dao.AgentStudioDao")
@patch("studio.tools.tool_template.TOOL_TEMPLATE_CATALOG_LOCATION", "/tool_template_catalog_location")
def test_add_tool_template_success(mock_dao, mock_validate, mock_join, mock_open, mock_makedirs):
    # Mock DAO session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock the database query for duplicates to return None
    test_session.query.return_value.filter_by.return_value.first.return_value = None

    # Mock validate_tool_template_code to return valid
    mock_validate.return_value = (True, [])

    # Mock file operations
    mock_open.return_value.__enter__.return_value.write = MagicMock()
    mock_join.side_effect = lambda *args: "/".join(args)

    # Mock directory creation
    mock_makedirs.return_value = None

    # Prepare the AddToolTemplateRequest
    req = AddToolTemplateRequest(
        tool_template_name="Valid Tool",
        python_code="def tool_example_wrapper(): return None",
        python_requirements="package==1.0"
    )

    # Call the function being tested
    res = add_tool_template(req, cml=None, dao=test_dao)

    # Validate the response
    assert isinstance(res, AddToolTemplateResponse)
    assert res.tool_template_id is not None

    # Validate that the template was added to the database
    test_session.add.assert_called_once()
    test_session.commit.assert_called_once()

    # Validate file operations
    mock_makedirs.assert_called_once()
    mock_open.assert_any_call("/tool_template_catalog_location/valid_tool/tool.py", "w")
    mock_open.assert_any_call("/tool_template_catalog_location/valid_tool/requirements.txt", "w")

@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("studio.db.dao.AgentStudioDao")
@patch("studio.tools.tool_template.TOOL_TEMPLATE_CATALOG_LOCATION", "/tool_template_catalog_location")
def test_add_tool_template_invalid_python_code(mock_dao, mock_validate):
    test_dao = mock_dao.return_value
    mock_validate.return_value = (False, ["Syntax error in code"])  # Mock invalid code validation

    req = AddToolTemplateRequest(
        tool_template_name="Invalid Tool",
        python_code="def invalid_code(: return None",  # Invalid syntax
        python_requirements="package==1.0"
    )

    # Expect RuntimeError because add_tool_template wraps the ValueError
    with pytest.raises(RuntimeError) as excinfo:
        add_tool_template(req, cml=None, dao=test_dao)

    # Assert the error message contains information about the invalid Python code
    assert "Unexpected error while adding tool template" in str(excinfo.value)
    assert "Invalid Python code for tool template" in str(excinfo.value)
    assert "Syntax error in code" in str(excinfo.value)

@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("studio.db.dao.AgentStudioDao")
@patch("studio.tools.tool_template.TOOL_TEMPLATE_CATALOG_LOCATION", "/tool_template_catalog_location")
def test_add_tool_template_duplicate_name(mock_dao, mock_validate):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Simulate an existing tool template in the database
    mock_existing_template = MagicMock()
    test_session.query.return_value.filter_by.return_value.first.return_value = mock_existing_template

    # Mock validate_tool_template_code to return valid Python code
    mock_validate.return_value = (True, [])

    # Prepare the AddToolTemplateRequest
    req = AddToolTemplateRequest(
        tool_template_name="Duplicate Tool",
        python_code="def tool_example_wrapper(): return None",
        python_requirements="package==1.0"
    )

    # Expect a RuntimeError due to the duplicate tool template
    with pytest.raises(RuntimeError) as excinfo:
        add_tool_template(req, cml=None, dao=test_dao)

    # Verify the error message contains the duplicate name error
    assert "Unexpected error while adding tool template" in str(excinfo.value)
    assert "A tool template with this name already exists." in str(excinfo.value)

    # Ensure validate_tool_template_code was called
    mock_validate.assert_called_once_with(req.python_code)

    # Ensure no files or directories were created
    test_session.add.assert_not_called()
    test_session.commit.assert_not_called()

@patch("os.makedirs")
@patch("builtins.open", new_callable=MagicMock)
@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("studio.db.dao.AgentStudioDao")
def test_update_tool_template_not_found(mock_dao, mock_validate, mock_open, mock_makedirs):
    # Mock DAO and session
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock query to return None (tool template not found)
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = None

    # Mock validate_tool_template_code to simulate valid Python code
    mock_validate.return_value = (True, [])

    # Prepare the UpdateToolTemplateRequest
    req = UpdateToolTemplateRequest(
        tool_template_id="nonexistent",
        tool_template_name="Updated Tool",
        python_code="def tool_example_wrapper(): return None",
        python_requirements="package==1.0"
    )

    # Call update_tool_template and assert it raises the expected RuntimeError
    with pytest.raises(RuntimeError) as excinfo:
        update_tool_template(req, cml=None, dao=test_dao)

    # Assert the error message
    assert "Unexpected error while updating tool template" in str(excinfo.value)
    assert "Tool template with ID 'nonexistent' not found" in str(excinfo.value)

    # Ensure validate_tool_template_code was called exactly once
    mock_validate.assert_called_once_with(req.python_code)

    # Ensure no directory or file operations were attempted
    mock_makedirs.assert_not_called()
    mock_open.assert_not_called()

    # Ensure no database commit was attempted
    test_session.commit.assert_not_called()

@patch("studio.db.dao.AgentStudioDao")
@patch("studio.tools.tool_template.validate_tool_template_code")
def test_update_tool_template_pre_built(mock_validate, mock_dao):
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    # Mock a pre-built tool template
    mock_tool_template = MagicMock(pre_built=True)
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool_template

    # Mock validate_tool_template_code to simulate valid Python code
    mock_validate.return_value = (True, [])

    # Prepare the UpdateToolTemplateRequest
    req = UpdateToolTemplateRequest(
        tool_template_id="prebuilt",
        tool_template_name="Updated Tool",
        python_code="def tool_example_wrapper(): return None",
        python_requirements="package==1.0"
    )

    # Call update_tool_template and assert it raises the expected RuntimeError
    with pytest.raises(RuntimeError) as excinfo:
        update_tool_template(req, cml=None, dao=test_dao)

    # Validate the error message
    assert "Unexpected error while updating tool template" in str(excinfo.value)
    assert "Tool template with ID 'prebuilt' si pre-built and cannot be updated" in str(excinfo.value)

    # Ensure no directory or file operations were attempted
    test_session.commit.assert_not_called()

@patch("os.makedirs")
@patch("builtins.open", new_callable=MagicMock)
@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("studio.db.dao.AgentStudioDao")
def test_update_tool_template_directory_write_failure(mock_dao, mock_validate, mock_open, mock_makedirs):
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    mock_validate.return_value = (True, [])

    # Mock existing tool template
    mock_tool_template = db_model.ToolTemplate(
        id="t1",
        name="Existing Template",
        source_folder_path="/path/t1",
        python_code_file_name="code.py",
        python_requirements_file_name="requirements.txt",
        tool_function_name="tool_function"
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool_template

    # Mock directory creation failure
    mock_makedirs.side_effect = OSError("Directory creation failed")

    req = UpdateToolTemplateRequest(
        tool_template_id="t1",
        tool_template_name="Updated Template",
        python_code="def tool_example_wrapper(): return None",
        python_requirements="package==1.0"
    )

    with pytest.raises(RuntimeError) as excinfo:
        update_tool_template(req, cml=None, dao=test_dao)
    assert "Failed to update tool template files" in str(excinfo.value)
    assert "Directory creation failed" in str(excinfo.value)

@patch("os.makedirs")
@patch("builtins.open", new_callable=MagicMock)
@patch("studio.tools.tool_template.validate_tool_template_code")
@patch("studio.db.dao.AgentStudioDao")
def test_update_tool_template_success(mock_dao, mock_validate, mock_open, mock_makedirs):
    test_dao = mock_dao.return_value
    test_session = test_dao.get_session.return_value.__enter__.return_value

    mock_validate.return_value = (True, [])

    # Mock existing tool template
    mock_tool_template = db_model.ToolTemplate(
        id="t1",
        name="Existing Template",
        source_folder_path="/path/t1",
        python_code_file_name="code.py",
        python_requirements_file_name="requirements.txt",
        tool_function_name="tool_function"
    )
    test_session.query.return_value.filter_by.return_value.one_or_none.return_value = mock_tool_template

    req = UpdateToolTemplateRequest(
        tool_template_id="t1",
        tool_template_name="Updated Template",
        python_code="def tool_example_wrapper(): return None",
        python_requirements="package==1.0"
    )

    res = update_tool_template(req, cml=None, dao=test_dao)

    assert isinstance(res, UpdateToolTemplateResponse)
    assert res.tool_template_id == "t1"
    mock_open.assert_any_call("/path/t1/code.py", "w")
    mock_open.assert_any_call("/path/t1/requirements.txt", "w")
