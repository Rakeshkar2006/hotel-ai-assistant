import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sqlalchemy import delete

from app.db.models.knowledge_document import KnowledgeDocument
from app.db.models.knowledge_document_chunk import KnowledgeDocumentChunk
from app.db.session import SessionLocal
from app.rag.chunker import chunk_text


def index_document(document_id: int):
    db = SessionLocal()

    try:
        document = db.get(KnowledgeDocument, document_id)

        if document is None:
            print("Error: Document not found.")
            return

        if not document.is_approved:
            print("Error: Document is not approved.")
            return

        file_path = Path(document.file_path)

        if not file_path.exists():
            print("Error: Document file not found.")
            return

        text = file_path.read_text(encoding="utf-8")

        chunks = chunk_text(text, chunk_size=100)

        if not chunks:
            print("Error: Document contains no readable text.")
            return

        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        embeddings = model.encode(chunks)

        # Remove old chunks before re-indexing
        db.execute(
            delete(KnowledgeDocumentChunk).where(
                KnowledgeDocumentChunk.document_id == document_id
            )
        )

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            db.add(
                KnowledgeDocumentChunk(
                    document_id=document_id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding.tolist(),
                )
            )

        db.commit()

        print("Document indexed successfully!")
        print("Document ID:", document_id)
        print("Document title:", document.title)
        print("Number of chunks saved:", len(chunks))

    except Exception as error:
        db.rollback()
        print("Error:", error)

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.index_document <document_id>")
        sys.exit(1)

    index_document(int(sys.argv[1]))