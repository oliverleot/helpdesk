import pytest

from app.services import ticket_service
from app.models.ticket import TicketStatus, TicketPriority
from app.models.ticket_history import TicketHistory


def test_create_ticket_sets_open_status_and_creator(db, user):
    ticket = ticket_service.create_ticket(
        {"title": "t", "description": "d", "category": "OTHER", "priority": TicketPriority.LOW},
        user,
    )

    assert ticket.status == TicketStatus.OPEN
    assert ticket.created_by == user.id


def test_get_tickets_for_user_only_returns_own_tickets(db, user, other_user, ticket):
    assert ticket_service.get_tickets_for_user(user) == [ticket]
    assert ticket_service.get_tickets_for_user(other_user) == []


def test_get_tickets_for_agent_sees_all_tickets(db, agent, ticket):
    assert ticket in ticket_service.get_tickets_for_user(agent)


def test_change_status_records_history(db, ticket, agent):
    ticket_service.change_status(ticket, TicketStatus.IN_PROGRESS, agent)

    assert ticket.status == TicketStatus.IN_PROGRESS
    history = TicketHistory.query.filter_by(ticket_id=ticket.id, field="status").all()
    assert len(history) == 1
    assert history[0].old_value == TicketStatus.OPEN
    assert history[0].new_value == TicketStatus.IN_PROGRESS


def test_change_status_to_resolved_sets_resolved_at(db, ticket, agent):
    ticket_service.change_status(ticket, TicketStatus.RESOLVED, agent)

    assert ticket.resolved_at is not None


def test_change_priority_records_history(db, ticket, agent):
    ticket_service.change_priority(ticket, TicketPriority.URGENT, agent)

    assert ticket.priority == TicketPriority.URGENT
    history = TicketHistory.query.filter_by(ticket_id=ticket.id, field="priority").all()
    assert len(history) == 1


def test_add_comment(db, ticket, user):
    comment = ticket_service.add_comment(ticket, user, "hola, alguna novedad?")

    assert comment.ticket_id == ticket.id
    assert comment.content == "hola, alguna novedad?"


def test_get_available_agents_returns_only_agent_and_admin(db, user, agent, admin):
    agents = ticket_service.get_available_agents()
    usernames = {a.username for a in agents}

    assert agent.username in usernames
    assert admin.username in usernames
    assert user.username not in usernames


def test_assign_ticket_persists_and_creates_history(db, ticket, agent):
    ticket_service.assign_ticket(ticket, str(agent.id), agent)

    assert ticket.assigned_to == agent.id
    history = TicketHistory.query.filter_by(ticket_id=ticket.id, field="assigned_to").all()
    assert len(history) == 1
    assert history[0].new_value == agent.username


def test_unassign_ticket_creates_history(db, ticket, agent):
    ticket_service.assign_ticket(ticket, str(agent.id), agent)
    ticket_service.assign_ticket(ticket, "", agent)

    assert ticket.assigned_to is None
    history = TicketHistory.query.filter_by(ticket_id=ticket.id, field="assigned_to").all()
    assert len(history) == 2


def test_assign_user_without_agent_role_raises(db, ticket, agent, user):
    with pytest.raises(ValueError):
        ticket_service.assign_ticket(ticket, str(user.id), agent)


def test_assign_nonexistent_user_raises(db, ticket, agent):
    with pytest.raises(ValueError):
        ticket_service.assign_ticket(ticket, "99999", agent)


def test_assign_same_agent_does_not_duplicate_history(db, ticket, agent):
    ticket_service.assign_ticket(ticket, str(agent.id), agent)
    ticket_service.assign_ticket(ticket, str(agent.id), agent)

    history = TicketHistory.query.filter_by(ticket_id=ticket.id, field="assigned_to").all()
    assert len(history) == 1
