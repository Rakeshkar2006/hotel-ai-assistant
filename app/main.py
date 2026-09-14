from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.room_types import router as room_types_router
from app.api.endpoints.rooms import router as rooms_router
from app.api.endpoints.guests import router as guests_router
from app.api.endpoints.bookings import router as bookings_router
from app.api.endpoints.service_requests import router as service_requests_router
from app.api.endpoints.documents import router as documents_router
from app.api.endpoints.chat import router as chat_router


app = FastAPI(
    title="Hotel AI Assistant",
    version="1.0.0",
)


app.include_router(auth_router)

app.include_router(room_types_router)

app.include_router(rooms_router)

app.include_router(guests_router)

app.include_router(bookings_router)

app.include_router(service_requests_router)

app.include_router(documents_router)

app.include_router(chat_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/chat.html", include_in_schema=False)
def chat_page():
    chat_file = (
        Path(__file__).resolve().parent.parent
        / "frontend"
        / "chat.html"
    )

    return FileResponse(chat_file)