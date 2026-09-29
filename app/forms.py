from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from app.models.ticket import TicketCategory, TicketPriority


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El email es obligatorio."),
            Email(message="Ingresa un email valido."),
        ],
    )
    password = PasswordField(
        "Contraseña", validators=[DataRequired(message="La contraseña es obligatoria.")]
    )


class RegisterForm(FlaskForm):
    username = StringField(
        "Usuario",
        validators=[
            DataRequired(message="El usuario es obligatorio."),
            Length(min=3, max=80, message="El usuario debe tener entre 3 y 80 caracteres."),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El email es obligatorio."),
            Email(message="Ingresa un email valido."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=8, message="La contraseña debe tener al menos 8 caracteres."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(message="Debes confirmar la contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )


class TicketForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Descripcion", validators=[DataRequired()])
    category = SelectField(
        "Categoria",
        choices=[
            (TicketCategory.HARDWARE, TicketCategory.HARDWARE),
            (TicketCategory.SOFTWARE, TicketCategory.SOFTWARE),
            (TicketCategory.NETWORK, TicketCategory.NETWORK),
            (TicketCategory.ACCESS, TicketCategory.ACCESS),
            (TicketCategory.OTHER, TicketCategory.OTHER),
        ],
        validators=[DataRequired()],
    )
    priority = SelectField(
        "Prioridad",
        choices=[
            (TicketPriority.LOW, TicketPriority.LOW),
            (TicketPriority.MEDIUM, TicketPriority.MEDIUM),
            (TicketPriority.HIGH, TicketPriority.HIGH),
            (TicketPriority.URGENT, TicketPriority.URGENT),
        ],
        validators=[DataRequired()],
    )


class CommentForm(FlaskForm):
    content = TextAreaField("Comentario", validators=[DataRequired()])
