def test_user_dashboard_shows_own_metrics_only(user_client, ticket):
    r = user_client.get("/dashboard")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Metricas de tus propios tickets" in html
    assert "Metricas globales" not in html


def test_agent_dashboard_shows_global_metrics(agent_client, ticket):
    r = agent_client.get("/dashboard")
    assert "Metricas globales" in r.get_data(as_text=True)


def test_dashboard_requires_login(client):
    r = client.get("/dashboard")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]
