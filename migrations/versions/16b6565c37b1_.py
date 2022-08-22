"""empty message

Revision ID: 16b6565c37b1
Revises: 269ebac87a3c
Create Date: 2022-08-22 05:02:57.691395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16b6565c37b1'
down_revision = '269ebac87a3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist-items',
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('show_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['show_id'], ['Show.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'show_id')
    )
    op.create_table('venue-items',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('show_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['show_id'], ['Show.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'show_id')
    )
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'])
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_table('venue-items')
    op.drop_table('artist-items')
    # ### end Alembic commands ###