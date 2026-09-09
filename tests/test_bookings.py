from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token


client = TestClient(app)


def get_admin_token():
    return create_access_token(subject="3", role="admin")


def get_existing_room_type_id():
    response = client.get("/room-types")

    assert response.status_code == 200

    room_types = response.json()

    assert len(room_types) > 0

    return room_types[0]["id"]


def create_test_room():
    token = get_admin_token()

    room_type_id = get_existing_room_type_id()

    room_number = f"PYTEST-{uuid4().hex[:8]}"

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
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_test_guest():
    token = get_admin_token()

    email = f"pytest_booking_guest_{uuid4().hex[:8]}@example.com"

    response = client.post(
        "/guests",
        json={
            "full_name": "Pytest Booking Guest",
            "email": email,
            "phone": "9876543210",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_create_booking():
    token = get_admin_token()

    guest_id = create_test_guest()

    room_id = create_test_room()

    check_in = date.today() + timedelta(days=365)

    check_out = check_in + timedelta(days=2)

    response = client.post(
        "/bookings",
        json={
            "guest_id": guest_id,
            "room_id": room_id,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "status": "pending",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["guest_id"] == guest_id

    assert data["room_id"] == room_id

    assert data["check_in"] == check_in.isoformat()

    assert data["check_out"] == check_out.isoformat()

    assert data["status"] == "pending"

    assert float(data["total_price"]) > 0


def test_invalid_booking_dates():
    token = get_admin_token()

    guest_id = create_test_guest()

    room_id = create_test_room()

    check_in = date.today() + timedelta(days=40)

    check_out = check_in

    response = client.post(
        "/bookings",
        json={
            "guest_id": guest_id,
            "room_id": room_id,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "status": "pending",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400


def test_overlapping_booking_is_rejected():
    token = get_admin_token()

    guest_id = create_test_guest()

    room_id = create_test_room()

    check_in = date.today() + timedelta(days=60)

    check_out = check_in + timedelta(days=3)

    # First booking
    first_response = client.post(
        "/bookings",
        json={
            "guest_id": guest_id,
            "room_id": room_id,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "status": "pending",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert first_response.status_code == 201

    # Second guest
    second_guest_id = create_test_guest()

    # Overlapping booking
    overlapping_response = client.post(
        "/bookings",
        json={
            "guest_id": second_guest_id,
            "room_id": room_id,
            "check_in": (check_in + timedelta(days=1)).isoformat(),
            "check_out": (check_out + timedelta(days=1)).isoformat(),
            "status": "pending",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert overlapping_response.status_code == 409