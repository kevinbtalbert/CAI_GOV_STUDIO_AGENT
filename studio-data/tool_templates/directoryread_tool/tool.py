from typing import Optional, Type
from textwrap import dedent
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool
import os

class UserParameters(BaseModel):
    """
    Args:
        directory (Optional[str]): The directory for listing the files (optional).
    """
    directory: Optional[str] = None

class DirectoryReadTool(StudioBaseTool):
    class ToolParameters(BaseModel):
        directory: Optional[str] = Field(None, description="The directory path for file listing.")

    name: str = "List files in directory"
    description: str = dedent(
        """
        A tool that recursively lists all files in the specified directory.
        The directory can be provided as a function argument or as a user parameter.
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(self, directory: Optional[str] = None) -> str:
        # Use function argument if provided, else fallback to user parameter
        directory = self.user_parameters.directory if self.user_parameters.directory else directory

        if not directory:
            return "Error: No directory provided."

        # Remove trailing slash if present
        directory = directory.rstrip("/")

        # List all files in the directory recursively
        files_list = [
            f"{directory}/{os.path.join(root, filename).replace(directory, '').lstrip(os.path.sep)}"
            for root, _, files in os.walk(directory)
            for filename in files
        ]
        
        if not files_list:
            return f"No files found in the specified directory: {directory}"

        # Prepare the file list as a formatted string
        files = "\n- ".join(files_list)
        return f"File paths in {directory}:\n- {files}"