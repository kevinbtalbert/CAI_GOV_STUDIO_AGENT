from textwrap import dedent
from typing import Type, Literal,Optional, List
from pydantic import BaseModel, Field
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pydantic import BaseModel as StudioBaseTool

class UserParameters(BaseModel):
    """
    Args:
        slack_api_token (str): The Slack API token for authentication.
    """
    slack_api_token: str

class SlackIntegrationTool(StudioBaseTool):
    class ToolParameters(BaseModel):
        action_type: Literal["sendMessage"] = Field(description="Action type specifying the operation to perform on Email: 'send message'")
        recipient: str = Field(
            description="The Slack channel name (e.g., 'general' or '#general') or user email (e.g., 'user@example.com')."
        )
        message: Optional[str] = Field(
            description="The message content to send. This is optional; files can be sent without a message.",
            default=None
        )
        file_paths: Optional[List[str]] = Field(
            description="A list of file paths to attach to the message. Optional.",
            default=None
        )

    name: str = "Slack Integration Tool"
    description: str = dedent(
        """
        Posts a message with optional multiple file attachments to a specified Slack username or channel name.

        Args:
            recipient (str): The Slack channel name (e.g., 'general' or '#general') or user email (e.g., 'user@example.com').
            message (Optional[str]): The message content to send. Defaults to None if no message is provided.
            file_paths (Optional[List[str]]): A list of file paths to attach to the message.

        Returns:
            str: Success or error message.
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(
        self,
        action_type: Literal["sendMessage"],
        recipient: str,
        message: Optional[str] = None,
        file_paths: Optional[List[str]] = None
    ) -> str:
        """
        Action to send a message and/or files to the specified Slack recipient.

        Parameters:
        recipient (str): The Slack channel name or user email.
        message (Optional[str], optional): The message content to send. Defaults to None.
        file_paths (Optional[List[str]], optional): A list of file paths for attachments. Defaults to None.

        Returns:
        str: A confirmation message.
        """
        client = WebClient(token=self.user_parameters.slack_api_token)

        try:
            if action_type=="sendMessage":
                is_channel = not ("@" in recipient or "." in recipient)  # Infer as channel if no '@' or '.'

                if is_channel:
                    # Ensure the channel name starts with '#'
                    recipient = recipient.strip()
                    if not recipient.startswith("#"):
                        recipient = "#" + recipient

                    if file_paths:
                        # Upload each file using files_upload_v2
                        for file_path in file_paths:
                            response = client.files_upload_v2(
                                channel=recipient,
                                file=file_path,
                                initial_comment=message if message else ""  # Only include message if provided
                            )
                            if not response.get("ok", False):
                                return f"Error: Failed to upload file '{file_path}' to channel '{recipient}'."
                    else:
                        # Send a simple message if no files
                        if message:
                            response = client.chat_postMessage(
                                channel=recipient,
                                text=message
                            )
                            if not response.get("ok", False):
                                return f"Error: Failed to send message to channel '{recipient}'."
                        else:
                            return "Error: No message and no files provided to send."

                    return f"Message and/or files sent successfully to channel '{recipient}'."
                else:
                    # Resolve user ID by email
                    user_response = client.users_lookupByEmail(email=recipient)
                    user_id = user_response.get("user", {}).get("id")

                    if not user_id:
                        return f"Error: No user found with the email '{recipient}'."

                    # Open DM with user
                    dm_response = client.conversations_open(users=user_id)
                    dm_channel = dm_response.get("channel", {}).get("id")

                    if not dm_channel:
                        return f"Error: Failed to open a DM channel with user '{recipient}'."

                    if file_paths:
                        # Upload each file using files_upload_v2
                        for file_path in file_paths:
                            response = client.files_upload_v2(
                                channel=dm_channel,
                                file=file_path,
                                initial_comment=message if message else ""  # Only include message if provided
                            )
                            if not response.get("ok", False):
                                return f"Error: Failed to upload file '{file_path}' to user '{recipient}'."
                    else:
                        # Send a simple message if no files
                        if message:
                            response = client.chat_postMessage(
                                channel=dm_channel,
                                text=message
                            )
                            if not response.get("ok", False):
                                return f"Error: Failed to send message to user '{recipient}'."
                        else:
                            return "Error: No message and no files provided to send."

                    return f"Message and/or files sent successfully to user '{recipient}'."

            return "Invalid action type. Available action is 'sendMessage'."
        except SlackApiError as e:
            error_message = e.response.get('error', 'unknown_error')
            return f"Slack API error: {error_message}. Please check the recipient format, file paths, or permissions."
