from functools import wraps

from flask import flash, redirect, request, url_for
from flask_login import current_user, login_required


def role_required(*roles):

    def decorator(function):

        @wraps(function)
        @login_required
        def wrapper(*args, **kwargs):

            if current_user.role not in roles:

                flash(
                    "Seu perfil não possui permissão para realizar esta ação.",
                    "danger",
                )

                return redirect(
                    request.referrer
                    or url_for("main.dashboard")
                )

            return function(*args, **kwargs)

        return wrapper

    return decorator