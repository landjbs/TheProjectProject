"""empty message

Revision ID: e8ffbd72bbe1
Revises: e3b3a1ea419b
Create Date: 2020-08-10 09:38:00.930274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8ffbd72bbe1'
down_revision = 'e3b3a1ea419b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_badge', 'badge_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('user_badge', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_badge', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('user_badge', 'badge_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
