# File: tool.py

from textwrap import dedent
from typing import Literal, Type
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool

import json

class UserParameters(BaseModel):
    pass

class CustomerProfileLookupTool(StudioBaseTool):
    class ToolParameters(BaseModel):
        customer_id: str = Field(description="Customer ID - The unique identifier for the customer")

    name: str = "Customer Profile Data Retrieval Tool"
    description: str = dedent(
        """
        This tool fetches Customer profile data which includes their account information and their previously specified investment preferences.

        Returns:
            str: json string with customer profile data containing customer info and investment preferences including risk profile, investment horizon,
                 and financial information.
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(self, customer_id) -> str:
        # Placeholder for actual portfolio data retrieval
        customer_profile = {
            "customer_id": customer_id,
            "name": "John Doe", 
            "risk_profile": "Moderate",
            "investment_horizon": "Long-term",
            "max_drawdown": "20%",
            "annual_income": 100000,
            "amount_to_invest" : 100000,
        }
        return json.dumps(customer_profile)