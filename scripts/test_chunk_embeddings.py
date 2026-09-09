from pathlib import Path

from sentence_transformers import SentenceTransformer

from app.rag.chunker import chunk_text


file_path = Path("data/storage/hotel_policy.txt")

text = file_path.read_text(encoding="utf-8")

chunks = chunk_text(text, chunk_size=100)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embeddings = model.encode(chunks)

print("Embeddings created successfully!")
print("Number of chunks:", len(chunks))

for index, embedding in enumerate(embeddings, start=1):
    print(f"\n--- Chunk {index} ---")
    print("Vector dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])