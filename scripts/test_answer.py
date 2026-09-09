from app.db.session import SessionLocal
from app.rag.answer import answer_question


db = SessionLocal()

try:
    question = "What time is breakfast?"

    result = answer_question(db, question)

    print("\n=== ANSWER ===")
    print(result["answer"])

    print("\n=== SOURCES ===")

    for source in result["sources"]:
        print(source)

finally:
    db.close()