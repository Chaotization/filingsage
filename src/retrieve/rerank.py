"""Phase 4 TODO: cross-encoder reranking.

from sentence_transformers import CrossEncoder
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
scores = model.predict([(question, chunk_text), ...])

Sort candidates by score, keep top_k. Slower than bi-encoders, so only run it
on the ~25 fused candidates, never the whole corpus.
"""
