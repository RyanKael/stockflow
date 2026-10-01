from datetime import datetime
from enum import Enum

from typing import TYPE_CHECKING
from flask_login import UserMixin
from sqlalchemy import Enum as SqlEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

if TYPE_CHECKING:

    from app.models.stock_movement import StockMovement
    from app.models.audit_log import AuditLog

class UserRole(Enum):
    ADMIN = "Administrador"
    MANAGER = "Gerente"
    USER = "Usuário"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole),
        nullable=False,
        default=UserRole.USER,
    )

    active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    stock_movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="user",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
    )

    @property
    def is_active(self) -> bool:
        return self.active

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)


    def check_password(self, password: str) -> bool:
        return check_password_hash(
            self.password_hash,
            password,
        )