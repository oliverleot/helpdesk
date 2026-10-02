def test_register_success_redirects_to_login(client, db):
    r = client.post(
        "/register",
        data={
            "username": "juan",
            "email": "juan@test.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_register_password_mismatch_shows_error(client, db):
    r = client.post(
        "/register",
        data={
            "username": "juan",
            "email": "juan@test.com",
            "password": "password123",
            "confirm_password": "otra-clave-distinta",
        },
    )

    assert r.status_code == 200
    assert "no coinciden" in r.get_data(as_text=True)


def test_login_correct_credentials_redirects_to_tickets(client, user):
    r = client.post("/login", data={"email": user.email, "password": "password123"})

    assert r.status_code == 302
    assert "/tickets" in r.headers["Location"]


def test_login_incorrect_credentials_stays_on_login(client, user):
    r = client.post("/login", data={"email": user.email, "password": "clave-incorrecta"})

    assert r.status_code == 200
    assert "incorrectos" in r.get_data(as_text=True)


def test_unauthenticated_user_redirected_to_login(client):
    r = client.get("/tickets")

    assert r.status_code == 302
    assert "/login" in r.headers["Location"]
