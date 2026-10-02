from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, Text
from sqlalchemy import ForeignKey

from app.extensions import db
from app.utils.datetime_utils import utc_now

if TYPE_CHECKING:
    from app.models.stock_movement import StockMovement
    from app.models.category import Category


class Product(db.Model):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "quantity >= 0",
            name="ck_products_quantity_non_negative",
        ),
        CheckConstraint(
            "minimum_stock >= 0",
            name="ck_products_minimum_stock_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key = True)

    code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    quantity: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    minimum_stock: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(80),
    )

    active: Mapped[bool] = mapped_column(
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        default = utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        default = utc_now,
        onupdate = utc_now,
    )

    movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )

    category: Mapped["Category | None"] = relationship(
        back_populates="products",
    )