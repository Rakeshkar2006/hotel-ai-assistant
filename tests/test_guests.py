from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token


client = TestClient(app)


def get_admin_token():
    return create_access_token(
        subject="3",
        role="admin",
    )


def test_create_guest():
    token = get_admin_token()

    email = f"pytest_guest_{uuid4().hex[:8]}@example.com"

    response = client.post(
        "/guests",
        json={
            "full_name": "Pytest Guest",
            "email": email,
            "phone": "9876543210",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Pytest Guest"
    assert data["email"] == email
    assert data["phone"] == "9876543210"


def test_list_guests():
    token = get_admin_token()

    response = client.get(
        "/guests",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)