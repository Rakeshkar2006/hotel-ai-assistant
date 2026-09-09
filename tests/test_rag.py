from sqlalchemy import select
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.db.models.knowledge_document import KnowledgeDocument
from app.db.session import SessionLocal
from app.rag.search import search_knowledge

client = TestClient(app)


def get_guest_token():
    return create_access_token(subject="4", role="guest")


def test_rag_finds_approved_breakfast_document():
    db = SessionLocal()

    try:
        document = db.scalar(
            select(KnowledgeDocument).where(
                KnowledgeDocument.title == "Hotel Breakfast Policy"
            )
        )

        assert document is not None
        assert document.is_approved is True

        results = search_knowledge(
            db,
            "What time is breakfast?",
        )

        assert len(results) > 0

        for chunk, doc, distance in results:
            assert doc.is_approved is True
            assert doc.id == document.id
            assert distance <= 0.6

    finally:
        db.close()


def test_rag_ignores_unsupported_question():
    db = SessionLocal()

    try:
        results = search_knowledge(
            db,
            "What is the swimming pool temperature?",
        )

        assert results == []

    finally:
        db.close()


def test_chat_returns_breakfast_answer_with_sources():
    token = get_guest_token()

    response = client.post(
        "/chat",
        json={
            "question": "What time is breakfast?"
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "breakfast" in data["answer"].lower()
    assert "7:00 AM" in data["answer"]
    assert "10:00 AM" in data["answer"]

    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0

    for source in data["sources"]:
        assert source["title"] == "Hotel Breakfast Policy"
        assert source["file_name"] == "hottle_policy.txt"


def test_chat_returns_safe_no_answer_for_unknown_question():
    token = get_guest_token()

    response = client.post(
        "/chat",
        json={
            "question": "What is the swimming pool temperature?"
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "don't have enough information" in data["answer"].lower()
    assert data["sources"] == []