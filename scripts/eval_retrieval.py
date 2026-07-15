"""Retrieval evaluation: measures whether the right chunks are retrieved
for a gold set of questions. Run before/after retrieval changes.

Usage:
    python scripts/eval_retrieval.py vector
    python scripts/eval_retrieval.py hybrid
    python scripts/eval_retrieval.py hybrid+rerank
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieve.vector import vector_search
from src.retrieve.hybrid import hybrid_search
from src.retrieve.rerank import rerank

PIPELINES = {
    "vector": lambda q, k: vector_search(q, top_k=k),
    "hybrid": lambda q, k: hybrid_search(q, top_k=k),
    "hybrid+rerank": lambda q, k: rerank(q, hybrid_search(q, top_k=30), top_k=k),
}

# Gold set: (question, expected_ticker, expected_section_keyword)
# A retrieved chunk counts as a "hit" if ticker matches and the
# section contains the keyword.
GOLD = [
    ("What are Apple's main risk factors?",            "AAPL", "Risk Factors"),
    ("What products does Apple sell?",                 "AAPL", "Business"),
    ("What are Nvidia's main risk factors?",           "NVDA", "Risk Factors"),
    ("What does Nvidia's data center business do?",    "NVDA", "Business"),
    ("How does Apple describe competition?",           "AAPL", "Risk Factors"),
    ("What supply chain risks does Nvidia face?",      "NVDA", "Risk Factors"),
    ("Summarize Apple's financial performance",        "AAPL", "Financial"),
    ("What legal proceedings is Apple involved in?",   "AAPL", "Legal"),
    # Add more -- aim for 12-15 covering every company/section you ingested
]

K = 5  # evaluate top-k


def is_hit(chunk, ticker, section_kw):
    return chunk["ticker"] == ticker and section_kw.lower() in chunk["section"].lower()


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "vector"
    if name not in PIPELINES:
        print(f"Unknown pipeline '{name}'. Options: {', '.join(PIPELINES)}")
        sys.exit(1)
    search = PIPELINES[name]

    print(f"Pipeline: {name}\n")
    recall_hits, mrr_total = 0, 0.0
    for question, ticker, section_kw in GOLD:
        chunks = search(question, K)
        ranks = [i for i, c in enumerate(chunks, start=1) if is_hit(c, ticker, section_kw)]
        recall_hits += bool(ranks)
        mrr_total += (1.0 / ranks[0]) if ranks else 0.0
        status = f"hit@{ranks[0]}" if ranks else "MISS"
        print(f"[{status:>6}] {question}")

    n = len(GOLD)
    print(f"\nRecall@{K}: {recall_hits}/{n} = {recall_hits/n:.2f}")
    print(f"MRR@{K}:   {mrr_total/n:.3f}")


if __name__ == "__main__":
    main()