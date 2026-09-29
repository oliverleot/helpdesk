from flask import Blueprint, render_template, redirect, url_for, request

from flask_login import login_required, current_user

from app.forms import TicketForm, CommentForm
from app.models.user import Role
from app.models.ticket import TicketStatus, TicketPriority
from app.services import ticket_service
from app.utils.decorators import roles_required

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")

ALL_STATUSES = [
    TicketStatus.OPEN,
    TicketStatus.IN_PROGRESS,
    TicketStatus.WAITING,
    TicketStatus.RESOLVED,
    TicketStatus.CLOSED,
]

ALL_PRIORITIES = [
    TicketPriority.LOW,
    TicketPriority.MEDIUM,
    TicketPriority.HIGH,
    TicketPriority.URGENT,
]


@tickets_bp.route("", methods=["GET"])
@login_required
def list_tickets():
    tickets = ticket_service.get_tickets_for_user(current_user)
    return render_template("tickets/list.html", tickets=tickets)


@tickets_bp.route("/new", methods=["GET"])
@login_required
def new_ticket_form():
    form = TicketForm()
    return render_template("tickets/form.html", form=form)


@tickets_bp.route("", methods=["POST"])
@login_required
def create_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = ticket_service.create_ticket(
            {
                "title": form.title.data,
                "description": form.description.data,
                "category": form.category.data,
                "priority": form.priority.data,
            },
            current_user,
        )
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))
    return render_template("tickets/form.html", form=form)


@tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@login_required
def detail(ticket_id):
    ticket = ticket_service.get_ticket_or_403(ticket_id, current_user)
    comment_form = CommentForm()
    return render_template(
        "tickets/detail.html",
        ticket=ticket,
        comment_form=comment_form,
        statuses=ALL_STATUSES,
        priorities=ALL_PRIORITIES,
    )


@tickets_bp.route("/<int:ticket_id>/status", methods=["POST"])
@login_required
@roles_required(Role.AGENT, Role.ADMIN)
def update_status(ticket_id):
    ticket = ticket_service.get_ticket_or_403(ticket_id, current_user)
    new_status = request.form.get("status")
    ticket_service.change_status(ticket, new_status, current_user)
    return redirect(url_for("tickets.detail", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/priority", methods=["POST"])
@login_required
@roles_required(Role.AGENT, Role.ADMIN)
def update_priority(ticket_id):
    ticket = ticket_service.get_ticket_or_403(ticket_id, current_user)
    new_priority = request.form.get("priority")
    ticket_service.change_priority(ticket, new_priority, current_user)
    return redirect(url_for("tickets.detail", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/comments", methods=["POST"])
@login_required
def add_comment(ticket_id):
    ticket = ticket_service.get_ticket_or_403(ticket_id, current_user)
    form = CommentForm()
    if form.validate_on_submit():
        ticket_service.add_comment(ticket, current_user, form.content.data)
    return redirect(url_for("tickets.detail", ticket_id=ticket.id))
