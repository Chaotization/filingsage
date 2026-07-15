"""Phase 4 TODO: BM25 keyword retrieval.

Plan:
  1. Load (chunk_id, text) from Postgres once at startup; tokenize simply (lowercase, split).
  2. Build rank_bm25.BM25Okapi over the corpus.
  3. bm25_search(question, top_k) -> [{'id': ..., 'score': ...}] by BM25 score.

Why: embeddings miss exact terms (ticker symbols, dollar figures, named products).
BM25 catches them. You merge both result lists in hybrid.py.
"""
