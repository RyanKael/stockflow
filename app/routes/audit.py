from datetime import datetime

from flask import Blueprint, render_template, request

from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.auth import role_required
from app.models.user import UserRole


audit = Blueprint(
    "audit",
    __name__,
    url_prefix="/audit",
)


@audit.route("/")
@role_required(UserRole.ADMIN, UserRole.MANAGER)
def index():

    #========================
    # FILTROS
    #========================

    action = request.args.get(
        "action",
        "",
    ).strip()

    entity_type = request.args.get(
        "entity_type",
        "",
    ).strip()

    user_id = request.args.get(
        "user_id",
        type=int,
    )

    start_date = request.args.get(
        "start_date",
        "",
    ).strip()

    end_date = request.args.get(
        "end_date",
        "",
    ).strip()


    #=========================
    # CONSULTAS
    #=========================

    query = AuditLog.query


    if action:

        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:

        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if user_id is not None:

        query = query.filter(
            AuditLog.user_id == user_id
        )

    if start_date:

        try:

            start_datetime = datetime.strptime(
                start_date,
                "%Y-%m-%d",
            )

            query = query.filter(
                AuditLog.created_at >= start_datetime
            )

        except ValueError:
            pass


    if end_date:

        try:

            end_datetime = datetime.strptime(
                end_date,
                "%Y-%m-%d",
            )

            end_datetime = end_datetime.replace(
                hour=23,
                minute=59,
                second=59,
            )

            query = query.filter(
                AuditLog.created_at <= end_datetime
            )

        except ValueError:
            pass



    #========================
    # CONTADORES
    #========================


    total_logs = query.count()

    total_creates = query.filter(
        AuditLog.action == "CREATE"
    ).count()

    total_updates = query.filter(
        AuditLog.action == "UPDATE"
    ).count()

    total_sensitive = query.filter(
        AuditLog.action.in_(
            [
                "DELETE",
                "REVERSE",
                "INVENTORY",
                "DEACTIVATE",
            ]
        )
    ).count()


    #==========================
    # PAGINAÇÃO
    #==========================


    page = request.args.get(
        "page",
        1,
        type=int,
    )

    pagination = (
        query.order_by(
            AuditLog.created_at.desc()
        ).paginate(
            page=page,
            per_page=20,
            error_out=False,
        )
    )

    logs = pagination.items

    #======================
    # OPÇÕES DE FILTROS
    #======================

    users = (
        User.query.order_by(
            User.username
        ).all()
    )

    actions = [
        "CREATE",
        "UPDATE",
        "ACTIVATE",
        "DEACTIVATE",
        "DELETE",
        "REVERSE",
        "INVENTORY",
    ]

    entity_types = [
        "Product",
        "Category",
        "StockMovement",
    ]


    return render_template(
        "audit/index.html",
        logs=logs,
        pagination=pagination,
        users=users,
        actions=actions,
        entity_types=entity_types,
        selected_action=action,
        selected_entity_type=entity_type,
        selected_user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        total_logs=total_logs,
        total_creates=total_creates,
        total_updates=total_updates,
        total_sensitive=total_sensitive,
    )