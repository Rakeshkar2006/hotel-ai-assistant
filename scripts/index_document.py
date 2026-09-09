from pathlib import Path

from sentence_transformers import SentenceTransformer
from sqlalchemy import delete

from app.db.models.knowledge_document_chunk import KnowledgeDocumentChunk
from app.db.session import SessionLocal
from app.rag.chunker import chunk_text


DOCUMENT_ID = 3
FILE_PATH = Path("data/storage/Hotel Check-in Policy.txt")


def index_document():
    text = FILE_PATH.read_text(encoding="utf-8")

    chunks = chunk_text(text, chunk_size=100)

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    embeddings = model.encode(chunks)

    db = SessionLocal()

    try:
        # Remove old chunks for this document before re-indexing
        db.execute(
            delete(KnowledgeDocumentChunk).where(
                KnowledgeDocumentChunk.document_id == DOCUMENT_ID
            )
        )

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            db.add(
                KnowledgeDocumentChunk(
                    document_id=DOCUMENT_ID,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding.tolist(),
                )
            )

        db.commit()

        print("Document indexed successfully!")
        print("Document ID:", DOCUMENT_ID)
        print("Number of chunks saved:", len(chunks))

    except Exception as error:
        db.rollback()
        print("Error:", error)

    finally:
        db.close()


if __name__ == "__main__":
    index_document()