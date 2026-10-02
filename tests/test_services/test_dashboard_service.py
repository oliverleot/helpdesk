from app.services import dashboard_service, ticket_service


def test_user_only_sees_own_metrics(db, user, other_user, ticket):
    metrics = dashboard_service.get_dashboard_metrics(user)
    assert metrics["is_global"] is False
    assert metrics["total"] == 1

    other_metrics = dashboard_service.get_dashboard_metrics(other_user)
    assert other_metrics["total"] == 0


def test_agent_sees_global_metrics(db, user, agent, ticket):
    metrics = dashboard_service.get_dashboard_metrics(agent)
    assert metrics["is_global"] is True
    assert metrics["total"] == 1


def test_admin_sees_global_metrics(db, user, admin, ticket):
    metrics = dashboard_service.get_dashboard_metrics(admin)
    assert metrics["is_global"] is True
    assert metrics["total"] == 1


def test_assigned_to_me(db, ticket, agent):
    ticket_service.assign_ticket(ticket, str(agent.id), agent)

    metrics = dashboard_service.get_dashboard_metrics(agent)
    assert metrics["assigned_to_me"] == 1
