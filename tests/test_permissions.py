def login(client, username, password="123456"):

    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )

def test_admin_can_access_users(
        client,
        admin_user,
):

    login(
        client,
        "admin_test",
    )

    response = client.get(
        "/users/",
        follow_redirects=False,
    )

    assert response.status_code == 200


def test_manager_cannot_access_users(
        client,
        manager_user,
):

    login(
        client,
        "manager_test",
    )

    response = client.get(
        "/users/",
        follow_redirects=False,
    )

    assert response.status_code == 302


def test_user_cannot_access_users(
        client,
        normal_user,
):

    login(
        client,
        "user_test",
    )

    response = client.get(
        "/users/",
        follow_redirects=False,
    )

    assert response.status_code == 302