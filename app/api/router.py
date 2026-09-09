from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.room_types import router as room_types_router
from app.api.endpoints.rooms import router as rooms_router
from app.api.endpoints.guests import router as guests_router
from app.api.endpoints.bookings import router as bookings_router
from app.api.endpoints.service_requests import router as service_requests_router
from app.api.endpoints.documents import router as documents_router
from app.api.endpoints.chat import router as chat_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(room_types_router)
api_router.include_router(rooms_router)
api_router.include_router(guests_router)
api_router.include_router(bookings_router)
api_router.include_router(service_requests_router)
api_router.include_router(documents_router)
api_router.include_router(chat_router)