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


def test_create_room_type():
    token = get_admin_token()

    room_type_name = f"Test Room {uuid4().hex[:8]}"

    response = client.post(
        "/room-types",
        json={
            "name": room_type_name,
            "description": "Room type created by automated test",
            "base_price": 2500,
            "max_guests": 2,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == room_type_name
    assert data["description"] == "Room type created by automated test"
    assert data["base_price"] == 2500
    assert data["max_guests"] == 2


def test_list_room_types():
    response = client.get("/room-types")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)