"""Cross-encoder reranking: scores each (question, chunk) pair jointly —
slower but far more precise than embedding similarity. Applied to a small
candidate set from hybrid retrieval."""
from sentence_transformers import CrossEncoder

_model = None

def rerank(question: str, chunks: list[dict], top_k: int = 8) -> list[dict]:
    global _model
    if _model is None:
        _model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    scores = _model.predict([(question, c["text"]) for c in chunks])
    for c, s in zip(chunks, scores):
        c["score"] = float(s)
    return sorted(chunks, key=lambda c: c["score"], reverse=True)[:top_k]