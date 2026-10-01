import pytest

from app import create_app
from app.extensions import db
from app.models.product import Product
from app.models.user import User, UserRole


@pytest.fixture()
def app():

    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():

        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):

    return app.test_client()


@pytest.fixture()
def runner(app):

    return app.test_cli_runner()


@pytest.fixture()
def admin_user(app):

    user = User(
        username="admin_test",
        email="admin@test.com",
        role=UserRole.ADMIN,
        active=True,
    )

    user.set_password(
        "123456"
    )

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture()
def manager_user(app):

    user = User(
        username="manager_test",
        email="manager@test.com",
        role=UserRole.MANAGER,
        active=True,
    )

    user.set_password(
        "123456"
    )

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture()
def normal_user(app):

    user = User(
        username="user_test",
        email="user@test.com",
        role=UserRole.USER,
        active=True,
    )

    user.set_password(
        "123456"
    )

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture()
def product(app):

    product = Product(
        code="TEST001",
        name="Produto de Teste",
        description="Produto usado nos testes automatizados.",
        quantity=20,
        minimum_stock=5,
        location="Armário A",
        active=True,
    )

    db.session.add(product)
    db.session.commit()

    return product