from sqlalchemy import select

from app.db.models.knowledge_document_chunk import KnowledgeDocumentChunk
from app.db.session import SessionLocal


DOCUMENT_ID = 2


db = SessionLocal()

try:
    chunks = db.scalars(
        select(KnowledgeDocumentChunk)
        .where(KnowledgeDocumentChunk.document_id == DOCUMENT_ID)
        .order_by(KnowledgeDocumentChunk.chunk_index)
    ).all()

    print("Indexed chunks found:", len(chunks))

    for chunk in chunks:
        print(f"\n--- Chunk {chunk.chunk_index + 1} ---")
        print("Document ID:", chunk.document_id)
        print("Content:", chunk.content)
        print("Embedding dimensions:", len(chunk.embedding))

finally:
    db.close()