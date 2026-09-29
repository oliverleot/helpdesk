from sqlalchemy import func

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.user import Role


def get_dashboard_metrics(user):
    is_global = user.role in (Role.AGENT, Role.ADMIN)

    base_query = Ticket.query
    if not is_global:
        base_query = base_query.filter_by(created_by=user.id)

    status_counts = dict(
        base_query.with_entities(Ticket.status, func.count(Ticket.id))
        .group_by(Ticket.status)
        .all()
    )

    urgent_count = base_query.filter(Ticket.priority == TicketPriority.URGENT).count()
    assigned_to_me = Ticket.query.filter_by(assigned_to=user.id).count()

    return {
        "is_global": is_global,
        "total": sum(status_counts.values()),
        "open": status_counts.get(TicketStatus.OPEN, 0),
        "in_progress": status_counts.get(TicketStatus.IN_PROGRESS, 0),
        "waiting": status_counts.get(TicketStatus.WAITING, 0),
        "resolved": status_counts.get(TicketStatus.RESOLVED, 0),
        "closed": status_counts.get(TicketStatus.CLOSED, 0),
        "urgent": urgent_count,
        "assigned_to_me": assigned_to_me,
    }
