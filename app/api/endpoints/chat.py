from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import decode_access_token
from app.db.models.booking import Booking
from app.db.models.chat_message import ChatMessage
from app.db.models.chat_session import ChatSession
from app.db.models.guest import Guest
from app.db.models.room import Room
from app.db.models.user import User
from app.db.session import get_db
from app.rag.answer import answer_question


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


class ChatHistoryMessage(BaseModel):
    id: int
    session_id: int
    question: str
    answer: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryMessage]


def is_booking_question(question: str) -> bool:
    booking_keywords = [
        "booking",
        "reservation",
        "reserved",
        "reservation status",
        "booking status",
        "my room",
        "my booking",
        "my reservation",
    ]

    question_lower = question.lower()

    return any(
        keyword in question_lower
        for keyword in booking_keywords
    )


def get_my_booking_answer(
    db: Session,
    current_user: User,
):
    guest = db.scalar(
        select(Guest).where(
            Guest.user_id == current_user.id
        )
    )

    if not guest:
        return "I could not find a guest profile linked to your account."

    bookings = db.scalars(
        select(Booking)
        .where(
            Booking.guest_id == guest.id
        )
        .order_by(Booking.id.desc())
    ).all()

    if not bookings:
        return "You do not have any bookings in the hotel system."

    booking_lines = []

    for booking in bookings:
        room = db.get(Room, booking.room_id)

        room_number = (
            room.room_number
            if room
            else str(booking.room_id)
        )

        booking_lines.append(
            f"Booking ID: {booking.id}, "
            f"Room: {room_number}, "
            f"Check-in: {booking.check_in}, "
            f"Check-out: {booking.check_out}, "
            f"Total price: {booking.total_price}, "
            f"Status: {booking.status}."
        )

    return (
        "Your booking information: "
        + " ".join(booking_lines)
    )


def generate_chat_answer(
    db: Session,
    question: str,
    current_user: User,
):
    if is_booking_question(question):
        answer = get_my_booking_answer(
            db,
            current_user
        )

        sources = []

    else:
        rag_result = answer_question(
            db,
            question
        )

        answer = rag_result["answer"]
        sources = rag_result["sources"]

    return answer, sources


def get_or_create_chat_session(
    db: Session,
    current_user: User,
):
    chat_session = db.scalar(
        select(ChatSession)
        .where(
            ChatSession.user_id == current_user.id
        )
        .order_by(ChatSession.id.desc())
    )

    if not chat_session:
        chat_session = ChatSession(
            user_id=current_user.id
        )

        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)

    return chat_session


@router.post(
    "",
    response_model=ChatResponse
)
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat_session = get_or_create_chat_session(
        db,
        current_user
    )

    answer, sources = generate_chat_answer(
        db,
        data.question,
        current_user
    )

    chat_message = ChatMessage(
        session_id=chat_session.id,
        question=data.question,
        answer=answer,
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)

    return {
        "answer": answer,
        "sources": sources,
    }


@router.get(
    "/history",
    response_model=ChatHistoryResponse
)
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = db.scalars(
        select(ChatMessage)
        .join(
            ChatSession,
            ChatSession.id == ChatMessage.session_id
        )
        .where(
            ChatSession.user_id == current_user.id
        )
        .order_by(ChatMessage.created_at.asc())
    ).all()

    history = []

    for message in messages:
        history.append(
            ChatHistoryMessage(
                id=message.id,
                session_id=message.session_id,
                question=message.question,
                answer=message.answer,
                created_at=message.created_at.isoformat(),
            )
        )

    return {
        "messages": history
    }


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    db: Session = next(get_db())

    try:
        # First message must contain JWT token
        auth_data = await websocket.receive_json()

        token = auth_data.get("token")

        if not token:
            await websocket.send_json({
                "error": "Authentication token is required"
            })
            await websocket.close(code=1008)
            return

        # Verify JWT
        try:
            payload = decode_access_token(token)
        except Exception:
            await websocket.send_json({
                "error": "Invalid or expired token"
            })
            await websocket.close(code=1008)
            return

        user_id = payload.get("sub")

        if not user_id:
            await websocket.send_json({
                "error": "Invalid token"
            })
            await websocket.close(code=1008)
            return

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            await websocket.send_json({
                "error": "Invalid token subject"
            })
            await websocket.close(code=1008)
            return

        current_user = db.scalar(
            select(User).where(
                User.id == user_id
            )
        )

        if not current_user:
            await websocket.send_json({
                "error": "User not found"
            })
            await websocket.close(code=1008)
            return

        if not current_user.is_active:
            await websocket.send_json({
                "error": "User account is inactive"
            })
            await websocket.close(code=1008)
            return

        # Get or create chat session
        chat_session = get_or_create_chat_session(
            db,
            current_user
        )

        await websocket.send_json({
            "message": "WebSocket authentication successful",
            "session_id": chat_session.id
        })

        # Continuous chat loop
        while True:
            message_data = await websocket.receive_json()

            question = message_data.get("question")

            if not question:
                await websocket.send_json({
                    "error": "Question is required"
                })
                continue

            answer, sources = generate_chat_answer(
                db,
                question,
                current_user
            )

            # Save message
            chat_message = ChatMessage(
                session_id=chat_session.id,
                question=question,
                answer=answer,
            )

            db.add(chat_message)
            db.commit()
            db.refresh(chat_message)

            # Send real-time answer
            await websocket.send_json({
                "question": question,
                "answer": answer,
                "sources": sources,
                "message_id": chat_message.id,
            })

    except WebSocketDisconnect:
        pass

    finally:
        db.close()