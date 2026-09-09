from pathlib import Path

from app.rag.chunker import chunk_text


file_path = Path("data/storage/hotel_policy.txt")

text = file_path.read_text(encoding="utf-8")

chunks = chunk_text(text, chunk_size=100)

print("Document read successfully!")
print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(chunk)