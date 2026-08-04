from sqlalchemy import Boolean, DateTime, Integer, String, Text
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column


from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

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
        default = datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        default = datetime.utcnow,
        onupdate = datetime.utcnow,
    )