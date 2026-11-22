"""enforce unique team membership

Revision ID: 38c1a7b2d9e4
Revises: 8700d154da44
Create Date: 2026-11-19 14:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "38c1a7b2d9e4"
down_revision: Union[str, None] = "8700d154da44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("team_members") as batch_op:
        batch_op.create_unique_constraint(
            "uq_team_member", ["team_id", "user_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("team_members") as batch_op:
        batch_op.drop_constraint("uq_team_member", type_="unique")
