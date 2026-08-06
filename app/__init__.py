from flask import Flask

from config import Config
from app.extensions import db, migrate
from app.routes import main, products


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main)
    app.register_blueprint(products)

    from app.models.product import Product

    return app

