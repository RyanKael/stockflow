from flask import Blueprint, render_template, redirect, flash, request, url_for
from flask_login import login_user, logout_user

from app.models.user import User


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(
            username=username
        ).first()

        if user is None or not user.check_password(password):

            flash(
                "Usuário ou senha incorretos.",
                "danger",
            )

            return render_template(
                "auth/login.html"
            )

        if not user.active:

            flash(
                "Este usuário está desativado.",
                "danger",
            )

            return render_template(
                "auth/login.html"
            )

        login_user(user)

        return redirect(
            url_for("main.index")
        )

    return render_template(
        "auth/login.html"
    )

@auth.route("/logout")
def logout():

    logout_user()

    return redirect(
        url_for("auth.login")
    )
