

def test_login_page_loads(client):

    response = client.get(
        "/auth/login"
    )

    assert response.status_code == 200


def test_login_valid(client, admin_user):

    response = client.post(
        "/auth/login",
        data={
            "username": "admin_test",
            "password": "123456",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "_user_id" in session
        assert session["_user_id"] == str(admin_user.id)


def test_login_invalid(client, admin_user):

    response = client.post(
        "/auth/login",
        data={
            "username": "admin_test",
            "password": "senha_errada",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "_user_id" not in session