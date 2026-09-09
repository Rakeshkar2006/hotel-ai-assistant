from sqlalchemy.orm import Session

from app.rag.search import search_knowledge


def answer_question(
    db: Session,
    question: str,
):
    results = search_knowledge(
        db,
        question,
        limit=10,
    )

    if not results:
        return {
            "answer": "Sorry, I don't have enough information in the approved hotel documents to answer this question.",
            "sources": [],
        }

    # The best result decides which document is relevant.
    best_chunk, best_document, best_distance = results[0]

    # Use chunks only from the same document as the best result.
    relevant_results = [
        result
        for result in results
        if result[1].id == best_document.id
    ]

    # Sort chunks in their original document order.
    relevant_results.sort(key=lambda result: result[0].chunk_index)

    answer = " ".join(
        chunk.content
        for chunk, document, distance in relevant_results
    )

    sources = [
        {
            "document_id": document.id,
            "title": document.title,
            "file_name": document.file_name,
            "chunk_index": chunk.chunk_index,
            "distance": float(distance),
        }
        for chunk, document, distance in relevant_results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }