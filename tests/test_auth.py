from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_user():
    email = f"pytest_register_{uuid4().hex[:8]}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Pytest User",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Pytest User"
    assert data["role"] == "guest"
    assert data["is_active"] is True


def test_login_and_get_me():
    email = f"pytest_login_{uuid4().hex[:8]}@example.com"
    password = "TestPassword123"

    # Register a new user
    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Pytest Login User",
            "password": password,
        },
    )

    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token_data = login_response.json()

    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    token = token_data["access_token"]

    # Get current user using JWT
    me_response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert me_response.status_code == 200

    user_data = me_response.json()

    assert user_data["email"] == email
    assert user_data["full_name"] == "Pytest Login User"
    assert user_data["role"] == "guest"
    assert user_data["is_active"] is True