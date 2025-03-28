import json
from gql import gql, Client
from datetime import datetime

# This is the Python equivalent of your TypeScript constants:
EVENT_TYPES = [
    "Crew.kickoff",
    "Agent._start_task",
    "completion",
    "ToolUsage._use",
    "ToolUsage._end_use",
    "Agent._end_task",
    "Crew.complete",
]


def get_project_and_trace_info(client: Client, local_trace_id: str):
    """
    Given a local trace ID, query all projects and find the one whose node.trace.id exists.
    Returns a dictionary containing { "projectId": ..., "globalTraceId": ... }.
    """

    # GraphQL query in a multi-line string.
    # We'll embed the `trace_id` into the query string:
    query_str = f"""
    query QueryProjectsForTraceExistence {{
      projects(first: 1000) {{
        edges {{
          node {{
            id
            trace(traceId: "{local_trace_id}") {{
              id
            }}
          }}
        }}
      }}
    }}
    """

    # Structure your payload:
    result = client.execute(gql(query_str))

    edges = result["projects"]["edges"]

    # Find the project whose 'trace' is not null and has an 'id'
    project = next((edge for edge in edges if edge["node"]["trace"] and edge["node"]["trace"].get("id")), None)

    if not project:
        raise ValueError(f"No project found for traceId={local_trace_id}")

    global_trace_id = project["node"]["trace"]["id"]
    project_id = project["node"]["id"]

    return {"projectId": project_id, "globalTraceId": global_trace_id}


def get_crew_events(client: Client, local_trace_id: str) -> dict:
    """
    Get all "descendants" spanning events for the global trace that corresponds
    to a local trace ID. Returns a dict with keys "projectId" and "events".
    """
    # First, retrieve the global trace ID (and project ID) from your helper:
    project_and_trace_info = get_project_and_trace_info(client, local_trace_id)
    project_id = project_and_trace_info["projectId"]
    global_trace_id = project_and_trace_info["globalTraceId"]

    # GraphQL query using a variable for the global trace ID
    query_str = f"""
    query GetCrewEvents {{
        node(id: "{global_trace_id}") {{
            ... on Trace {{
            rootSpan {{
                name
                descendants {{
                id
                name
                startTime
                cumulativeTokenCountTotal
                cumulativeTokenCountPrompt
                cumulativeTokenCountCompletion
                endTime
                attributes
                events {{
                    message
                    name
                    timestamp
                }}
                }}
            }}
            }}
        }}
    }}
    """

    # Execute the query with the global trace ID
    result = client.execute(gql(query_str))

    node_data = result["node"]
    if not node_data or not node_data.get("rootSpan"):
        return {"projectId": project_id, "events": []}

    descendants = node_data["rootSpan"]["descendants"] or []

    # Filter to the spans whose `name` is in EVENT_TYPES
    filtered_events = []
    for d in descendants:
        if d["name"] in EVENT_TYPES:
            # Parse the "attributes" JSON, if present
            parsed_attributes = {}
            if d["attributes"]:
                try:
                    parsed_attributes = json.loads(d["attributes"])
                except json.JSONDecodeError:
                    parsed_attributes = {}

            event_object = {
                **d,
                "attributes": parsed_attributes,
                "events": d.get("events", []),
            }
            filtered_events.append(event_object)

    # Sort by the 'startTime' ascending, converting ISO string to datetime
    def parse_time(e):
        # e.g. '2023-03-12T12:34:56.789Z'
        return datetime.fromisoformat(e["startTime"].replace("Z", "+00:00"))

    filtered_events.sort(key=parse_time)

    return {"projectId": project_id, "events": filtered_events}
