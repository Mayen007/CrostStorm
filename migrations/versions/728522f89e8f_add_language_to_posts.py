"""add language to posts

Revision ID: 728522f89e8f
Revises: 9056bc0fc955
Create Date: 2023-11-14 11:19:32.515224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '728522f89e8f'
down_revision = '9056bc0fc955'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('language', sa.String(length=5), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('language')

    # ### end Alembic commands ###