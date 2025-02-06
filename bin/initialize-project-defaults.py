from studio.db.utils import import_defaults
from studio.db.dao import get_sqlite_db_location, delete_database
import os
import subprocess
from pathlib import Path

def main():
    
    # Make the app state location if it's not yet created.
    os.makedirs(os.path.dirname(get_sqlite_db_location()), exist_ok=True)
    
    # Also run any and all DB upgrades. Our upgrades need to be compatible with our
    # style of project defaults here - which means that if project defaults gets updated with
    # new schemas, then alembic still needs to go through the entire ugrade lineage even though
    # the new schemas alredy exist. This is to support both old users and new users of agent studio.
    # This means that, for example, if there was an alembic version upgrade to add a column, we need
    # to first check if that column already exists. If the column already exists, someone new must have
    # pulled down agent studio and ran a fresh project-defaults. If the column does not exist, that 
    # means we are performing an upgrade.
    if Path(get_sqlite_db_location()).exists():
        subprocess.run(["uv run alembic upgrade head"], shell=True, capture_output=True, text=True)

    # Import project defaults.
    import_defaults()
    
    return



if __name__ == "__main__":
    main()
