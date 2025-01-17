"""Add email column to users table

Revision ID: 8f131c02bfb8
Revises:
Create Date: 2025-01-18 00:57:11.071944

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f131c02bfb8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add the email column as nullable
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))

    # Step 2: Populate the email column with placeholder values
    op.execute("UPDATE users SET email = 'placeholder@example.com' WHERE email IS NULL")

    # Step 3: Alter the column to make it NOT NULL
    op.alter_column("users", "email", nullable=False)

    # Allow 'phone_number' to be nullable as per your original script
    op.alter_column("users", "phone_number", existing_type=sa.VARCHAR(), nullable=True)

    # Add a unique constraint on the 'email' column
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    # Reverse the changes
    op.drop_constraint(None, "users", type_="unique")
    op.alter_column("users", "phone_number", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column("users", "email")
