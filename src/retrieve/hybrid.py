"""Hybrid retrieval: vector + BM25 fused with Reciprocal Rank Fusion.
RRF score = sum over rankings of 1/(K + rank). Rank-based, so the two
systems' incomparable score scales don't matter."""
from src.retrieve.vector import vector_search
from src.retrieve.bm25 import bm25_search

RRF_K = 60

def hybrid_search(question: str, top_k: int = 20, fetch_k: int = 30) -> list[dict]:
    fused: dict = {}
    for results in (vector_search(question, fetch_k), bm25_search(question, fetch_k)):
        for rank, chunk in enumerate(results, start=1):
            entry = fused.setdefault(chunk["id"], {**chunk, "score": 0.0})
            entry["score"] += 1.0 / (RRF_K + rank)
    ranked = sorted(fused.values(), key=lambda c: c["score"], reverse=True)
    return ranked[:top_k]