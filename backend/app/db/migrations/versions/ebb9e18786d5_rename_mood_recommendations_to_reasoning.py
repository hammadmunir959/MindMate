"""Rename mood recommendations to reasoning

Revision ID: ebb9e18786d5
Revises: e6a3125ec3eb
Create Date: 2025-10-14 09:01:30.329818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebb9e18786d5'
down_revision: Union[str, None] = 'e6a3125ec3eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Rename recommendations to reasoning in mood_assessments."""
    # Rename column from recommendations to reasoning
    op.alter_column('mood_assessments', 'recommendations',
                   new_column_name='reasoning',
                   existing_type=sa.Text(),
                   existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema - Rename reasoning back to recommendations."""
    # Rename column back from reasoning to recommendations
    op.alter_column('mood_assessments', 'reasoning',
                   new_column_name='recommendations',
                   existing_type=sa.Text(),
                   existing_nullable=True)
