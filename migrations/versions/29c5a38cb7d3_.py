"""empty message

Revision ID: 29c5a38cb7d3
Revises: 4575207e2d8c
Create Date: 2020-10-07 15:36:00.905931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29c5a38cb7d3'
down_revision = '4575207e2d8c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.alter_column('comment', 'pinned',
    #            existing_type=sa.BOOLEAN(),
    #            nullable=False)
    op.add_column('project', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'project', 'company', ['company_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'project', type_='foreignkey')
    op.drop_column('project', 'company_id')
    op.alter_column('comment', 'pinned',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
