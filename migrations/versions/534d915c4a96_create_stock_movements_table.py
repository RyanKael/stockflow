"""Create stock movements table

Revision ID: 534d915c4a96
Revises: 4251b9c6cbbe
Create Date: 2026-08-08 14:04:20.360577

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "534d915c4a96"
down_revision = "4251b9c6cbbe"
branch_labels = None
depends_on = None


def upgrade():

    movement_type_enum = sa.Enum(
        "ENTRY",
        "EXIT",
        "ADJUSTMENT",
        name="movementtype",
    )

    op.create_table(
        "stock_movements",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "movement_type",
            movement_type_enum,
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "reason",
            sa.String(length=250),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )


def downgrade():

    op.drop_table(
        "stock_movements"
    )

    movement_type_enum = sa.Enum(
        "ENTRY",
        "EXIT",
        "ADJUSTMENT",
        name="movementtype",
    )

    movement_type_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )
