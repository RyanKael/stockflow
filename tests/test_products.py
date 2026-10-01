from app.extensions import db
from app.models.product import Product


def login(client, username, password="123456"):

    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )


def test_admin_can_create_product(
        client,
        admin_user,
):

    login(
        client,
        "admin_test"
    )

    response = client.post(
        "/products/new",
        data={
            "code": "NOVO001",
            "name": "Produto Novo",
            "description": "Produto criado por teste.",
            "quantity": 10,
            "minimum_stock": 2,
            "location": "Armário B",
            "active": "y",
            "category_id": 0,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200


    product = Product.query.filter_by(
        code="NOVO001"
    ).first()


    assert product is not None

    assert product.name == "Produto Novo"

    assert product.description == (
        "Produto criado por teste."
    )

    assert product.quantity == 10

    assert product.minimum_stock == 2

    assert product.location == "Armário B"

    assert product.active is True

    assert product.category_id is None


def test_admin_can_edit_product(
        client,
        admin_user,
        product,
):

    login(
        client,
        "admin_test",
    )

    response = client.post(
        f"/products/{product.id}/edit",
        data={
            "code": product.code,
            "name": "Produto Alterado",
            "description": "Descrição alterada.",
            "minimum_stock": 8,
            "location": "Armário C",
            "active": "y",
            "category_id": 0,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    db.session.refresh(
        product
    )

    assert product.name == "Produto Alterado"
    assert product.description == "Descrição alterada."
    assert product.minimum_stock == 8
    assert product.location == "Armário C"
    assert product.active is True
    assert product.category_id is None