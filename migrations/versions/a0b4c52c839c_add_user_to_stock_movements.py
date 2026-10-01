"""Add user to stock movements

Revision ID: a0b4c52c839c
Revises: 2953e86fff7f
Create Date: 2026-08-28 17:24:40.079003
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a0b4c52c839c"
down_revision = "2953e86fff7f"
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona user_id temporariamente como opcional,
    # pois já existem movimentações no banco.
    with op.batch_alter_table(
        "stock_movements",
        schema=None,
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_foreign_key(
            "fk_stock_movements_user_id_users",
            "users",
            ["user_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table(
        "stock_movements",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_stock_movements_user_id_users",
            type_="foreignkey",
        )

        batch_op.drop_column("user_id")