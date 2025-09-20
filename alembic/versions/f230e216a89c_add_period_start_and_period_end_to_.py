"""add period_start and period_end to invoices

Revision ID: f230e216a89c
Revises: b5ac236dbd93
Create Date: 2025-09-19 22:20:28.904557

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f230e216a89c"
down_revision: Union[str, Sequence[str], None] = "b5ac236dbd93"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "fastapi_racuni", sa.Column("period_start", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "fastapi_racuni",
        sa.Column("period_end", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
