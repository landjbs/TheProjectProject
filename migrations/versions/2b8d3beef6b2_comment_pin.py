"""comment pin

Revision ID: 2b8d3beef6b2
Revises: 707bb9b6c53c
Create Date: 2020-09-30 17:08:33.489860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b8d3beef6b2'
down_revision = '707bb9b6c53c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('pinned', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comment', 'pinned')
    # ### end Alembic commands ###
