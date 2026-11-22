"""limit each user to one team

Revision ID: 7a9c1d2e4f60
Revises: 38c1a7b2d9e4
Create Date: 2026-11-19 15:30:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "7a9c1d2e4f60"
down_revision: Union[str, None] = "38c1a7b2d9e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("team_members") as batch_op:
        batch_op.drop_constraint("uq_team_member", type_="unique")
        batch_op.create_unique_constraint(
            "uq_team_member_user", ["user_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("team_members") as batch_op:
        batch_op.drop_constraint("uq_team_member_user", type_="unique")
        batch_op.create_unique_constraint(
            "uq_team_member", ["team_id", "user_id"]
        )
