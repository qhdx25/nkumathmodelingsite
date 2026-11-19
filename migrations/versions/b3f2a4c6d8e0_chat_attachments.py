"""add temporary chat attachment metadata

Revision ID: b3f2a4c6d8e0
Revises: 7a9c1d2e4f60
Create Date: 2026-11-20 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b3f2a4c6d8e0"
down_revision: Union[str, None] = "7a9c1d2e4f60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("messages") as batch_op:
        batch_op.add_column(sa.Column("attachment_key", sa.String(255)))
        batch_op.add_column(sa.Column("attachment_name", sa.String(255)))
        batch_op.add_column(sa.Column("attachment_mime", sa.String(120)))
        batch_op.add_column(sa.Column("attachment_size", sa.BigInteger()))
        batch_op.add_column(sa.Column("attachment_kind", sa.String(16)))
        batch_op.add_column(sa.Column("attachment_expires_at", sa.DateTime()))
        batch_op.create_index(
            "ix_messages_attachment_key", ["attachment_key"]
        )
        batch_op.create_index(
            "ix_messages_attachment_expires_at",
            ["attachment_expires_at"],
        )


def downgrade() -> None:
    with op.batch_alter_table("messages") as batch_op:
        batch_op.drop_index("ix_messages_attachment_expires_at")
        batch_op.drop_index("ix_messages_attachment_key")
        batch_op.drop_column("attachment_expires_at")
        batch_op.drop_column("attachment_kind")
        batch_op.drop_column("attachment_size")
        batch_op.drop_column("attachment_mime")
        batch_op.drop_column("attachment_name")
        batch_op.drop_column("attachment_key")
