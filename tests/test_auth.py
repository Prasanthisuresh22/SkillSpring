import re

from app.models import User
from extensions import db


def csrf_token(client, path="/register"):
    response = client.get(path)
    match = re.search(rb'name="csrf_token"[^>]+value="([^"]+)"', response.data)
    assert match is not None
    return match.group(1).decode()


def register(client, email="student@example.com", password="secure-pass-123", name="Test Student"):
    return client.post(
        "/register",
        data={
            "csrf_token": csrf_token(client),
            "full_name": name,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, email="student@example.com", password="secure-pass-123"):
    return client.post(
        "/login",
        data={"csrf_token": csrf_token(client, "/login"), "email": email, "password": password},
        follow_redirects=True,
    )


def test_auth_pages_load(client):
    assert client.get("/register").status_code == 200
    assert client.get("/login").status_code == 200


def test_registration_creates_hashed_password(client, app):
    response = register(client)
    assert response.status_code == 200
    assert b"Your account is ready" in response.data
    with app.app_context():
        user = User.query.filter_by(email="student@example.com").one()
        assert user.full_name == "Test Student"
        assert user.password_hash != "secure-pass-123"
        assert user.password_hash.startswith("scrypt:")


def test_registration_validation_and_duplicate_email(client):
    register(client)
    duplicate = register(client)
    assert b"already registered" in duplicate.data
    invalid_email = client.post(
        "/register",
        data={
            "csrf_token": csrf_token(client),
            "full_name": "Another Student",
            "email": "not-an-email",
            "password": "secure-pass-123",
            "confirm_password": "different-pass",
        },
    )
    assert invalid_email.status_code == 200
    assert b"Invalid email address" in invalid_email.data
    assert b"Passwords must match" in invalid_email.data


def test_missing_registration_fields_are_rejected(client):
    response = client.post("/register", data={"csrf_token": csrf_token(client)})
    assert response.status_code == 200
    assert b"This field is required" in response.data


def test_login_success_and_failure(client):
    register(client)
    failed = client.post(
        "/login",
        data={"csrf_token": csrf_token(client, "/login"), "email": "student@example.com", "password": "wrong-password"},
    )
    assert failed.status_code == 200
    assert b"Invalid email or password" in failed.data
    logged_in = login(client)
    assert logged_in.status_code == 200
    assert b"Welcome, Test Student" in logged_in.data


def test_logout_is_post_only_and_clears_session(client):
    register(client)
    login(client)
    assert client.get("/logout").status_code == 405
    response = client.post(
        "/logout",
        data={"csrf_token": csrf_token(client, "/dashboard")},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"You have been logged out" in response.data
    assert client.get("/dashboard").status_code == 302


def test_dashboard_requires_authentication_and_shows_user(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    register(client)
    login(client)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Test Student" in response.data


def test_csrf_rejects_state_changing_request_without_token(client):
    response = client.post(
        "/register",
        data={
            "full_name": "No Token",
            "email": "not-saved@example.com",
            "password": "secure-pass-123",
            "confirm_password": "secure-pass-123",
        },
    )
    assert response.status_code == 400
    with client.application.app_context():
        assert db.session.query(User).filter_by(email="not-saved@example.com").first() is None
