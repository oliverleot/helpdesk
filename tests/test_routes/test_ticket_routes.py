def test_user_can_create_ticket(user_client):
    r = user_client.post(
        "/tickets",
        data={"title": "t", "description": "d", "category": "OTHER", "priority": "LOW"},
    )

    assert r.status_code == 302


def test_user_sees_only_own_tickets_in_list(client, user, other_user, ticket):
    # Un unico test client, con logout explicito entre sesiones: evita tener
    # dos "usuarios logueados" coexistiendo en el mismo proceso de test.
    client.post("/login", data={"email": user.email, "password": "password123"})
    r = client.get("/tickets")
    assert ticket.title.encode() in r.data
    client.post("/logout")

    client.post("/login", data={"email": other_user.email, "password": "password123"})
    r2 = client.get("/tickets")
    assert ticket.title.encode() not in r2.data


def test_user_cannot_change_status(user_client, ticket):
    r = user_client.post(f"/tickets/{ticket.id}/status", data={"status": "IN_PROGRESS"})
    assert r.status_code == 403


def test_user_cannot_change_priority(user_client, ticket):
    r = user_client.post(f"/tickets/{ticket.id}/priority", data={"priority": "URGENT"})
    assert r.status_code == 403


def test_agent_can_see_all_tickets(agent_client, ticket):
    r = agent_client.get("/tickets")
    assert ticket.title.encode() in r.data


def test_agent_can_change_status(agent_client, ticket):
    r = agent_client.post(
        f"/tickets/{ticket.id}/status", data={"status": "IN_PROGRESS"}, follow_redirects=True
    )
    assert r.status_code == 200
    assert b"IN_PROGRESS" in r.data


def test_agent_can_change_priority(agent_client, ticket):
    r = agent_client.post(
        f"/tickets/{ticket.id}/priority", data={"priority": "URGENT"}, follow_redirects=True
    )
    assert b"URGENT" in r.data


def test_add_comment_appears_on_detail_page(user_client, ticket):
    r = user_client.post(
        f"/tickets/{ticket.id}/comments", data={"content": "hola, alguna novedad?"},
        follow_redirects=True,
    )
    assert b"hola, alguna novedad?" in r.data


def test_history_recorded_after_status_change(agent_client, ticket):
    agent_client.post(f"/tickets/{ticket.id}/status", data={"status": "IN_PROGRESS"})

    r = agent_client.get(f"/tickets/{ticket.id}")
    assert "cambio status".encode() in r.data
