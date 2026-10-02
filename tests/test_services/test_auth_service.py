import pytest

from app.services import auth_service
from app.models.user import Role


def test_register_user_creates_user_with_hashed_password(db):
    user = auth_service.register_user("juan", "juan@test.com", "password123")

    assert user.id is not None
    assert user.role == Role.USER
    assert user.password_hash != "password123"


def test_register_user_duplicate_email_raises(db):
    auth_service.register_user("juan", "juan@test.com", "password123")

    with pytest.raises(ValueError):
        auth_service.register_user("otro", "juan@test.com", "password123")


def test_register_user_duplicate_username_raises(db):
    auth_service.register_user("juan", "juan@test.com", "password123")

    with pytest.raises(ValueError):
        auth_service.register_user("juan", "otro@test.com", "password123")


def test_authenticate_correct_credentials(db):
    auth_service.register_user("juan", "juan@test.com", "password123")

    user = auth_service.authenticate("juan@test.com", "password123")

    assert user is not None
    assert user.username == "juan"


def test_authenticate_wrong_password(db):
    auth_service.register_user("juan", "juan@test.com", "password123")

    assert auth_service.authenticate("juan@test.com", "clave-incorrecta") is None


def test_authenticate_unknown_email(db):
    assert auth_service.authenticate("nadie@test.com", "password123") is None
