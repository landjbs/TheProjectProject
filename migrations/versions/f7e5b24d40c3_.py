"""empty message

Revision ID: f7e5b24d40c3
Revises: ba26b28a5304
Create Date: 2020-08-10 13:07:43.212285

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7e5b24d40c3'
down_revision = 'ba26b28a5304'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('badge_to_perk',
    sa.Column('badge_id', sa.Integer(), nullable=True),
    sa.Column('perk_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['badge_id'], ['badge.id'], ),
    sa.ForeignKeyConstraint(['perk_id'], ['badge_perk.id'], )
    )
    op.drop_column('badge', 'icon')
    op.drop_constraint(None, 'badge_perk', type_='foreignkey')
    op.drop_column('badge_perk', 'badge_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('badge_perk', sa.Column('badge_id', sa.INTEGER(), nullable=True))
    op.create_foreign_key(None, 'badge_perk', 'badge', ['badge_id'], ['id'])
    op.add_column('badge', sa.Column('icon', sa.VARCHAR(length=250), nullable=False))
    op.drop_table('badge_to_perk')
    # ### end Alembic commands ###
