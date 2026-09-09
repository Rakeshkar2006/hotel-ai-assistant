from pathlib import Path

file_path = Path("data/storage/hotel_policy.txt")

text = file_path.read_text(encoding="utf-8")

print("Document read successfully!")
print("Characters:", len(text))
print("\n--- Document Content ---")
print(text)