from app.extensions import db
from app.models.product import Product
from app.models.stock_movement import (
    StockMovement,
    MovementType,
)


def login(
    client,
    username,
    password="123456",
):

    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )


def test_entry_increases_stock(
    client,
    admin_user,
    product,
):

    login(
        client,
        "admin_test",
    )

    initial_quantity = product.quantity

    response = client.post(
        "/movements/new",
        data={
            "product_id": product.id,
            "movement_type": MovementType.ENTRY.value,
            "quantity": 5,
            "reason": "Entrada de teste",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    db.session.refresh(product)

    assert product.quantity == initial_quantity + 5

    movement = (
        StockMovement.query
        .filter_by(
            product_id=product.id,
            movement_type=MovementType.ENTRY,
        )
        .order_by(
            StockMovement.id.desc()
        )
        .first()
    )

    assert movement is not None
    assert movement.quantity == 5
    assert movement.previous_quantity == initial_quantity
    assert movement.user_id == admin_user.id


def test_exit_decreases_stock(
    client,
    admin_user,
    product,
):

    login(
        client,
        "admin_test",
    )

    initial_quantity = product.quantity

    response = client.post(
        "/movements/new",
        data={
            "product_id": product.id,
            "movement_type": MovementType.EXIT.value,
            "quantity": 5,
            "reason": "Saída de teste",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    db.session.refresh(product)

    assert product.quantity == initial_quantity - 5

    movement = (
        StockMovement.query
        .filter_by(
            product_id=product.id,
            movement_type=MovementType.EXIT,
        )
        .order_by(
            StockMovement.id.desc()
        )
        .first()
    )

    assert movement is not None
    assert movement.quantity == 5
    assert movement.previous_quantity == initial_quantity
    assert movement.user_id == admin_user.id


def test_exit_cannot_exceed_stock(
    client,
    admin_user,
    product,
):

    login(
        client,
        "admin_test",
    )

    initial_quantity = product.quantity

    response = client.post(
        "/movements/new",
        data={
            "product_id": product.id,
            "movement_type": MovementType.EXIT.value,
            "quantity": initial_quantity + 100,
            "reason": "Saída inválida",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    db.session.refresh(product)

    assert product.quantity == initial_quantity

    movement = StockMovement.query.filter_by(
        product_id=product.id,
        movement_type=MovementType.EXIT,
    ).first()

    assert movement is None


def test_adjustment_changes_stock(
    client,
    admin_user,
    product,
):

    login(
        client,
        "admin_test",
    )

    initial_quantity = product.quantity

    response = client.post(
        "/movements/new",
        data={
            "product_id": product.id,
            "movement_type": MovementType.ADJUSTMENT.value,
            "quantity": 12,
            "reason": "Ajuste de teste",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    db.session.refresh(product)

    assert product.quantity == 12

    movement = (
        StockMovement.query
        .filter_by(
            product_id=product.id,
            movement_type=MovementType.ADJUSTMENT,
        )
        .order_by(
            StockMovement.id.desc()
        )
        .first()
    )

    assert movement is not None
    assert movement.quantity == 12
    assert movement.previous_quantity == initial_quantity
    assert movement.user_id == admin_user.id


def test_reverse_entry_restores_stock(
    client,
    admin_user,
    product,
):

    login(
        client,
        "admin_test",
    )

    initial_quantity = product.quantity

    # Cria uma entrada de 5 unidades

    client.post(
        "/movements/new",
        data={
            "product_id": product.id,
            "movement_type": MovementType.ENTRY.value,
            "quantity": 5,
            "reason": "Entrada para teste de estorno",
        },
        follow_redirects=True,
    )

    db.session.refresh(product)

    assert product.quantity == initial_quantity + 5

    movement = (
        StockMovement.query
        .filter_by(
            product_id=product.id,
            movement_type=MovementType.ENTRY,
        )
        .order_by(
            StockMovement.id.desc()
        )
        .first()
    )

    assert movement is not None


    # Estorna a movimentação criada

    response = client.post(
        f"/movements/{movement.id}/reverse",
        follow_redirects=True,
    )

    assert response.status_code == 200

    db.session.refresh(product)

    assert product.quantity == initial_quantity


    reverse_movement = (
        StockMovement.query
        .filter_by(
            reversed_movement_id=movement.id
        )
        .first()
    )

    assert reverse_movement is not None
    assert reverse_movement.movement_type == MovementType.EXIT
    assert reverse_movement.quantity == 5
    assert reverse_movement.user_id == admin_user.id


def test_cannot_reverse_same_movement_twice(
    client,
    admin_user,
    product,
):

    login(
        client,
        "admin_test",
    )

    client.post(
        "/movements/new",
        data={
            "product_id": product.id,
            "movement_type": MovementType.ENTRY.value,
            "quantity": 5,
            "reason": "Entrada para teste",
        },
        follow_redirects=True,
    )

    movement = (
        StockMovement.query
        .filter_by(
            product_id=product.id,
            movement_type=MovementType.ENTRY,
        )
        .order_by(
            StockMovement.id.desc()
        )
        .first()
    )

    client.post(
        f"/movements/{movement.id}/reverse",
        follow_redirects=True,
    )

    first_reverse = StockMovement.query.filter_by(
        reversed_movement_id=movement.id
    ).count()

    client.post(
        f"/movements/{movement.id}/reverse",
        follow_redirects=True,
    )

    second_reverse = StockMovement.query.filter_by(
        reversed_movement_id=movement.id
    ).count()

    assert first_reverse == 1
    assert second_reverse == 1


def test_user_cannot_make_adjustment(
    client,
    normal_user,
    product,
):

    login(
        client,
        "user_test",
    )

    initial_quantity = product.quantity

    response = client.post(
        "/movements/new",
        data={
            "product_id": product.id,
            "movement_type": MovementType.ADJUSTMENT.value,
            "quantity": 50,
            "reason": "Tentativa de ajuste",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    db.session.refresh(product)

    assert product.quantity == initial_quantity

    movement = StockMovement.query.filter_by(
        product_id=product.id,
        movement_type=MovementType.ADJUSTMENT,
    ).first()

    assert movement is None