"""empty message

Revision ID: efbf8a380eea
Revises: aca5d8cf752b
Create Date: 2020-08-20 13:34:52.327911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efbf8a380eea'
down_revision = 'aca5d8cf752b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('competition_to_project')
    op.add_column('notification', sa.Column('name', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notification', 'name')
    op.create_table('competition_to_project',
    sa.Column('competition_id', sa.INTEGER(), nullable=True),
    sa.Column('project_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['competition_id'], ['competition.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], )
    )
    # ### end Alembic commands ###
