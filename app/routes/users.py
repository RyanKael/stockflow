from flask import Blueprint, flash, render_template, redirect, url_for, request

from app.extensions import db
from app.models.user import UserRole, User
from app.utils.auth import role_required
from flask_login import current_user


users = Blueprint(
    "users",
    __name__,
    url_prefix="/users",
)


@users.route("/")
@role_required(UserRole.ADMIN)
def list_users():

    users_list = User.query.order_by(
        User.username
    ).all()

    return render_template(
        "users/list.html",
        users=users_list,
    )

@users.route("/new", methods=["GET", "POST"])
@role_required(UserRole.ADMIN)
def new_user():

    if request.method == "POST":

        username = request.form.get(
            "username",
            "",
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role_value = request.form.get(
            "role",
            ""
        )

        #----------------------------------
        # Validação de usuário
        #----------------------------------

        if not username:

            flash(
                "Informe o nome de usuário.",
                "danger",
            )

            return render_template(
                "users/form.html",
            )

        #--------------------------
        # Validação do email
        #-------------------------

        if not email:

            flash(
                "Informe o seu e-mail.",
                "danger",
            )

            return render_template(
                "users/form.html",

            )

        #-------------------------
        # Validação da senha
        #-------------------------

        if not password:

            flash(
                "Informe sua senha.",
                "danger",
            )

            return render_template(
                "users/form.html",
            )

        if len(password) < 8:

            flash(
                "A senha deve possuir pelo menos 8 caracteres.",
                "danger",
            )

            return render_template(
                "users/form.html",
            )

        #---------------------------
        # Validação do perfil
        #--------------------------

        try:

            role = UserRole(role_value)


        except ValueError:

            flash(
                "Selecione um perfil válido.",
                "danger",
            )

            return render_template(
                "users/form.html",
            )


        #-------------------------
        # Verifica usuário existente
        #--------------------------

        existing_username = User.query.filter_by(
            username=username,
        ).first()


        if existing_username:

            flash(
                "Este nome de usuário já foi cadastrado.",
                "danger",
            )

            return render_template(
                "users/form.html",
            )

        #----------------------------
        # Verifica o e-mail existente
        #----------------------------


        existing_email = User.query.filter_by(
            email=email,
        ).first()

        if existing_email:

            flash(
                "Este e-mail já está cadastrado.",
                "danger",
            )

            return render_template(
                "users/form.html",
            )

        #-------------------------------
        # Criação do usuário
        #-------------------------------

        user = User(
            username=username,
            email=email,
            role=role,
            active=True,
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(
            f"Usuário '{username}' criado com sucesso.",
            "success",
        )

        return redirect(
            url_for("users.list_users")
        )

    return render_template(
        "users/form.html",
    )

@users.route("/<int:id>/edit", methods=["GET", "POST"])
@role_required(UserRole.ADMIN)
def edit_user(id):

    user = db.get_or_404(
        User,
        id,
    )

    if request.method == "POST":

        username = request.form.get(
            "username",
            "",
        ).strip()


        email = request.form.get(
            "email",
            "",
        ).strip()


        role_value = request.form.get(
            "role",
            "",
        )

        #---------------------------------
        # Validação
        #---------------------------------

        if not username:

            flash(
                "Informe o nome de usuário.",
                "danger",
            )

            return render_template(
                "users/edit.html",
                user=user,
                UserRole=UserRole,
            )

        if not email:

            flash(
                "Informe o e-mail.",
                "danger",

            )

            return render_template(
                "users/edit.html",
                user=user,
                UserRole=UserRole,
            )

        #------------------------------
        # Validação do perfil
        #-----------------------------

        try:

            role = UserRole(role_value)


        except ValueError:

            flash(
                "Selecione um perfil válido.",
                "danger",
            )

            return render_template(
                "users/edit.html",
                user=user,
                UserRole=UserRole,
            )

        #----------------------------
        # Verifica username
        #-----------------------------

        existing_username = User.query.filter(
            User.username == username,
            User.id != user.id,
        ).first()

        if existing_username:

            flash(
                "Este nome de usuário já está cadastrado.",
                "danger",
            )

            return render_template(
                "users/edit.html",
                user=user,
                UserRole=UserRole,
            )

        #--------------------------
        # Verifica e-mail
        #--------------------------


        existing_email = User.query.filter(
            User.email == email,
            User.id != user.id,
        ).first()

        if existing_email:

            flash(
                "Este e-mail já está cadastrado.",
                "danger",
            )

            return render_template(
                "users/edit.html",
                user=user,
                UserRole=UserRole,
            )

        #----------------------
        # Atualização
        #-------------------------

        user.username = username
        user.email = email
        user.role = role

        db.session.commit()

        flash(
            f"Usuário '{user.username}' atualizado com sucesso.",
            "success",
        )

        return redirect(
            url_for("users.list_users")
        )

    return render_template(
        "users/edit.html",
        user=user,
        UserRole=UserRole,
    )

@users.route("/<int:id>/deactivate", methods=["POST"])
@role_required(UserRole.ADMIN)
def deactivate_user(id):

    user = db.get_or_404(
        User,
        id,
    )

    if not user.active:

        flash(
            "Este usuário já está desativado.",
            "warning",
        )

        return redirect(
            url_for("users.list_users")
        )

    #  Impde o administrador de desativar a própria conta

    if user.id == current_user.id:

        flash(
            "Você não pode desativar sua própria conta.",
            "danger",
        )

        return redirect(
            url_for("users.list_users")
        )

    user.active = False

    db.session.commit()

    flash(
        f"Usuário '{user.username}' desativado com sucesso.",
        "success",
    )

    return redirect(
        url_for("users.list_users")
    )


@users.route("/<int:id>/activate", methods=["POST"])
@role_required(UserRole.ADMIN)
def activate_user(id):

    user = db.get_or_404(
        User,
        id,
    )

    if user.active:

        flash(
            "Este usuário já está ativo.",
            "warning",
        )

        return redirect(
            url_for("users.list_users")
        )


    user.active = True

    db.session.commit()

    flash(
        f"Usuário '{user.username}' ativado com sucesso.",
        "success",
    )

    return redirect(
        url_for("users.list_users")
    )

@users.route("/<int:id>/password", methods=["GET", "POST"])
@role_required(UserRole.ADMIN)
def change_password(id):

    user = db.get_or_404(
        User,
        id,
    )

    if request.method == "POST":

        password = request.form.get(
            "password",
            "",
        )

        confirmation = request.form.get(
            "confirmation",
            "",
        )

        #-----------------------
        # Validação da senha
        #-----------------------

        if not password:

            flash(
                "Informe a senha novamente.",
                "danger",
            )

            return render_template(
                "users/password.html",
            )

        if len(password) < 8:

            flash(
                "A senha deve possuir pelo menos 8 caracteres.",
                "danger",
            )

            return render_template(
                "users/password.html",
            )

        #----------------------
        # Confirmação
        #----------------------

        if password != confirmation:

            flash(
                "As senhas não coincidem.",
                "danger",
            )

            return render_template(
                "users/password.html",
            )

        #--------------------
        # Atualiza senha
        #--------------------

        user.set_password(password)
        db.session.commit()

        flash(
            f"Senha do usuário '{user.username}' alterada com sucesso.",
            "success",
        )

        return redirect(
            url_for("users.list_users")
        )

    return render_template(
        "users/password.html",
        user=user,
    )
