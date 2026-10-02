from datetime import datetime
from typing import TYPE_CHECKING


from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.utils.datetime_utils import utc_now


if TYPE_CHECKING:
    from app.models.user import User



class AuditLog(db.Model):

    __tablename__ = "audit_logs"


    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        db.String(50),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(
        db.String(50),
        nullable=False,
    )

    entity_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        db.String(500),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=utc_now,
        nullable=False,
    )

    user: Mapped["User | None"] = relationship(
        back_populates="audit_logs",
    )

    def __repr__(self):
        return (
            f"<Auditlog "
            f"{self.action} "
            f"{self.entity_type} "
            f"{self.entity_id}>"
        )