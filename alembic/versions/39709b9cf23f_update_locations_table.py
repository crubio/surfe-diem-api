"""update locations table

Revision ID: 39709b9cf23f
Revises: 870b21f91b3d
Create Date: 2023-06-01 12:03:24.900049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39709b9cf23f'
down_revision = '870b21f91b3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('locations', sa.Column('description', sa.String(), server_default=None, nullable=True))
    op.add_column('locations', sa.Column('elevation', sa.String(), server_default=None, nullable=True))
    op.add_column('locations', sa.Column('depth', sa.String(), server_default=None, nullable=True))
    op.add_column('locations', sa.Column('location', sa.String(), server_default=None, nullable=True))


def downgrade() -> None:
    op.drop_column('locations', 'description')
    op.drop_column('locations', 'elevation')
    op.drop_column('locations', 'depth')
    op.drop_column('locations', 'location')
