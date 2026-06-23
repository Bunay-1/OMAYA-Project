import pytest
from datetime import timedelta
from auth import AuthManager, TokenData, User

def test_password_hashing():
    password = "test_password"
    hashed = AuthManager.get_password_hash(password)
    assert AuthManager.verify_password(password, hashed)
    assert not AuthManager.verify_password("wrong_password", hashed)

def test_authenticate_user():
    # Test valid credentials
    user = AuthManager.authenticate_user("admin", "password123")
    assert user is not None
    assert user.username == "admin"

    # Test invalid username
    assert AuthManager.authenticate_user("nonexistent", "password") is None

    # Test invalid password
    assert AuthManager.authenticate_user("admin", "wrong_password") is None

def test_create_and_verify_access_token():
    data = {"sub": "test_user", "roles": ["operator"]}
    token = AuthManager.create_access_token(data)

    assert token.token_type == "bearer"
    assert token.access_token is not None

    # Verify token
    token_data = AuthManager.verify_token(token.access_token)
    assert token_data is not None
    assert token_data.username == "test_user"
    assert "operator" in token_data.roles

def test_token_expiration():
    data = {"sub": "test_user"}
    # Create an expired token
    token = AuthManager.create_access_token(data, expires_delta=timedelta(seconds=-1))

    # Verify should fail
    assert AuthManager.verify_token(token.access_token) is None

def test_has_permission():
    assert AuthManager.has_permission(["admin"], "operator") is True
    assert AuthManager.has_permission(["operator"], "admin") is False
    assert AuthManager.has_permission(["supervisor"], "operator") is True
    assert AuthManager.has_permission(["operator"], "operator") is True
