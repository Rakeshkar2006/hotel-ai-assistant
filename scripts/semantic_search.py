from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.db.models.knowledge_document_chunk import KnowledgeDocumentChunk
from app.db.session import SessionLocal


QUESTION = "What time is breakfast?"


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

question_embedding = model.encode(QUESTION).tolist()

db = SessionLocal()

try:
    distance = KnowledgeDocumentChunk.embedding.cosine_distance(
        question_embedding
    )

    results = db.scalars(
        select(KnowledgeDocumentChunk)
        .order_by(distance)
        .limit(2)
    ).all()

    print("Question:", QUESTION)
    print("\nMost relevant chunks:")

    for index, chunk in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print("Chunk index:", chunk.chunk_index)
        print("Content:", chunk.content)

finally:
    db.close()