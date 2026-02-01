import json
import os
from pypdf import PdfReader
from tqdm import tqdm

PDF_PATH = "../data/manual.pdf"
OUT_PATH = "../data/chunks.json"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def main():
    print("Loading PDF...")

    if not os.path.exists(PDF_PATH):
        print("❌ PDF not found at", PDF_PATH)
        return

    reader = PdfReader(PDF_PATH)
    print(f"PDF loaded. Pages: {len(reader.pages)}")

    all_chunks = []
    chunk_id = 0  

    for page_num, page in enumerate(tqdm(reader.pages)):
        try:
            text = page.extract_text()
            if not text or len(text.strip()) < 50:
                continue

            chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

            for c in chunks:
                all_chunks.append({
                    "id": chunk_id,      
                    "text": c,
                    "page": page_num
                })
                chunk_id += 1

        except Exception as e:
            print(f"Error on page {page_num}: {e}")

    print(f"Total chunks created: {len(all_chunks)}")

    os.makedirs("../data", exist_ok=True)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print("✅ Saved chunks to", OUT_PATH)
    print("DONE")


if __name__ == "__main__":
    main()
