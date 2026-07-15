"""Phase 4 TODO: merge vector + BM25 results with Reciprocal Rank Fusion, then rerank.

RRF skeleton:

def rrf(result_lists, k=60):
    scores = {}
    for results in result_lists:            # each: list of chunk ids in rank order
        for rank, chunk_id in enumerate(results):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)

Pipeline: vector_search(q, 25) + bm25_search(q, 25) -> rrf -> top 25 -> rerank.rerank(q, top25) -> top 8.
"""
