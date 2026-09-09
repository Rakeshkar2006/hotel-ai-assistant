from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.models.service_request import ServiceRequest
from app.db.models.guest import Guest
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestResponse,
    ServiceRequestUpdate,
)


router = APIRouter(
    prefix="/service-requests",
    tags=["Service Requests"],
)


@router.post(
    "",
    response_model=ServiceRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service_request(
    data: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    guest = db.get(Guest, data.guest_id)

    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    service_request = ServiceRequest(
        guest_id=data.guest_id,
        request_type=data.request_type,
        description=data.description,
        status="pending",
    )

    db.add(service_request)
    db.commit()
    db.refresh(service_request)

    return service_request


@router.get(
    "",
    response_model=list[ServiceRequestResponse],
)
def list_service_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    service_requests = db.scalars(
        select(ServiceRequest).order_by(ServiceRequest.id)
    ).all()

    return service_requests


@router.get(
    "/{service_request_id}",
    response_model=ServiceRequestResponse,
)
def get_service_request(
    service_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    service_request = db.get(
        ServiceRequest,
        service_request_id,
    )

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
        )

    return service_request


@router.patch(
    "/{service_request_id}",
    response_model=ServiceRequestResponse,
)
def update_service_request(
    service_request_id: int,
    data: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "receptionist")
    ),
):
    service_request = db.get(
        ServiceRequest,
        service_request_id,
    )

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(service_request, field, value)

    db.commit()
    db.refresh(service_request)

    return service_request


@router.delete(
    "/{service_request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service_request(
    service_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
):
    service_request = db.get(
        ServiceRequest,
        service_request_id,
    )

    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
        )

    db.delete(service_request)
    db.commit()

    return None