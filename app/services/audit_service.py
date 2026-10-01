from app.extensions import db
from app.models.audit_log import AuditLog


def register_audit(
        *,
        user_id,
        action,
        entity_type,
        entity_id=None,
        description,

):

    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )

    db.session.add(log)

    return log