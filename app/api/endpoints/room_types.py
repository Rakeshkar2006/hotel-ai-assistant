from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models.room_type import RoomType
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.room_type import (
    RoomTypeCreate,
    RoomTypeResponse,
    RoomTypeUpdate,
)


router = APIRouter(
    prefix="/room-types",
    tags=["Room Types"],
)


# ============================================================
# CREATE ROOM TYPE
# Admin and Receptionist only
# ============================================================

@router.post(
    "",
    response_model=RoomTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room_type(
    data: RoomTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    # Check if room type with the same name already exists
    existing_room_type = db.scalar(
        select(RoomType).where(RoomType.name == data.name)
    )

    if existing_room_type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room type already exists",
        )

    # Create new room type
    room_type = RoomType(
        name=data.name,
        description=data.description,
        base_price=data.base_price,
        max_guests=data.max_guests,
    )

    db.add(room_type)
    db.commit()
    db.refresh(room_type)

    return room_type


# ============================================================
# LIST ALL ROOM TYPES
# Public endpoint
# ============================================================

@router.get(
    "",
    response_model=list[RoomTypeResponse],
)
def list_room_types(
    db: Session = Depends(get_db),
):
    room_types = db.scalars(
        select(RoomType).order_by(RoomType.id)
    ).all()

    return room_types


# ============================================================
# GET SINGLE ROOM TYPE
# Public endpoint
# ============================================================

@router.get(
    "/{room_type_id}",
    response_model=RoomTypeResponse,
)
def get_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
):
    room_type = db.get(RoomType, room_type_id)

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    return room_type


# ============================================================
# UPDATE ROOM TYPE
# Admin and Receptionist only
# ============================================================

@router.patch(
    "/{room_type_id}",
    response_model=RoomTypeResponse,
)
def update_room_type(
    room_type_id: int,
    data: RoomTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    # Find room type
    room_type = db.get(RoomType, room_type_id)

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    # Get only fields that were actually provided
    update_data = data.model_dump(exclude_unset=True)

    # Check duplicate name
    if "name" in update_data:
        existing_room_type = db.scalar(
            select(RoomType).where(
                RoomType.name == update_data["name"],
                RoomType.id != room_type_id,
            )
        )

        if existing_room_type:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room type name already exists",
            )

    # Update fields
    for field, value in update_data.items():
        setattr(room_type, field, value)

    db.commit()
    db.refresh(room_type)

    return room_type


# ============================================================
# DELETE ROOM TYPE
# Admin only
# ============================================================

@router.delete(
    "/{room_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
):
    # Find room type
    room_type = db.get(RoomType, room_type_id)

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    # Delete room type
    db.delete(room_type)
    db.commit()

    return None