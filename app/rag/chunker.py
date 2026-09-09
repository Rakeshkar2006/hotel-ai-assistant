def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """
    Split text into small chunks without cutting words in half.
    """

    text = text.strip()

    if not text:
        return []

    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word)

        if current_chunk and current_length + 1 + word_length > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

        current_chunk.append(word)
        current_length += word_length

        if len(current_chunk) > 1:
            current_length += 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks