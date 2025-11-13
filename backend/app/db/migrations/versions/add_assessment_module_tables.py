"""add_assessment_module_tables

Revision ID: f1a2b3c4d5e6
Revises: ebb9e18786d5
Create Date: 2025-10-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'ebb9e18786d5'
branch_labels = None
depends_on = None


def upgrade():
    # Create assessment_sessions table
    op.create_table('assessment_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('current_module', sa.String(length=100), nullable=True),
        sa.Column('module_history', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=False),
        sa.Column('session_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('idx_assessment_sessions_patient', 'assessment_sessions', ['patient_id'], unique=False)
    op.create_index('idx_assessment_sessions_patient_active', 'assessment_sessions', ['patient_id', 'is_complete'], unique=False)
    op.create_index('idx_assessment_sessions_session_id', 'assessment_sessions', ['session_id'], unique=False)
    op.create_index('idx_assessment_sessions_updated', 'assessment_sessions', ['updated_at'], unique=False)
    op.create_index('idx_assessment_sessions_user', 'assessment_sessions', ['user_id'], unique=False)
    op.create_index('idx_assessment_sessions_complete', 'assessment_sessions', ['is_complete'], unique=False)

    # Create assessment_module_states table
    op.create_table('assessment_module_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('module_name', sa.String(length=100), nullable=False),
        sa.Column('state_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at_time', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['assessment_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_module_states_patient', 'assessment_module_states', ['patient_id'], unique=False)
    op.create_index('idx_module_states_session', 'assessment_module_states', ['session_id'], unique=False)
    op.create_index('idx_module_states_session_module', 'assessment_module_states', ['session_id', 'module_name'], unique=True)
    op.create_index('idx_module_states_updated', 'assessment_module_states', ['updated_at_time'], unique=False)
    op.create_index('idx_module_states_module', 'assessment_module_states', ['module_name'], unique=False)

    # Create assessment_module_results table
    op.create_table('assessment_module_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('module_name', sa.String(length=100), nullable=False),
        sa.Column('results_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('completed_at_time', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['assessment_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_module_results_completed', 'assessment_module_results', ['completed_at_time'], unique=False)
    op.create_index('idx_module_results_patient', 'assessment_module_results', ['patient_id'], unique=False)
    op.create_index('idx_module_results_patient_module', 'assessment_module_results', ['patient_id', 'module_name'], unique=False)
    op.create_index('idx_module_results_session', 'assessment_module_results', ['session_id'], unique=False)
    op.create_index('idx_module_results_session_module', 'assessment_module_results', ['session_id', 'module_name'], unique=True)

    # Create assessment_conversations table
    op.create_table('assessment_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('module_name', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('message_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_conversation_role'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['assessment_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_module', 'assessment_conversations', ['module_name'], unique=False)
    op.create_index('idx_conversations_patient', 'assessment_conversations', ['patient_id'], unique=False)
    op.create_index('idx_conversations_patient_timestamp', 'assessment_conversations', ['patient_id', 'timestamp'], unique=False)
    op.create_index('idx_conversations_session_timestamp', 'assessment_conversations', ['session_id', 'timestamp'], unique=False)
    op.create_index('idx_conversations_timestamp', 'assessment_conversations', ['timestamp'], unique=False)
    op.create_index('idx_conversations_role', 'assessment_conversations', ['role'], unique=False)

    # Create assessment_module_transitions table
    op.create_table('assessment_module_transitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_module', sa.String(length=100), nullable=True),
        sa.Column('to_module', sa.String(length=100), nullable=False),
        sa.Column('transitioned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('transition_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['assessment_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_transitions_modules', 'assessment_module_transitions', ['from_module', 'to_module'], unique=False)
    op.create_index('idx_transitions_patient', 'assessment_module_transitions', ['patient_id'], unique=False)
    op.create_index('idx_transitions_session', 'assessment_module_transitions', ['session_id'], unique=False)
    op.create_index('idx_transitions_timestamp', 'assessment_module_transitions', ['transitioned_at'], unique=False)

    # Create assessment_demographics table
    op.create_table('assessment_demographics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=50), nullable=True),
        sa.Column('education_level', sa.String(length=100), nullable=True),
        sa.Column('occupation', sa.String(length=100), nullable=True),
        sa.Column('marital_status', sa.String(length=50), nullable=True),
        sa.Column('cultural_background', sa.String(length=200), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('family_psychiatric_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('living_situation', sa.String(length=50), nullable=True),
        sa.Column('financial_status', sa.String(length=50), nullable=True),
        sa.Column('recent_stressors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at_demographics', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('age >= 18 AND age <= 120'),
        sa.CheckConstraint("gender IN ('Male', 'Female', 'Non-binary', 'Prefer not to say')"),
        sa.CheckConstraint("education_level IN ('No formal education', 'Primary school', 'High school', 'Bachelor''s degree', 'Master''s degree', 'Doctorate')"),
        sa.CheckConstraint("occupation IN ('Student', 'Employed full-time', 'Employed part-time', 'Self-employed', 'Unemployed', 'Retired')"),
        sa.CheckConstraint("marital_status IN ('Single', 'Married', 'Divorced', 'Widowed', 'Separated')"),
        sa.CheckConstraint("living_situation IN ('alone', 'with_family', 'with_partner', 'shared', 'institutionalized')"),
        sa.CheckConstraint("financial_status IN ('stable', 'moderate', 'unstable')"),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['assessment_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('patient_id')
    )
    op.create_index('idx_demographics_collected', 'assessment_demographics', ['collected_at'], unique=False)
    op.create_index('idx_demographics_patient', 'assessment_demographics', ['patient_id'], unique=False)
    op.create_index('idx_demographics_session', 'assessment_demographics', ['session_id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index('idx_demographics_session', table_name='assessment_demographics')
    op.drop_index('idx_demographics_patient', table_name='assessment_demographics')
    op.drop_index('idx_demographics_collected', table_name='assessment_demographics')
    op.drop_table('assessment_demographics')
    
    op.drop_index('idx_transitions_timestamp', table_name='assessment_module_transitions')
    op.drop_index('idx_transitions_session', table_name='assessment_module_transitions')
    op.drop_index('idx_transitions_patient', table_name='assessment_module_transitions')
    op.drop_index('idx_transitions_modules', table_name='assessment_module_transitions')
    op.drop_table('assessment_module_transitions')
    
    op.drop_index('idx_conversations_role', table_name='assessment_conversations')
    op.drop_index('idx_conversations_timestamp', table_name='assessment_conversations')
    op.drop_index('idx_conversations_session_timestamp', table_name='assessment_conversations')
    op.drop_index('idx_conversations_patient_timestamp', table_name='assessment_conversations')
    op.drop_index('idx_conversations_patient', table_name='assessment_conversations')
    op.drop_index('idx_conversations_module', table_name='assessment_conversations')
    op.drop_table('assessment_conversations')
    
    op.drop_index('idx_module_results_session_module', table_name='assessment_module_results')
    op.drop_index('idx_module_results_session', table_name='assessment_module_results')
    op.drop_index('idx_module_results_patient_module', table_name='assessment_module_results')
    op.drop_index('idx_module_results_patient', table_name='assessment_module_results')
    op.drop_index('idx_module_results_completed', table_name='assessment_module_results')
    op.drop_table('assessment_module_results')
    
    op.drop_index('idx_module_states_module', table_name='assessment_module_states')
    op.drop_index('idx_module_states_updated', table_name='assessment_module_states')
    op.drop_index('idx_module_states_session_module', table_name='assessment_module_states')
    op.drop_index('idx_module_states_session', table_name='assessment_module_states')
    op.drop_index('idx_module_states_patient', table_name='assessment_module_states')
    op.drop_table('assessment_module_states')
    
    op.drop_index('idx_assessment_sessions_complete', table_name='assessment_sessions')
    op.drop_index('idx_assessment_sessions_user', table_name='assessment_sessions')
    op.drop_index('idx_assessment_sessions_updated', table_name='assessment_sessions')
    op.drop_index('idx_assessment_sessions_session_id', table_name='assessment_sessions')
    op.drop_index('idx_assessment_sessions_patient_active', table_name='assessment_sessions')
    op.drop_index('idx_assessment_sessions_patient', table_name='assessment_sessions')
    op.drop_table('assessment_sessions')

