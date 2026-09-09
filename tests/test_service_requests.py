from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token


client = TestClient(app)


def get_admin_token():
    return create_access_token(subject="3", role="admin")


def create_test_guest():
    token = get_admin_token()

    email = f"pytest_service_guest_{uuid4().hex[:8]}@example.com"

    response = client.post(
        "/guests",
        json={
            "full_name": "Pytest Service Guest",
            "email": email,
            "phone": "9876543210",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_service_request():
    token = get_admin_token()

    guest_id = create_test_guest()

    response = client.post(
        "/service-requests",
        json={
            "guest_id": guest_id,
            "request_type": "housekeeping",
            "description": "Please clean the room.",
            "status": "pending",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["guest_id"] == guest_id
    assert data["request_type"] == "housekeeping"
    assert data["description"] == "Please clean the room."
    assert data["status"] == "pending"


def test_list_service_requests():
    token = get_admin_token()

    response = client.get(
        "/service-requests",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_invalid_service_request_guest():
    token = get_admin_token()

    response = client.post(
        "/service-requests",
        json={
            "guest_id": 999999,
            "request_type": "housekeeping",
            "description": "Invalid guest test.",
            "status": "pending",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404