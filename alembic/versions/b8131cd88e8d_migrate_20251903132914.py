"""migrate-20251903132914

Revision ID: b8131cd88e8d
Revises: 3ab53535ced8
Create Date: 2025-03-19 13:29:14.978456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8131cd88e8d'
down_revision: Union[str, None] = '3ab53535ced8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('certificate', sa.Column('archived', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('certificate', 'archived')
    # ### end Alembic commands ###
