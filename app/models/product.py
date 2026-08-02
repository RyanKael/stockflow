from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(120), 
        nullable=False
    )