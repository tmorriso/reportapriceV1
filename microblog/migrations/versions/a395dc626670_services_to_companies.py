"""services to companies

Revision ID: a395dc626670
Revises: 6c5b9f7dbe0a
Create Date: 2018-08-06 00:03:25.153043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a395dc626670'
down_revision = '6c5b9f7dbe0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('companies_services',
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('companies_services')
    # ### end Alembic commands ###
