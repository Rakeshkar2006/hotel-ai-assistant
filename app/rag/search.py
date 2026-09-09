from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.knowledge_document import KnowledgeDocument
from app.db.models.knowledge_document_chunk import KnowledgeDocumentChunk


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def search_knowledge(
    db: Session,
    query: str,
    limit: int = 10,
    max_distance: float = 0.6,
):
    query_embedding = model.encode(query).tolist()

    distance = KnowledgeDocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    results = db.execute(
        select(
            KnowledgeDocumentChunk,
            KnowledgeDocument,
            distance.label("distance"),
        )
        .join(
            KnowledgeDocument,
            KnowledgeDocument.id == KnowledgeDocumentChunk.document_id,
        )
        .where(
            KnowledgeDocument.is_approved.is_(True)
        )
        .order_by(distance)
        .limit(limit)
    ).all()

    relevant_results = []

    for row in results:
        chunk = row[0]
        document = row[1]
        chunk_distance = row[2]

        if chunk_distance <= max_distance:
            relevant_results.append(
                (chunk, document, chunk_distance)
            )

    return relevant_results