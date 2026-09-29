from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.user import User, Role


def register_user(username, email, password, role=Role.USER):
    username = username.strip()
    email = email.strip().lower()

    if User.query.filter_by(email=email).first():
        raise ValueError("Ese email ya esta registrado.")
    if User.query.filter_by(username=username).first():
        raise ValueError("Ese nombre de usuario ya esta en uso.")

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Ese email o nombre de usuario ya esta en uso.")
    return user


def authenticate(email, password):
    user = User.query.filter_by(email=email.strip().lower()).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
