"""BM25 keyword search over all chunks. Index built in-memory on first use
(~1.2k chunks, negligible memory)."""
import re
from rank_bm25 import BM25Okapi
from src import db

_index = None
_chunks = None

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

def _load():
    global _index, _chunks
    if _index is not None:
        return
    sql = """
        SELECT c.id, c.text, f.ticker, f.company, f.section, f.filing_date
        FROM chunks c JOIN filings f ON f.id = c.filing_id
    """
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        cols = [d.name for d in cur.description]
        _chunks = [dict(zip(cols, row)) for row in cur.fetchall()]
    _index = BM25Okapi([_tokenize(c["text"]) for c in _chunks])

def bm25_search(question: str, top_k: int = 20) -> list[dict]:
    _load()
    scores = _index.get_scores(_tokenize(question))
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [{**_chunks[i], "score": float(scores[i])} for i in ranked]