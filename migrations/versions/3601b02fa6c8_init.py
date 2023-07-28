"""'Init'

Revision ID: 3601b02fa6c8
Revises: 
Create Date: 2023-07-28 11:24:18.031083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3601b02fa6c8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contacts', 'name',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    op.alter_column('contacts', 'surname',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    op.alter_column('contacts', 'phone',
               existing_type=sa.VARCHAR(length=16),
               nullable=False)
    op.alter_column('contacts', 'email',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    op.alter_column('contacts', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('users', 'name',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    op.alter_column('users', 'surname',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    op.alter_column('users', 'phone',
               existing_type=sa.VARCHAR(length=16),
               nullable=False)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
    op.alter_column('users', 'phone',
               existing_type=sa.VARCHAR(length=16),
               nullable=True)
    op.alter_column('users', 'surname',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
    op.alter_column('users', 'name',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
    op.alter_column('contacts', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('contacts', 'email',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
    op.alter_column('contacts', 'phone',
               existing_type=sa.VARCHAR(length=16),
               nullable=True)
    op.alter_column('contacts', 'surname',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
    op.alter_column('contacts', 'name',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
    # ### end Alembic commands ###
