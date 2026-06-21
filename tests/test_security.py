from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

from datetime import timedelta


def test_password_returns_different_string():
    password = "zxc1234"

    hashed = hash_password(password)

    assert hashed != password


def test_verify_password_correct():
    password = "zxc1234"
    hashed = hash_password(password)

    result = verify_password(password, hashed)

    assert result is True


def test_verify_password_incorrect():
    password = "zxc1234"
    hashed = hash_password(password)

    result = verify_password("3143144", hashed)

    assert result is False


def test_create_access_token():
    token = create_access_token({"sub": "1"})

    assert token is not None


def test_decode_access_token():
    token = create_access_token({"sub": "1"})

    payload = decode_access_token(token)

    assert payload is not None
    assert int(payload.get("sub")) == 1


def test_overdue_token():
    token = create_access_token({"sub": "1"}, expires_delta=timedelta(minutes=-5))

    payload = decode_access_token(token)

    assert payload is None


def test_invalid_token():
    token = create_access_token({"sub": "1"})
    broken_token = token + "xxx"

    payload = decode_access_token(broken_token)

    assert payload is None
