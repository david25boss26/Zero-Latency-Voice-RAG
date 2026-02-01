from __future__ import annotations

from typing import List,Dict,Any
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        print("loading cross encoder reranker...")
        self.model = CrossEncoder(model_name)

    def rerank(
            self,
            query: str,
            docs: List[Dict[str, Any]],
            top_n: int = 20,
            batch_size: int = 16,
    ) -> List[Dict[str, Any]]:
        """
        Rerank only top_n docs (already retrieved by hybrid).
        Returns a NEW list (does not mutate original docs). 
        """

        if not docs:
            return []
        
        cleaned = []
        for d in docs:
            t = (d.get("text") or "").strip()
            if t:
                cleaned.append(d)

        if not cleaned:
            return []
        
        candidate_docs = cleaned[:top_n]

        pairs = [(query, d["text"]) for d in candidate_docs]

        scores = self.model.predict(pairs, batch_size=batch_size)

        scored = []
        for d, s in zip(candidate_docs, scores):
            nd = dict(d)
            nd["score"] = float(s)
            scored.append(nd)

        scored.sort(key = lambda x: x["score"], reverse=True)

        if len(cleaned) > top_n:
            scored.extend(cleaned[top_n:])

        return scored