# File: tool.py

from textwrap import dedent
from typing import Literal, Type
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool

import json

class UserParameters(BaseModel):
    pass

class CustomerPortfolioLookupTool(StudioBaseTool):
    class ToolParameters(BaseModel):
        customer_id: str = Field(description="Customer ID - The unique identifier for the customer")

    name: str = "Customer Portfolio Data Retrieval Tool"
    description: str = dedent(
        """
        This tool fetches portfolio data including stocks, bonds and cash holdings for a given customer ID. Currently returns placeholder data.

        Returns:
            str: json string with customer portfolio data containing stocks, bonds and cash holdings
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(self, customer_id) -> str:
        # Placeholder for actual portfolio data retrieval
        portfolio_data = {
            "portfolio_makeup": {
                "stocks": ["AAPL", "GOOGL", "MSFT", "ADBE"],
                "percent": ["0.2", "0.4", "0.3", "0.1" ]
            },
            "total_value": 100000
        }
        return json.dumps(portfolio_data)