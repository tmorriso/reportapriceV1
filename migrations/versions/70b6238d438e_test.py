"""test

Revision ID: 70b6238d438e
Revises: 089a23bebdb5
Create Date: 2018-08-04 21:59:58.393388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70b6238d438e'
down_revision = '089a23bebdb5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'review')
    op.drop_column('post', 'service')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('service', sa.VARCHAR(length=140), nullable=True))
    op.add_column('post', sa.Column('review', sa.VARCHAR(length=280), nullable=True))
    # ### end Alembic commands ###
