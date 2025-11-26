"""create tags table

Revision ID: 104
Revises: 
Create Date: 2025-11-18 12:49:59.787245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4f2cfea67fd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tags', sa.Column('type_', sa.String(length=50), nullable=True))
    op.execute("UPDATE tags SET type_ = 'default' WHERE type_ IS NULL")
    op.alter_column('tags', 'type_', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tags', 'type_')
