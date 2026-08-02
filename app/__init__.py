from flask import Flask

from config import Config
from app.routes import main
from app.extensions import db, migrate


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main)

    from app.models.product import Product

    return app

