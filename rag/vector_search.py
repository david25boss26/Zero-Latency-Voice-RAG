import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorSearch:
    def __init__(self):
        self.index = faiss.read_index("data/faiss.index")
        self.chunks = json.load(open("data/chunks.json", "r", encoding="utf-8"))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(self, query, k= 5):
        q_emb = self.model.encode([query]).astype("float32")
        D, I = self.index.search(q_emb, k)
        return [self.chunks[i] for i in I[0]]