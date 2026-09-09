from app.db.session import SessionLocal
from app.rag.search import search_knowledge


db = SessionLocal()

try:
    question = "What is the swimming pool temperature?"

    results = search_knowledge(
        db,
        question,
        limit=2,
    )

    print("Question:", question)
    print("Relevant results:", len(results))

    for index, (chunk, distance) in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print("Document ID:", chunk.document_id)
        print("Chunk index:", chunk.chunk_index)
        print("Distance:", distance)
        print("Content:", chunk.content)

finally:
    db.close()