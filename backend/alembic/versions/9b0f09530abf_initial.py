"""initial

Revision ID: 9b0f09530abf
Revises: 
Create Date: 2026-09-29 00:18:39.799118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b0f09530abf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'complaints',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('text', sa.String(length=2000), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=False),
        sa.Column('reporter_contact', sa.String(length=200), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('ai_summary', sa.String(length=140), nullable=True),
        sa.Column('triaged_by', sa.String(length=50), nullable=False),
        sa.Column('triage_latency_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_complaints_created_at', 'complaints', ['created_at'], unique=False)
    op.create_index('ix_complaints_status_priority', 'complaints', ['status', 'priority'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_complaints_status_priority', table_name='complaints')
    op.drop_index('ix_complaints_created_at', table_name='complaints')
    op.drop_table('complaints')
