import os
import shutil

from datetime import datetime

import click
from flask import current_app

from app.extensions import db
from app.models.user import User, UserRole


# =========================================================
# CRIAR ADMINISTRADOR
# =========================================================

@click.command("create-admin")
@click.option(
    "--username",
    prompt="Nome de usuário",
)
@click.option(
    "--email",
    prompt="Email",
)
@click.option(
    "--password",
    prompt="Senha",
    hide_input=True,
    confirmation_prompt=True,
)
def create_admin(
    username,
    email,
    password,
):

    if User.query.filter_by(
        username=username
    ).first():

        click.echo(
            "Erro: esse nome de usuário já existe."
        )

        return


    if User.query.filter_by(
        email=email
    ).first():

        click.echo(
            "Erro: esse e-mail já está cadastrado."
        )

        return


    user = User(
        username=username,
        email=email,
        role=UserRole.ADMIN,
    )

    user.set_password(
        password
    )

    db.session.add(
        user
    )

    db.session.commit()


    click.echo(
        f"Administrador '{username}' criado com sucesso."
    )


# =========================================================
# BACKUP DO BANCO SQLITE
# =========================================================

@click.command("backup-db")
def backup_db():

    database_uri = current_app.config[
        "SQLALCHEMY_DATABASE_URI"
    ]


    # Este comando é usado apenas no SQLite local

    if not database_uri.startswith(
        "sqlite:///"
    ):

        click.echo(
            "O comando backup-db atual suporta apenas SQLite."
        )

        return


    # Remove o prefixo sqlite:///

    database_path = database_uri.replace(
        "sqlite:///",
        "",
        1,
    )


    # =====================================================
    # PASTA RAIZ DO PROJETO
    # =====================================================

    project_root = os.path.abspath(
        os.path.join(
            current_app.root_path,
            "..",
        )
    )


    backup_directory = os.path.join(
        project_root,
        "backups",
    )


    os.makedirs(
        backup_directory,
        exist_ok=True,
    )


    # =====================================================
    # NOME DO BACKUP
    # =====================================================

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )


    backup_filename = (
        f"stockflow_{timestamp}.db"
    )


    backup_path = os.path.join(
        backup_directory,
        backup_filename,
    )


    # =====================================================
    # VALIDAÇÃO
    # =====================================================

    if not os.path.exists(
        database_path
    ):

        click.echo(
            "Erro: banco de dados não encontrado."
        )

        return


    # =====================================================
    # CÓPIA DO BANCO
    # =====================================================

    shutil.copy2(
        database_path,
        backup_path,
    )


    click.echo(
        "Backup criado com sucesso:"
    )

    click.echo(
        backup_path
    )