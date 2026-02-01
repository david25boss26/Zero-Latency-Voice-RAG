import json
import pickle
import numpy as np
import faiss
from tqdm import tqdm
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

print("Loading chunks...")
chunks = json.load(open("../data/chunks.json", "r", encoding="utf-8"))

texts = [c["text"] for c in chunks]

print("loading embedding models...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("computing embeddings...")
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

embeddings = np.array(embeddings).astype("float32")

print("building FAISS index...")
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

faiss.write_index(index, "../data/faiss.index")

print("building BM25 index...")
tokenized = [t.split() for t in texts]
bm25 = BM25Okapi(tokenized)

with open("../data/bm25.pkl", "wb") as f:
    pickle.dump(bm25, f)

print("✅ All indexes built successfully!")
