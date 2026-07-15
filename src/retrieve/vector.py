"""Phase 3 retrieval: pure pgvector semantic search (working).
Phase 4 upgrades this via bm25.py + hybrid.py + rerank.py.
"""
from src import db
from src.ingest.chunk import embed


def vector_search(question: str, top_k: int = 20) -> list[dict]:
    qvec = embed([question])[0]
    sql = """
        SELECT c.id, c.text, f.ticker, f.company, f.section, f.filing_date,
               1 - (c.embedding <=> %s::vector) AS score
        FROM chunks c JOIN filings f ON f.id = c.filing_id
        ORDER BY c.embedding <=> %s::vector
        LIMIT %s
    """
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (qvec, qvec, top_k))
        cols = [d.name for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
