"""empty message

Revision ID: 988ae76da6b2
Revises: 
Create Date: 2020-08-09 12:29:05.711451

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '988ae76da6b2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('email', table_name='admin_user')
    op.drop_table('admin_user')
    op.add_column('badge', sa.Column('icon', sa.String(length=250), nullable=False))
    op.drop_index('color', table_name='badge')
    op.drop_index('icon_url', table_name='badge')
    op.create_unique_constraint(None, 'badge', ['icon'])
    op.drop_column('badge', 'icon_url')
    op.drop_column('badge', 'color')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('badge', sa.Column('color', mysql.VARCHAR(length=6), nullable=False))
    op.add_column('badge', sa.Column('icon_url', mysql.VARCHAR(length=250), nullable=False))
    op.drop_constraint(None, 'badge', type_='unique')
    op.create_index('icon_url', 'badge', ['icon_url'], unique=True)
    op.create_index('color', 'badge', ['color'], unique=True)
    op.drop_column('badge', 'icon')
    op.create_table('admin_user',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=128), nullable=True),
    sa.Column('email', mysql.VARCHAR(length=254), nullable=False),
    sa.Column('password', mysql.VARCHAR(length=254), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('email', 'admin_user', ['email'], unique=True)
    # ### end Alembic commands ###
