from datetime import datetime

from flask import abort

from app.extensions import db
from app.models.ticket import Ticket, TicketStatus
from app.models.comment import Comment
from app.models.ticket_history import TicketHistory
from app.models.user import Role


def can_view_ticket(user, ticket):
    if user.role in (Role.AGENT, Role.ADMIN):
        return True
    return ticket.created_by == user.id


def get_tickets_for_user(user):
    query = Ticket.query.order_by(Ticket.created_at.desc())
    if user.role in (Role.AGENT, Role.ADMIN):
        return query.all()
    return query.filter_by(created_by=user.id).all()


def get_ticket_or_403(ticket_id, user):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not can_view_ticket(user, ticket):
        abort(403)
    return ticket


def create_ticket(data, user):
    ticket = Ticket(
        title=data["title"],
        description=data["description"],
        category=data["category"],
        priority=data["priority"],
        status=TicketStatus.OPEN,
        created_by=user.id,
    )
    db.session.add(ticket)
    db.session.flush()

    history = TicketHistory(
        ticket_id=ticket.id,
        user_id=user.id,
        field="status",
        old_value=None,
        new_value=TicketStatus.OPEN,
    )
    db.session.add(history)
    db.session.commit()
    return ticket


def change_status(ticket, new_status, user):
    old_status = ticket.status
    ticket.status = new_status
    if new_status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()

    db.session.add(TicketHistory(
        ticket_id=ticket.id,
        user_id=user.id,
        field="status",
        old_value=old_status,
        new_value=new_status,
    ))
    db.session.commit()
    return ticket


def change_priority(ticket, new_priority, user):
    old_priority = ticket.priority
    ticket.priority = new_priority

    db.session.add(TicketHistory(
        ticket_id=ticket.id,
        user_id=user.id,
        field="priority",
        old_value=old_priority,
        new_value=new_priority,
    ))
    db.session.commit()
    return ticket


def add_comment(ticket, user, content):
    comment = Comment(ticket_id=ticket.id, user_id=user.id, content=content)
    db.session.add(comment)
    db.session.commit()
    return comment
