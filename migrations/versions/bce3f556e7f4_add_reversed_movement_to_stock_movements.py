"""Add reversed movement to stock movements

Revision ID: bce3f556e7f4
Revises: b84c8174c0c4
Create Date: 2026-08-16 22:46:57.350762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bce3f556e7f4'
down_revision = 'b84c8174c0c4'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        "stock_movements",
        schema=None,
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "reversed_movement_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_foreign_key(
            "fk_stock_movements_reversed_movement",
            "stock_movements",
            ["reversed_movement_id"],
            ["id"],
        )


def downgrade():

    with op.batch_alter_table(
        "stock_movements",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_stock_movements_reversed_movement",
            type_="foreignkey",
        )

        batch_op.drop_column(
            "reversed_movement_id"
        )