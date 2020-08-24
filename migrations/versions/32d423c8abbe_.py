"""empty message

Revision ID: 32d423c8abbe
Revises: cfc8c12e45e3
Create Date: 2020-08-24 15:32:00.758205

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '32d423c8abbe'
down_revision = 'cfc8c12e45e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('available', sa.Boolean(), nullable=True))
    op.alter_column('user_subjects', 'user_selected',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_subjects', 'user_selected',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.drop_column('user', 'available')
    # ### end Alembic commands ###