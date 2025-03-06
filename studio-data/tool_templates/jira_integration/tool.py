from typing import Literal, Optional, Dict
from pydantic import Field
from typing import Literal, Type, Optional
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool

# import required libraries
from jira import JIRA

class UserParameters(BaseModel):
    jira_url: Optional[str] = None
    auth_token: Optional[str] = None
    user_email: Optional[str] = None

class JiraIntegrationTool(StudioBaseTool):
    class ToolParameters(BaseModel):
        action_type: Literal["search", "create", "update", "delete"] = Field(description="Action type specifying the operation to perform on Jira: 'search', 'create', 'update', or 'delete'")
        query_params: Optional[str] = Field(description="JQL query string for filtering Jira data, formatted like 'project=PROJ AND assignee != currentUser()'")
        issue_data: Optional[Dict] = Field(description="Data for creating a Jira issue. Example format: {'project': {'id': 123}, 'summary': 'Issue title', 'description': 'Issue description', 'issuetype': {'name': 'Bug'}}")
        issue_id: Optional[str] = Field(description="ID of the issue to update or delete, required for 'update' and 'delete' actions.")
        update_data: Optional[Dict] = Field(description="Data for updating a Jira issue in the format: {'fields': {'summary': 'new summary', 'description': 'updated description'}}")

    name: str = "Jira Integration Tool"
    description: str = "Jira Integration Tool: Executes specified actions on Jira such as searching, creating, updating, and deleting issues."
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters

    def _run(
        self,
        action_type: Literal["search", "create", "update", "delete"],
        query_params: Optional[str] = None,
        issue_data: Optional[Dict] = None,
        issue_id: Optional[str] = None,
        update_data: Optional[Dict] = None
    ) -> str:
        """
        Jira Integration Tool: Executes specified actions on Jira such as searching, creating, updating, and deleting issues.
        """
        try:
            # Initialize Jira client
            jira_client = JIRA(server=self.user_parameters.jira_url, basic_auth=(self.user_parameters.user_email, self.user_parameters.auth_token))

            if action_type == "search":
                if query_params:
                    issues = jira_client.search_issues(query_params)
                    return str([issue.raw for issue in issues]) if issues else "No issues found for the provided query."
                return "Error: 'query_params' is required for 'search' action."

            elif action_type == "create":
                if issue_data:
                    issue = jira_client.create_issue(fields=issue_data)
                    return f"Issue created successfully: {issue.key}"
                return "Error: 'issue_data' is required for 'create' action."

            elif action_type == "update":
                if issue_id and update_data:
                    issue = jira_client.issue(issue_id)
                    issue.update(fields=update_data.get('fields', {}))
                    return f"Issue {issue_id} updated successfully."
                return "Error: Both 'issue_id' and 'update_data' are required for 'update' action."

            elif action_type == "delete":
                if issue_id:
                    issue = jira_client.issue(issue_id)
                    issue.delete()
                    return f"Issue {issue_id} deleted successfully."
                return "Error: 'issue_id' is required for 'delete' action."

            return "Invalid action type. Available actions are 'search', 'create', 'update', 'delete'."

        except Exception as e:
            return f"Failed to perform {action_type} action: {str(e)}"
