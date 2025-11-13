"""add_approval_timeline_and_status_columns

Revision ID: add_approval_timeline
Revises: ecba55ec568f
Create Date: 2025-11-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = 'add_approval_timeline'
down_revision: Union[str, Sequence[str], None] = ('ecba55ec568f', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing columns to specialists_approval_data table
    op.add_column('specialists_approval_data', 
                  sa.Column('document_verification_status', sa.String(20), 
                           nullable=True, server_default='pending',
                           comment='Status of document verification'))
    
    op.add_column('specialists_approval_data', 
                  sa.Column('compliance_check_status', sa.String(20), 
                           nullable=True, server_default='pending',
                           comment='Status of compliance check'))
    
    op.add_column('specialists_approval_data', 
                  sa.Column('approval_timeline', JSON, 
                           nullable=True,
                           comment='Timeline of approval process: {profile_completion: timestamp, ...}'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the added columns from specialists_approval_data table
    op.drop_column('specialists_approval_data', 'approval_timeline')
    op.drop_column('specialists_approval_data', 'compliance_check_status')
    op.drop_column('specialists_approval_data', 'document_verification_status')

