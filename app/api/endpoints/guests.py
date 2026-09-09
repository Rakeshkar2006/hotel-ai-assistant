from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models.guest import Guest
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.guest import GuestCreate, GuestResponse, GuestUpdate


router = APIRouter(
    prefix="/guests",
    tags=["Guests"],
)


@router.post(
    "",
    response_model=GuestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_guest(
    data: GuestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    # Check email uniqueness
    existing_guest = db.scalar(
        select(Guest).where(Guest.email == data.email)
    )

    if existing_guest:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Guest with this email already exists",
        )

    # Check user_id if provided
    if data.user_id is not None:
        user = db.get(User, data.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        existing_user_guest = db.scalar(
            select(Guest).where(
                Guest.user_id == data.user_id
            )
        )

        if existing_user_guest:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This user is already linked to a guest",
            )

    guest = Guest(
        user_id=data.user_id,
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
    )

    db.add(guest)
    db.commit()
    db.refresh(guest)

    return guest


@router.get(
    "",
    response_model=list[GuestResponse],
)
def list_guests(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    guests = db.scalars(
        select(Guest).order_by(Guest.id)
    ).all()

    return guests


@router.get(
    "/{guest_id}",
    response_model=GuestResponse,
)
def get_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    guest = db.get(Guest, guest_id)

    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    return guest


@router.patch(
    "/{guest_id}",
    response_model=GuestResponse,
)
def update_guest(
    guest_id: int,
    data: GuestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    guest = db.get(Guest, guest_id)

    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Check email uniqueness
    if "email" in update_data:
        existing_guest = db.scalar(
            select(Guest).where(
                Guest.email == update_data["email"],
                Guest.id != guest_id,
            )
        )

        if existing_guest:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Guest with this email already exists",
            )

    # Check user_id uniqueness
    if "user_id" in update_data:
        user_id = update_data["user_id"]

        if user_id is not None:
            user = db.get(User, user_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            existing_user_guest = db.scalar(
                select(Guest).where(
                    Guest.user_id == user_id,
                    Guest.id != guest_id,
                )
            )

            if existing_user_guest:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This user is already linked to a guest",
                )

    for field, value in update_data.items():
        setattr(guest, field, value)

    db.commit()
    db.refresh(guest)

    return guest


@router.delete(
    "/{guest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
):
    guest = db.get(Guest, guest_id)

    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    db.delete(guest)
    db.commit()

    return None