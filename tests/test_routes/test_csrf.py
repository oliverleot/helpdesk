import re

# Estos tests activan CSRF explicitamente (el resto de la suite lo deja
# desactivado via WTF_CSRF_ENABLED=False para simplificar, pero eso es solo
# configuracion de testing: CSRFProtect sigue activo por default en la app real).


def _csrf_token(client, url):
    html = client.get(url).get_data(as_text=True)
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    assert match, f"No se encontro csrf_token en {url}"
    return match.group(1)


def test_login_without_csrf_token_is_rejected(app, db, user):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()

    r = client.post("/login", data={"email": user.email, "password": "password123"})
    assert r.status_code == 400


def test_login_with_csrf_token_succeeds(app, db, user):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()

    token = _csrf_token(client, "/login")
    r = client.post(
        "/login", data={"email": user.email, "password": "password123", "csrf_token": token}
    )
    assert r.status_code == 302


def test_status_change_without_csrf_token_is_rejected(app, db, agent, ticket):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()
    token = _csrf_token(client, "/login")
    client.post(
        "/login",
        data={"email": agent.email, "password": "password123", "csrf_token": token},
    )

    r = client.post(f"/tickets/{ticket.id}/status", data={"status": "IN_PROGRESS"})
    assert r.status_code == 400


def test_status_change_with_csrf_token_succeeds(app, db, agent, ticket):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()
    login_token = _csrf_token(client, "/login")
    client.post(
        "/login",
        data={"email": agent.email, "password": "password123", "csrf_token": login_token},
    )

    page_token = _csrf_token(client, f"/tickets/{ticket.id}")
    r = client.post(
        f"/tickets/{ticket.id}/status",
        data={"status": "IN_PROGRESS", "csrf_token": page_token},
    )
    assert r.status_code in (200, 302)
