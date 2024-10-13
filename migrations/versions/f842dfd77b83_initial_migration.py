"""Initial migration.

Revision ID: f842dfd77b83
Revises: f81edbe94976
Create Date: 2024-10-12 18:09:14.855479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f842dfd77b83'
down_revision = 'f81edbe94976'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('portfolio_view', schema=None) as batch_op:
        batch_op.create_unique_constraint('_user_ticker_uc', ['user_id', 'ticker'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cash_balance', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('cash_balance')

    with op.batch_alter_table('portfolio_view', schema=None) as batch_op:
        batch_op.drop_constraint('_user_ticker_uc', type_='unique')

    # ### end Alembic commands ###
