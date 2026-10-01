from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

if TYPE_CHECKING:
    from app.models.product import Product


class Category(db.Model):

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
    )

    def __repr__(self):
        return f"<Category {self.name}>"