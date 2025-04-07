"""Add STUDENT role to RoleType enum

Revision ID: 5d48cba98122
Revises: 74637546ccca
Create Date: 2025-04-07 17:17:25.777252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d48cba98122'
down_revision: Union[str, None] = '74637546ccca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users MODIFY COLUMN role ENUM('USER', 'ADMIN', 'SUPER_ADMIN', 'STUDENT') NOT NULL;"
    )

def downgrade() -> None:
    op.execute(
        "ALTER TABLE users MODIFY COLUMN role ENUM('USER', 'ADMIN', 'SUPER_ADMIN') NOT NULL;"
    )
