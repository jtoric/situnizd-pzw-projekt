"""rename user email to username, add is_active

Revision ID: 002
Revises: 001
Create Date: 2026-10-06 14:30:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # autogenerate je ovdje predložio drop_column("email") + add_column("username"),
    # što bi obrisalo sve postojeće vrijednosti. Preimenovanje čuva podatke.
    op.alter_column("users", "email", new_column_name="username")
    op.execute(
        "ALTER TABLE users RENAME CONSTRAINT users_email_key TO users_username_key"
    )
    # server_default popunjava postojeće retke, pa NOT NULL prolazi
    op.add_column(
        "users",
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_active")
    op.execute(
        "ALTER TABLE users RENAME CONSTRAINT users_username_key TO users_email_key"
    )
    op.alter_column("users", "username", new_column_name="email")
