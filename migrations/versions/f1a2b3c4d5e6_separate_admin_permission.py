"""separate admin permission from participant role

Revision ID: f1a2b3c4d5e6
Revises: d8e1f2a3b4c5
Create Date: 2026-11-26 11:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "d8e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index("ix_users_is_admin", "users", ["is_admin"], unique=False)

    if op.get_bind().dialect.name == "postgresql":
        op.execute("UPDATE users SET is_admin = TRUE WHERE role::text = 'ADMIN'")
        op.execute("UPDATE users SET role = 'STUDENT' WHERE role::text = 'ADMIN'")
        op.execute("ALTER TYPE userrole RENAME TO userrole_legacy")
        op.execute("CREATE TYPE userrole AS ENUM ('STUDENT', 'LEADER')")
        op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
        op.execute(
            """
            ALTER TABLE users
            ALTER COLUMN role TYPE userrole
            USING role::text::userrole
            """
        )
        op.execute("DROP TYPE userrole_legacy")
    else:
        op.execute(
            sa.text("UPDATE users SET is_admin = TRUE WHERE role = 'ADMIN'")
        )
        op.execute(
            sa.text("UPDATE users SET role = 'STUDENT' WHERE role = 'ADMIN'")
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE userrole RENAME TO userrole_legacy")
        op.execute(
            "CREATE TYPE userrole AS ENUM "
            "('STUDENT', 'LEADER', 'ADMIN')"
        )
        op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
        op.execute(
            """
            ALTER TABLE users
            ALTER COLUMN role TYPE userrole
            USING (
                CASE
                    WHEN is_admin THEN 'ADMIN'
                    ELSE role::text
                END
            )::userrole
            """
        )
        op.execute("DROP TYPE userrole_legacy")
    else:
        op.execute(
            sa.text("UPDATE users SET role = 'ADMIN' WHERE is_admin = 1")
        )

    op.drop_index("ix_users_is_admin", table_name="users")
    op.drop_column("users", "is_admin")
