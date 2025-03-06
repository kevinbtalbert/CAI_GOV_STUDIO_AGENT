"""add directory field to workflows

Revision ID: 59fbac3b744e
Revises: 0819cfc5e56c
Create Date: 2025-03-06 04:19:06.722909

"""

import base64, uuid, os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "59fbac3b744e"
down_revision: Union[str, None] = "0819cfc5e56c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_workflow_directory_prefix = "studio-data/workflows"


def create_slug_from_name(name: str) -> str:
    """
    Create a slug from a name.
    """
    return (
        name.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(":", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(".", "_")
    )


def get_random_compact_string() -> str:
    """
    Generate a random 8-character string.
    """
    try:
        return (
            base64.urlsafe_b64encode(uuid.uuid4().bytes)[:8]
            .decode()
            .replace("_", "")
            .replace("-", "")
            .replace("=", "")[:8]
        )
    except Exception as e:
        raise RuntimeError(f"Failed to generate random string: {str(e)}") from e


def upgrade() -> None:
    try:
        op.execute("ALTER TABLE workflows ADD COLUMN directory VARCHAR NOT NULL DEFAULT ''")
    except Exception as e:  # sqlite does not have "IF NOT EXISTS"
        print(f"Error adding directory column: {str(e)}")
        print("This is expected if the column already exists")
        return

    workflows = sa.table(
        "workflows", sa.Column("id", sa.String), sa.Column("name", sa.String), sa.Column("directory", sa.String)
    )

    connection = op.get_bind()
    existing_workflows = connection.execute(sa.select(workflows.c.id, workflows.c.name)).fetchall()

    for workflow_id, workflow_name in existing_workflows:
        workflow_basedir = create_slug_from_name(workflow_name) + "_" + get_random_compact_string()
        workflow_directory = f"{_workflow_directory_prefix}/{workflow_basedir}"
        os.makedirs(workflow_directory, exist_ok=True)
        connection.execute(workflows.update().where(workflows.c.id == workflow_id).values(directory=workflow_directory))


def downgrade() -> None:
    op.drop_column("workflows", "directory")
