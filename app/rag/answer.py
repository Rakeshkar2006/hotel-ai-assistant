import os

from groq import Groq
from sqlalchemy.orm import Session

from app.rag.search import search_knowledge


def generate_groq_answer(
    question: str,
    context: str,
) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return context

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a hotel guest service assistant. "
                    "Answer only from the provided hotel information. "
                    "Do not invent or assume information. "
                    "If the information is not available in the context, "
                    "say that you do not have enough information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Hotel information:\n{context}\n\n"
                    f"Guest question:\n{question}"
                ),
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content


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
            "answer": (
                "Sorry, I don't have enough information "
                "in the approved hotel documents to answer this question."
            ),
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
    relevant_results.sort(
        key=lambda result: result[0].chunk_index
    )

    context = " ".join(
        chunk.content
        for chunk, document, distance in relevant_results
    )

    llm_provider = os.getenv(
        "LLM_PROVIDER",
        "retrieval_only",
    )

    if llm_provider == "groq":
        try:
            answer = generate_groq_answer(
                question,
                context,
            )
        except Exception:
            # Safe fallback if Groq is unavailable.
            answer = context
    else:
        # Retrieval-only mode.
        answer = context

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