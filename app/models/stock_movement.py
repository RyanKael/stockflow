from datetime import datetime


from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.utils.datetime_utils import utc_now


if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class MovementType(Enum):
    ENTRY = "Entrada"
    EXIT = "Saída"
    ADJUSTMENT = "Ajuste"


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    reversed_movement_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_movements.id"),
        nullable=True,
    )

    reversed_movement: Mapped["StockMovement | None"] = relationship(
        "StockMovement",
        remote_side="StockMovement.id",
        backref=db.backref(
            "reverse",
            uselist=False,
        ),
    )

    product: Mapped["Product"] = relationship(
        back_populates="movements"
    )

    user: Mapped["User"] = relationship(
        back_populates="stock_movements",
    )

    movement_type: Mapped[MovementType] = mapped_column(
        SqlEnum(MovementType),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False,
    )

    previous_quantity: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        String(250),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
    )