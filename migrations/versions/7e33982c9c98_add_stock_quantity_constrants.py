"""Add stock quantity constrants

Revision ID: 7e33982c9c98
Revises: bce3f556e7f4
Create Date: 2026-08-19 17:03:13.696144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e33982c9c98'
down_revision = 'bce3f556e7f4'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        "products",
        schema=None,
    ) as batch_op:

        batch_op.create_check_constraint(
            "ck_products_quantity_non_negative",
            "quantity >= 0",
        )

        batch_op.create_check_constraint(
            "ck_products_minimum_stock_non_negative",
            "minimum_stock >= 0",
        )


def downgrade():

    with op.batch_alter_table(
        "products",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "ck_products_minimum_stock_non_negative",
            type_="check",
        )

        batch_op.drop_constraint(
            "ck_products_quantity_non_negative",
            type_="check",
        )