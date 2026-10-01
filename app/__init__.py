from flask import Flask

import logging
import os
from config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, login_manager, csrf
from app.routes import main, products, movements, reports, categories, audit
from app.routes.auth import auth
from app.routes.users import users
from app.utils.datetime import to_local_datetime
from app.utils import collation
from logging.handlers import RotatingFileHandler


def create_app():
    app = Flask(__name__)

    #======================
    #CONFIGURAÇÃO DO AMBIENTE
    #======================

    config_name = os.getenv(
        "FLASK_CONFIG",
        "development",
    )

    if config_name == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    #======================
    #FILTROS JINJA
    #======================

    app.jinja_env.filters["local_datetime"] = to_local_datetime

    #==================
    #EXTENSÕES
    #==================


    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "warning"

    #===============================
    # LOGS DO SISTEMA
    #===============================

    project_root = os.path.abspath(
        os.path.join(
            app.root_path,
            "..",
        )
    )

    log_directory = os.path.join(
        project_root,
        "logs",
    )

    os.makedirs(
        log_directory,
        exist_ok=True,
    )

    log_file = os.path.join(
        log_directory,
        "stockflow.log",
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setLevel(
        logging.INFO
    )

    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        )
    )

    app.logger.addHandler(
        file_handler
    )

    app.logger.setLevel(
        logging.INFO
    )

    app.logger.info(
        "StockFlow iniciado."
    )

    #=============================
    #COMANDOS CLI
    #=============================

    from app.commands import create_admin, backup_db

    app.cli.add_command(create_admin)
    app.cli.add_command(backup_db)

    #==============================
    #BLUEPRINTS
    #=============================

    app.register_blueprint(main)
    app.register_blueprint(products)
    app.register_blueprint(movements)
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(reports)
    app.register_blueprint(categories)
    app.register_blueprint(audit)

    #========================
    #MODELS
    #========================

    from app.models import Product, StockMovement, Category, User

    #==========================
    #FLASK-LOGIN
    #==========================

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(
            User,
            int(user_id),
        )

    from flask import render_template


    @app.errorhandler(403)
    def forbidden(error):

        return render_template(
            "errors/403.html"
        ), 403


    @app.errorhandler(404)
    def page_not_found(error):

        return render_template(
            "errors/404.html"
        ), 404


    @app.errorhandler(500)
    def internal_server_error(error):

        db.session.rollback()

        return render_template(
            "errors/500.html"
        ), 50


    """
    @app.route("/test-500")
    def test_500():
        raise Exception("Erro de teste para log")
   """


    return app

