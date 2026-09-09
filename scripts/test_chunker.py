from app.rag.chunker import chunk_text


text = """
Hotel Breakfast Policy

Breakfast is served every day from 7:00 AM to 10:00 AM.

Guests can have breakfast in the hotel restaurant.

Breakfast is included for all guests staying at the hotel.
"""


chunks = chunk_text(text, chunk_size=100)

print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(chunk)