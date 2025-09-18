"""create spot_accuracy_rating table

Revision ID: spot_accuracy_rating_20250918
Revises: 
Create Date: 2025-09-18

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'spot_accuracy_rating_20250918'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    spot_rating_enum = sa.Enum('accurate', 'not_accurate', name='spot_rating_enum')
    spot_rating_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        'spot_accuracy_rating',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('spot_id', sa.Integer, nullable=False),
        sa.Column('spot_slug', sa.String(length=128), nullable=False),
        sa.Column('rating', spot_rating_enum, nullable=False),
        sa.Column('forecast_json', sa.JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('session_id', sa.String(length=128), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_id', sa.Integer, nullable=True),
        sa.ForeignKeyConstraint(['spot_id'], ['spots.id'], name='fk_spot_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_id'),
        sa.UniqueConstraint('spot_id', 'session_id', 'ip_address', 'timestamp', name='uq_spot_session_ip_date')
    )

def downgrade():
    op.drop_table('spot_accuracy_rating')
    spot_rating_enum = sa.Enum('accurate', 'not_accurate', name='spot_rating_enum')
    spot_rating_enum.drop(op.get_bind(), checkfirst=True)
