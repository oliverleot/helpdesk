import os
import tempfile

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db as _db
from app.models.user import User, Role
from app.models.ticket import Ticket, TicketStatus, TicketPriority

TEST_PASSWORD = "password123"


@pytest.fixture()
def app():
    """
    Crea una app Flask nueva para cada test, usando SQLite en un archivo
    temporal propio. Nunca toca la base de datos de desarrollo en
    PostgreSQL: DATABASE_URL se sobreescribe explicitamente aca.

    SQLite es compatible con los modelos actuales porque no usamos
    ningun tipo o funcion especifica de PostgreSQL (solo columnas
    Integer/String/Text/DateTime y ForeignKey estandar).
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })

    ctx = application.app_context()
    ctx.push()
    _db.create_all()

    yield application

    _db.session.remove()
    _db.drop_all()
    ctx.pop()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def client(app):
    return app.test_client()


def _create_user(db, username, email, role):
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(TEST_PASSWORD),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user(db):
    return _create_user(db, "user1", "user1@test.com", Role.USER)


@pytest.fixture()
def other_user(db):
    return _create_user(db, "user2", "user2@test.com", Role.USER)


@pytest.fixture()
def agent(db):
    return _create_user(db, "agente1", "agente1@test.com", Role.AGENT)


@pytest.fixture()
def admin(db):
    return _create_user(db, "admin1", "admin1@test.com", Role.ADMIN)


def login(client, email, password=TEST_PASSWORD):
    return client.post(
        "/login", data={"email": email, "password": password}, follow_redirects=True
    )


# IMPORTANTE: el fixture `app` mantiene un app_context activo durante todo el
# test (necesario para poder hacer consultas SQLAlchemy directas en el cuerpo
# del test). Por eso, Flask-Login cachea el usuario logueado en `flask.g`,
# que vive en ese mismo app_context compartido. Si un test necesita DOS
# usuarios logueados "al mismo tiempo" (por ejemplo, comparar lo que ve un
# USER contra lo que ve otro), usar un unico test client con un
# `client.post("/logout")` explicito entre un login y el otro, en vez de dos
# fixtures *_client distintas en el mismo test: dos logins simultaneos sin
# logout de por medio pueden pisarse entre si por este cacheo compartido.
# Esto es un detalle de como se simulan los tests, no ocurre en producción,
# donde cada request real siempre tiene su propio contexto aislado.


@pytest.fixture()
def user_client(app, user):
    c = app.test_client()
    login(c, user.email)
    return c


@pytest.fixture()
def other_user_client(app, other_user):
    c = app.test_client()
    login(c, other_user.email)
    return c


@pytest.fixture()
def agent_client(app, agent):
    c = app.test_client()
    login(c, agent.email)
    return c


@pytest.fixture()
def admin_client(app, admin):
    c = app.test_client()
    login(c, admin.email)
    return c


@pytest.fixture()
def ticket(db, user):
    t = Ticket(
        title="Mi laptop no conecta al WiFi",
        description="Desde esta manana no puedo conectarme a la red",
        category="NETWORK",
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=user.id,
    )
    db.session.add(t)
    db.session.commit()
    return t
