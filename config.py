import os 

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "trocar-essa-chave-no-futuro"


    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(basedir, 'stockflow.db')}"
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False