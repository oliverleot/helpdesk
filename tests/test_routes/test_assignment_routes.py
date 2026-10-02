from app.models.ticket_history import TicketHistory


def test_agent_can_assign_ticket(agent_client, agent, ticket):
    r = agent_client.post(
        f"/tickets/{ticket.id}/assign", data={"agent_id": str(agent.id)}, follow_redirects=True
    )
    assert r.status_code == 200
    assert agent.username.encode() in r.data


def test_admin_can_assign_ticket(admin_client, admin, ticket):
    r = admin_client.post(
        f"/tickets/{ticket.id}/assign", data={"agent_id": str(admin.id)}, follow_redirects=True
    )
    assert admin.username.encode() in r.data


def test_user_cannot_assign_ticket(user_client, agent, ticket):
    r = user_client.post(f"/tickets/{ticket.id}/assign", data={"agent_id": str(agent.id)})
    assert r.status_code == 403


def test_assignment_is_persisted(agent_client, agent, ticket, db):
    agent_client.post(f"/tickets/{ticket.id}/assign", data={"agent_id": str(agent.id)})

    db.session.refresh(ticket)
    assert ticket.assigned_to == agent.id


def test_unassign_ticket(agent_client, agent, ticket):
    agent_client.post(f"/tickets/{ticket.id}/assign", data={"agent_id": str(agent.id)})

    r = agent_client.post(
        f"/tickets/{ticket.id}/assign", data={"agent_id": ""}, follow_redirects=True
    )
    assert "Sin asignar".encode() in r.data


def test_assign_creates_history_entry(agent_client, agent, ticket):
    agent_client.post(f"/tickets/{ticket.id}/assign", data={"agent_id": str(agent.id)})

    history = TicketHistory.query.filter_by(ticket_id=ticket.id, field="assigned_to").all()
    assert len(history) == 1


def test_unassign_creates_history_entry(agent_client, agent, ticket):
    agent_client.post(f"/tickets/{ticket.id}/assign", data={"agent_id": str(agent.id)})
    agent_client.post(f"/tickets/{ticket.id}/assign", data={"agent_id": ""})

    history = TicketHistory.query.filter_by(ticket_id=ticket.id, field="assigned_to").all()
    assert len(history) == 2


def test_assign_invalid_user_shows_error_and_does_not_assign(agent_client, user, ticket):
    r = agent_client.post(
        f"/tickets/{ticket.id}/assign", data={"agent_id": str(user.id)}, follow_redirects=True
    )
    assert "no es un agente valido" in r.get_data(as_text=True)
    assert "Sin asignar".encode() in r.data


def test_assign_same_agent_does_not_duplicate_history(agent_client, agent, ticket):
    agent_client.post(f"/tickets/{ticket.id}/assign", data={"agent_id": str(agent.id)})
    agent_client.post(f"/tickets/{ticket.id}/assign", data={"agent_id": str(agent.id)})

    history = TicketHistory.query.filter_by(ticket_id=ticket.id, field="assigned_to").all()
    assert len(history) == 1
