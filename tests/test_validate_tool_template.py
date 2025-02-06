from studio.tools.tool_template import validate_tool_template_code

# Test cases for validate_tool_template_code

def test_valid_tool_template_code():
    """Test valid tool template code with correct wrapper and annotations."""
    python_code = """
from typing import Annotated
from pydantic import Field

def tool_example_wrapper():
    def example_tool(
        param1: Annotated[int, Field(description="An integer parameter")],
        param2: Annotated[str, Field(description="A string parameter")]
    ) -> str:
        "Example tool description"
        return "example response"
    return example_tool
"""
    is_valid, errors = validate_tool_template_code(python_code)
    assert is_valid
    assert not errors


def test_missing_wrapper_function():
    """Test code with no wrapper function."""
    python_code = """
from typing import Annotated
from pydantic import Field

def not_a_wrrappeer():
    def example_tool(
        param1: Annotated[int, Field(description="An integer parameter")],
        param2: Annotated[str, Field(description="A string parameter")]
    ) -> str:
        "Example tool description"
        return "example response"
    return example_tool
"""
    is_valid, errors = validate_tool_template_code(python_code)
    assert not is_valid
    assert "No wrapper function found ending with '_wrapper'." in errors


def test_multiple_return_statements_in_wrapper():
    """Test code with multiple return statements in the wrapper function."""
    python_code = """
from typing import Annotated
from pydantic import Field

def tool_example_wrapper():
    def example_tool(
        param1: Annotated[int, Field(description="An integer parameter")],
        param2: Annotated[str, Field(description="A string parameter")]
    ) -> str:
        "Example tool description"
        return "example response"
    return example_tool
    return None  # Extra return statement
"""
    is_valid, errors = validate_tool_template_code(python_code)
    assert not is_valid
    assert "The wrapper function 'tool_example_wrapper' must have only one top-level return statement." in errors


def test_missing_inner_function_annotation():
    """Test code where the inner function is missing an annotation."""
    python_code = """
from typing import Annotated
from pydantic import Field

def tool_example_wrapper():
    def example_tool(
        param1: int,  # Missing Annotated
        param2: Annotated[str, Field(description="A string parameter")]
    ) -> str:
        "Example tool description"
        return "example response"
    return example_tool
"""
    is_valid, errors = validate_tool_template_code(python_code)
    assert not is_valid
    assert "Argument 'param1' in the function 'example_tool' must use 'Annotated'." in errors


def test_missing_inner_function_docstring():
    """Test code where the inner function is missing a docstring."""
    python_code = """
from typing import Annotated
from pydantic import Field

def tool_example_wrapper():
    def example_tool(
        param1: Annotated[int, Field(description="An integer parameter")],
        param2: Annotated[str, Field(description="A string parameter")]
    ) -> str:
        # Missing docstring
        return "example response"
    return example_tool
"""
    is_valid, errors = validate_tool_template_code(python_code)
    assert not is_valid
    assert "The function 'example_tool' must have a docstring describing the tool." in errors


def test_syntax_error_in_code():
    """Test code with a syntax error."""
    python_code = """
from typing import Annotated
from pydantic import Field

def tool_example_wrapper():
    def example_tool(
        param1: Annotated[int, Field(description="An integer parameter")],
        param2: Annotated[str, Field(description="A string parameter")]
    -> str:  # Syntax error here
        "Example tool description"
        return "example response"
    return example_tool
"""
    is_valid, errors = validate_tool_template_code(python_code)
    assert not is_valid
    assert any("Syntax error in Python code" in error for error in errors)


def test_no_return_statement_in_wrapper():
    """Test code where the wrapper function has no return statement."""
    python_code = """
from typing import Annotated
from pydantic import Field

def tool_example_wrapper():
    def example_tool(
        param1: Annotated[int, Field(description="An integer parameter")],
        param2: Annotated[str, Field(description="A string parameter")]
    ) -> str:
        "Example tool description"
        return "example response"
    # Missing return statement
"""
    is_valid, errors = validate_tool_template_code(python_code)
    assert not is_valid
    assert "The wrapper function 'tool_example_wrapper' must have a return statement." in errors
