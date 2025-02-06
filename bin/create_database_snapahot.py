import os
import json
from studio.db.dao import AgentStudioDao
from studio.db.utils import export_to_dict

def create_project_defaults_file(file_path="data/project_defaults.json"):
    """
    Create a JSON file snapshotting the current database state.

    :param file_path: Path to the JSON file to be created.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Initialize the DAO
    dao = AgentStudioDao()

    # Snapshot the database to a dictionary
    db_snapshot = export_to_dict(dao=dao)

    # Write the snapshot to the file
    with open(file_path, "w") as file:
        json.dump(db_snapshot, file, indent=2)

    print(f"Project defaults file created at: {file_path}")

if __name__ == "__main__":
    create_project_defaults_file()
