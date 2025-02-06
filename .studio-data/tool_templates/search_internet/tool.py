import json
import requests
from typing import Type
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool
from textwrap import dedent

class UserParameters(BaseModel):
    serper_api_key: str


class SearchInternetTool(StudioBaseTool):
    class ToolParameters(BaseModel):
        query: str = Field(description="The search query to find relevant results")

    name: str = "Search Internet Tool"
    description: str = dedent(
        """
        Useful to search the internet about a given topic and return relevant results.
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(self, query: str) -> str:
        top_result_to_return = 3
        url = "https://google.serper.dev/search"

        # Prepare request payload and headers
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': self.user_parameters.serper_api_key,
            'content-type': 'application/json'
        }

        # Make the POST request
        response = requests.request("POST", url, headers=headers, data=payload)

        # Check if 'organic' key exists in the response
        if 'organic' not in response.json():
            return "Sorry, I couldn't find anything about that. There might be an issue with your Serper API key."

        # Extract and format results
        results = response.json().get('organic', [])
        formatted_results = []
        for result in results[:top_result_to_return]:
            try:
                formatted_results.append('\n'.join([
                    f"Title: {result['title']}",
                    f"Link: {result['link']}",
                    f"Snippet: {result['snippet']}",
                    "\n-----------------"
                ]))
            except KeyError:
                continue  # Skip if any key is missing

        return '\n'.join(formatted_results)
