import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:


    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):

    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, 'stockflow.db')}"
    )


class ProductionConfig(Config):

    DEBUG = False

    database_url = os.getenv("DATABASE_URL")

    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    elif database_url and database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    SQLALCHEMY_DATABASE_URI = database_url

    SESSION_COOKIE_SECURE = True

    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"