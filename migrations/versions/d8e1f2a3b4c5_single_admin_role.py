"""consolidate administrator roles

Revision ID: d8e1f2a3b4c5
Revises: c4d6e8f0a2b3
Create Date: 2026-11-26 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d8e1f2a3b4c5"
down_revision: Union[str, None] = "c4d6e8f0a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LEGACY_ADMIN_ROLES = (
    "'ASSOCIATION_ADMIN', 'SCHOOL_ADMIN', 'PLATFORM_ADMIN'"
)


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE userrole RENAME TO userrole_legacy")
        op.execute("CREATE TYPE userrole AS ENUM ('STUDENT', 'LEADER', 'ADMIN')")
        op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
        op.execute(
            f"""
            ALTER TABLE users
            ALTER COLUMN role TYPE userrole
            USING (
                CASE
                    WHEN role::text IN ({LEGACY_ADMIN_ROLES}) THEN 'ADMIN'
                    ELSE role::text
                END
            )::userrole
            """
        )
        op.execute("DROP TYPE userrole_legacy")
    else:
        op.execute(
            sa.text(
                "UPDATE users SET role = 'ADMIN' "
                "WHERE role IN ('ASSOCIATION_ADMIN', 'SCHOOL_ADMIN', "
                "'PLATFORM_ADMIN')"
            )
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE userrole RENAME TO userrole_legacy")
        op.execute(
            "CREATE TYPE userrole AS ENUM "
            "('STUDENT', 'LEADER', 'ASSOCIATION_ADMIN', "
            "'SCHOOL_ADMIN', 'PLATFORM_ADMIN')"
        )
        op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
        op.execute(
            """
            ALTER TABLE users
            ALTER COLUMN role TYPE userrole
            USING (
                CASE
                    WHEN role::text = 'ADMIN' THEN 'PLATFORM_ADMIN'
                    ELSE role::text
                END
            )::userrole
            """
        )
        op.execute("DROP TYPE userrole_legacy")
    else:
        op.execute("UPDATE users SET role = 'PLATFORM_ADMIN' WHERE role = 'ADMIN'")
