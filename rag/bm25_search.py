import pickle
import json

class BM25Search:
    def __init__(self):
        self.bm25 = pickle.load(open("data/bm25.pkl", "rb"))
        self.chunks = json.load(open("data/chunks.json", "r", encoding="utf-8"))

    def search(self, query, k=5):
        scores = self.bm25.get_scores(query.split())
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self.chunks[i] for i in ranked[:k]]
    
    