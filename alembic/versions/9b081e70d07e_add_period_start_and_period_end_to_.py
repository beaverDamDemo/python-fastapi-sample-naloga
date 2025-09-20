"""add period start and period end to racuni

Revision ID: 9b081e70d07e
Revises: f230e216a89c
Create Date: 2025-09-19 22:33:36.882851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b081e70d07e'
down_revision: Union[str, Sequence[str], None] = 'f230e216a89c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
