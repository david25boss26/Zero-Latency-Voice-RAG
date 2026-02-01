from .vector_search import VectorSearch
from .bm25_search import BM25Search
from .reranker import Reranker

class HybridSearch:
    def __init__(self):
        self.vector = VectorSearch()
        self.bm25 = BM25Search()
        self.reranker = Reranker()

    def search(self, query, k=5):

        candidate_k = max(50, k*10)
        v_hits = self.vector.search(query, k=20)
        b_hits = self.bm25.search(query, k=20)

        pool = {}
        for d in v_hits + b_hits:
            key = d.get("id")
            if key is None:
                key = f"{d.get('page', '')}:{hash(d.get('text', ''))}"
            pool[key] = d
            

        merged = list(pool.values())
        reranked = self.reranker.rerank(query, merged, top_n=20)

        return reranked[:k]



# from rag.vector_search import VectorSearch
# from rag.bm25_search import BM25Search

# class HybridSearch:
    # def __init__(self):
        # self.vec = VectorSearch()
        # self.bm25 = BM25Search()

    # def search(self, query, k=5):
        # v = self.vec.search(query, k)
        # b = self.bm25.search(query, k)
        # merged = list(dict.fromkeys(v + b))
        # return merged[:k]
    