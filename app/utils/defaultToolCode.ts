export const defaultToolPyCode = `# File: tool.py

from textwrap import dedent
from typing import Dict, List, Optional, Type
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool # This import is required for the tool to be recognized by the studio

# import <any other requirements(python libraries) for the tool>

class UserParameters(BaseModel):
    """
    This class is used to define the parameters that would be passed by the user.
    These are used to configuire the same tool template for different instances of the service being used by the tool.
    For example,
    This can include URLs, file paths, API keys, etc.

    User parameters can also be an empty class, if the tool does not require any user parameters.
    """

    example_url: str
    example_api_key: str
    example_file_path: Optional[str] = None
    example_other_parameter: Optional[str] = None

class NewTool(StudioBaseTool):

    class ToolParameters(BaseModel):
        """
        This class is used to define the parameters that would be determined by AI/Agents.
        Make sure to properly annotate the parameters with the correct type and description,
        so that LLMs can understand the meaning of the parameters, and suggest the correct values.
        """

        runtime_parameter_1: str = Field(
            description="Description explaining the utility of the parameter."
        )
        runtime_parameter_2: float = Field(
            description="Description explaining the utility of the parameter."
        )
        runtime_parameter_3: Optional[Dict[str, str]] = Field(
            description="Description explaining the utility of the parameter."
        )

    name: str = "New Tool"
    description: str = dedent(
        """
        Please write multiline decsription for the tool, so that LLMs can understand the utility of the tool.
                         
        The description can also be used to describe the parameters of the tool in much more detail.
                         
        Agent studio will also uplevel the description of the tool in the UI.
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(
        self, runtime_parameter_1, runtime_parameter_2, runtime_parameter_3=None
    ) -> str:
        # Implementation for the tool goes here.
        return f"""
            {self.user_parameters.example_url}
            {self.user_parameters.example_api_key}
            {self.user_parameters.example_file_path}
            {self.user_parameters.example_other_parameter}
            {runtime_parameter_1}
            {runtime_parameter_2}
            {runtime_parameter_3}
        """
`;

export const defaultRequirementsTxt = `pydantic==2.10.6

# Refer to https://pip.pypa.io/en/stable/reference/requirements-file-format/ for requirements.txt format
# Please mention the tool specific python packages requirements below:
`;
