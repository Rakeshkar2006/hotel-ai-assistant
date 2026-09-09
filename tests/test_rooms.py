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


def get_existing_room_type_id():
    response = client.get("/room-types")

    assert response.status_code == 200

    room_types = response.json()

    assert len(room_types) > 0

    return room_types[0]["id"]


def test_create_room():
    token = get_admin_token()

    room_type_id = get_existing_room_type_id()
    room_number = f"TEST-{uuid4().hex[:6]}"

    response = client.post(
        "/rooms",
        json={
            "room_number": room_number,
            "room_type_id": room_type_id,
            "status": "available",
            "amenities": {
                "wifi": True,
                "tv": True,
                "ac": True,
            },
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["room_number"] == room_number
    assert data["room_type_id"] == room_type_id
    assert data["status"] == "available"
    assert data["amenities"]["wifi"] is True
    assert data["amenities"]["tv"] is True
    assert data["amenities"]["ac"] is True


def test_list_rooms():
    response = client.get("/rooms")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)