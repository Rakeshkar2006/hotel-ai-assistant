from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models.booking import Booking
from app.db.models.guest import Guest
from app.db.models.room import Room
from app.db.models.room_type import RoomType
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    # 1. Check-out date must be after check-in date
    if data.check_out <= data.check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date",
        )

    # 2. Check that the guest exists
    guest = db.get(Guest, data.guest_id)

    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    # 3. Check that the room exists
    room = db.get(Room, data.room_id)

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    # 4. Check room status
    if room.status != "available":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is not available",
        )

    # 5. Check for overlapping bookings
    overlapping_booking = db.scalar(
        select(Booking).where(
            Booking.room_id == data.room_id,
            Booking.status.in_(
                ["pending", "confirmed", "checked_in"]
            ),
            Booking.check_in < data.check_out,
            Booking.check_out > data.check_in,
        )
    )

    if overlapping_booking:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is already booked for these dates",
        )

    # 6. Get room type
    room_type = db.get(RoomType, room.room_type_id)

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    # 7. Calculate number of nights
    number_of_nights = (
        data.check_out - data.check_in
    ).days

    # 8. Calculate total price
    total_price = room_type.base_price * number_of_nights

    # 9. Create booking
    booking = Booking(
        guest_id=data.guest_id,
        room_id=data.room_id,
        check_in=data.check_in,
        check_out=data.check_out,
        total_price=total_price,
        status="pending",
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


@router.get(
    "",
    response_model=list[BookingResponse],
)
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    bookings = db.scalars(
        select(Booking).order_by(Booking.id)
    ).all()

    return bookings


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    booking = db.get(Booking, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking


@router.patch(
    "/{booking_id}",
    response_model=BookingResponse,
)
def update_booking(
    booking_id: int,
    data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    booking = db.get(Booking, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Check dates if either date is being updated
    new_check_in = update_data.get(
        "check_in",
        booking.check_in,
    )

    new_check_out = update_data.get(
        "check_out",
        booking.check_out,
    )

    if new_check_out <= new_check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date",
        )

    # If dates are changing, check for overlapping bookings
    if "check_in" in update_data or "check_out" in update_data:
        overlapping_booking = db.scalar(
            select(Booking).where(
                Booking.room_id == booking.room_id,
                Booking.id != booking.id,
                Booking.status.in_(
                    ["pending", "confirmed", "checked_in"]
                ),
                Booking.check_in < new_check_out,
                Booking.check_out > new_check_in,
            )
        )

        if overlapping_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room is already booked for these dates",
            )

        # Recalculate total price
        room = db.get(Room, booking.room_id)

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        room_type = db.get(RoomType, room.room_type_id)

        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room type not found",
            )

        number_of_nights = (
            new_check_out - new_check_in
        ).days

        update_data["check_in"] = new_check_in
        update_data["check_out"] = new_check_out
        booking.total_price = (
            room_type.base_price * number_of_nights
        )

    # Update allowed fields
    for field, value in update_data.items():
        if field != "total_price":
            setattr(booking, field, value)

    db.commit()
    db.refresh(booking)

    return booking


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
):
    booking = db.get(Booking, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    db.delete(booking)
    db.commit()

    return None