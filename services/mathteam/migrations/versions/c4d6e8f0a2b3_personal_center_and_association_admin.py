"""add personal profile fields, resume storage and association admin

Revision ID: c4d6e8f0a2b3
Revises: b3f2a4c6d8e0
Create Date: 2026-11-20 14:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c4d6e8f0a2b3"
down_revision: Union[str, None] = "b3f2a4c6d8e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ASSOCIATION_ADMIN'"
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("student_number", sa.String(40)))
        batch_op.add_column(sa.Column("college", sa.String(100)))
        batch_op.add_column(sa.Column("phone", sa.String(30)))
        batch_op.add_column(sa.Column("qq", sa.String(30)))
        batch_op.add_column(sa.Column("wechat", sa.String(100)))
        batch_op.add_column(sa.Column("github", sa.String(100)))
        batch_op.add_column(sa.Column("resume_key", sa.String(255)))
        batch_op.add_column(sa.Column("resume_name", sa.String(255)))
        batch_op.add_column(sa.Column("resume_mime", sa.String(120)))
        batch_op.add_column(sa.Column("resume_size", sa.Integer()))
        batch_op.add_column(sa.Column("resume_uploaded_at", sa.DateTime()))
        batch_op.create_index(
            "ix_users_student_number", ["student_number"]
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index("ix_users_student_number")
        batch_op.drop_column("resume_uploaded_at")
        batch_op.drop_column("resume_size")
        batch_op.drop_column("resume_mime")
        batch_op.drop_column("resume_name")
        batch_op.drop_column("resume_key")
        batch_op.drop_column("github")
        batch_op.drop_column("wechat")
        batch_op.drop_column("qq")
        batch_op.drop_column("phone")
        batch_op.drop_column("college")
        batch_op.drop_column("student_number")
    # PostgreSQL 原生枚举值无法安全回滚删除；旧版本代码会忽略该多余标签。
