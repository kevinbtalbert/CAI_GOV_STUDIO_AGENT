# File: tool.py

from textwrap import dedent
from typing import Literal, Type
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool

class UserParameters(BaseModel):
    pass

class CalculatorTool(StudioBaseTool):

    class ToolParameters(BaseModel):
        a: float = Field(
            description="first number"
        )
        b: float = Field(
            description="second number"
        )
        operator: Literal["+", "-", "*", "/"] = Field(
            description="operator"
        )

    name: str = "Calculator Tool"
    description: str = dedent(
        """
        Calculator tool which can do basic addition, subtraction, multiplication, and division.
        Division by 0 is not allowed.
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(
        self, a, b, operator
    ) -> str:
        # Implementation for the tool goes here.
        res = None
        if operator == "+":
            res = a + b
        elif operator == "-":
            res = a - b
        elif operator == "*":
            res = a * b
        elif operator == "/":
            res = float(a / b)
        else:
            raise ValueError("Invalid operator")
        return str(res)
