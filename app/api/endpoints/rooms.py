from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models.room import Room
from app.db.models.room_type import RoomType
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.room import RoomCreate, RoomResponse, RoomUpdate


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)


# ============================================================
# CREATE ROOM
# Admin and Receptionist only
# ============================================================

@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    # Check whether the room number already exists
    existing_room = db.scalar(
        select(Room).where(Room.room_number == data.room_number)
    )

    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room number already exists",
        )

    # Check whether the selected room type exists
    room_type = db.get(RoomType, data.room_type_id)

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    # Create room
    room = Room(
        room_number=data.room_number,
        room_type_id=data.room_type_id,
        status=data.status,
        amenities=data.amenities,
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return room


# ============================================================
# LIST ALL ROOMS
# Public endpoint
# ============================================================

@router.get(
    "",
    response_model=list[RoomResponse],
)
def list_rooms(
    db: Session = Depends(get_db),
):
    rooms = db.scalars(
        select(Room).order_by(Room.id)
    ).all()

    return rooms


# ============================================================
# GET SINGLE ROOM
# Public endpoint
# ============================================================

@router.get(
    "/{room_id}",
    response_model=RoomResponse,
)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
):
    room = db.get(Room, room_id)

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return room


# ============================================================
# UPDATE ROOM
# Admin and Receptionist only
# ============================================================

@router.patch(
    "/{room_id}",
    response_model=RoomResponse,
)
def update_room(
    room_id: int,
    data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    # Find room
    room = db.get(Room, room_id)

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Check duplicate room number
    if "room_number" in update_data:
        existing_room = db.scalar(
            select(Room).where(
                Room.room_number == update_data["room_number"],
                Room.id != room_id,
            )
        )

        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists",
            )

    # Check new room type if room_type_id is being changed
    if "room_type_id" in update_data:
        room_type = db.get(
            RoomType,
            update_data["room_type_id"],
        )

        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room type not found",
            )

    # Update fields
    for field, value in update_data.items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)

    return room


# ============================================================
# DELETE ROOM
# Admin only
# ============================================================

@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
):
    # Find room
    room = db.get(Room, room_id)

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    db.delete(room)
    db.commit()

    return None