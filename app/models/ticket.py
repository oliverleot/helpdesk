from datetime import datetime

from app.extensions import db


class TicketStatus:
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING = "WAITING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class TicketPriority:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketCategory:
    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    NETWORK = "NETWORK"
    ACCESS = "ACCESS"
    OTHER = "OTHER"


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), nullable=False, default=TicketStatus.OPEN)
    priority = db.Column(db.String(20), nullable=False, default=TicketPriority.MEDIUM)
    category = db.Column(db.String(20), nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    creator = db.relationship("User", foreign_keys=[created_by], backref="created_tickets")
    agent = db.relationship("User", foreign_keys=[assigned_to], backref="assigned_tickets")

    comments = db.relationship("Comment", backref="ticket", lazy=True)
    history = db.relationship("TicketHistory", backref="ticket", lazy=True)

    def __repr__(self):
        return f"<Ticket {self.id} {self.title}>"
