"""
Tests for Security Hardening Module
"""
import pytest
from backend.security_hardening import (
    PasswordValidator,
    TokenManager,
    SecurityConfig,
    SecurityHeaders
)
from unittest.mock import Mock
import secrets


def test_password_validator_strong_password():
    """Test password validation with strong password."""
    validator = PasswordValidator()
    password = "StrongP@ssw0rd123!"
    is_valid, errors = validator.validate_password(password)
    assert is_valid is True
    assert len(errors) == 0


def test_password_validator_weak_password():
    """Test password validation with weak password."""
    validator = PasswordValidator()
    password = "weak"
    is_valid, errors = validator.validate_password(password)
    assert is_valid is False
    assert len(errors) > 0


def test_password_validator_no_uppercase():
    """Test password without uppercase."""
    validator = PasswordValidator()
    password = "lowercase123!"
    is_valid, errors = validator.validate_password(password)
    assert is_valid is False
    assert any("uppercase" in e.lower() for e in errors)


def test_password_validator_no_digit():
    """Test password without digit."""
    validator = PasswordValidator()
    password = "NoDigitsHere!"
    is_valid, errors = validator.validate_password(password)
    assert is_valid is False
    assert any("digit" in e.lower() for e in errors)


def test_password_validator_no_special_char():
    """Test password without special character."""
    validator = PasswordValidator()
    password = "NoSpecialChars123"
    is_valid, errors = validator.validate_password(password)
    assert is_valid is False
    assert any("special" in e.lower() for e in errors)


def test_generate_secure_password():
    """Test secure password generation."""
    validator = PasswordValidator()
    password = validator.generate_secure_password(length=16)
    assert len(password) == 16
    is_valid, _ = validator.validate_password(password)
    assert is_valid is True


def test_token_manager_create_access_token():
    """Test access token creation."""
    manager = TokenManager(secret_key="test_secret_key")
    data = {"user_id": "test_user"}
    token = manager.create_access_token(data)
    assert token is not None
    assert isinstance(token, str)


def test_token_manager_verify_token():
    """Test token verification."""
    manager = TokenManager(secret_key="test_secret_key")
    data = {"user_id": "test_user"}
    token = manager.create_access_token(data)
    payload = manager.verify_token(token)
    assert payload is not None
    assert payload["user_id"] == "test_user"


def test_token_manager_blacklist_token():
    """Test token blacklisting."""
    manager = TokenManager(secret_key="test_secret_key")
    data = {"user_id": "test_user"}
    token = manager.create_access_token(data)
    
    manager.blacklist_token(token)
    payload = manager.verify_token(token)
    assert payload is None


def test_token_manager_create_refresh_token():
    """Test refresh token creation."""
    manager = TokenManager(secret_key="test_secret_key")
    data = {"user_id": "test_user"}
    token = manager.create_refresh_token(data)
    assert token is not None
    assert isinstance(token, str)


def test_security_config_defaults():
    """Test security configuration defaults."""
    assert SecurityConfig.MIN_PASSWORD_LENGTH == 12
    assert SecurityConfig.REQUIRE_UPPERCASE is True
    assert SecurityConfig.REQUIRE_LOWERCASE is True
    assert SecurityConfig.REQUIRE_DIGITS is True
    assert SecurityConfig.REQUIRE_SPECIAL_CHARS is True


def test_security_headers_get():
    """Test security headers retrieval."""
    headers = SecurityHeaders.get_security_headers()
    assert headers is not None
    assert "X-Content-Type-Options" in headers
    assert "X-Frame-Options" in headers
    assert "Strict-Transport-Security" in headers
    assert "Content-Security-Policy" in headers


def test_security_headers_values():
    """Test security header values."""
    headers = SecurityHeaders.get_security_headers()
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"
