from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

text = "Breakfast is served every day from 7:00 AM to 10:00 AM."

embedding = model.encode(text)

print("Embedding created successfully!")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])