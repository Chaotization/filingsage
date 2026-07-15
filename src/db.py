"""Postgres + pgvector access. Two tables: filings (one row per 10-K section source)
and chunks (embedded passages)."""
import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector
from src import config


def get_conn():
    conn = psycopg2.connect(config.DATABASE_URL)
    register_vector(conn)
    return conn


SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS filings (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    company TEXT,
    form TEXT NOT NULL,             -- e.g. 10-K
    filing_date DATE,
    section TEXT NOT NULL,          -- e.g. 'Item 1A. Risk Factors'
    url TEXT,
    body TEXT NOT NULL,
    UNIQUE (ticker, form, filing_date, section)
);

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    filing_id INT REFERENCES filings(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    text TEXT NOT NULL,
    embedding vector({config.EMBED_DIM})
);

-- HNSW index for fast approximate cosine search
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""


def init_schema():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(SCHEMA)
    print("Schema ready.")


def insert_filing(ticker, company, form, filing_date, section, url, body) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO filings (ticker, company, form, filing_date, section, url, body)
               VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (ticker, form, filing_date, section) DO UPDATE SET body = EXCLUDED.body
               RETURNING id""",
            (ticker, company, form, filing_date, section, url, body),
        )
        return cur.fetchone()[0]


def insert_chunks(filing_id, texts, embeddings):
    rows = [(filing_id, i, t, e) for i, (t, e) in enumerate(zip(texts, embeddings))]
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM chunks WHERE filing_id = %s", (filing_id,))
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO chunks (filing_id, chunk_index, text, embedding) VALUES %s",
            rows,
        )


def sections_without_chunks():
    """Filings whose sections have not been embedded yet."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT f.id, f.ticker, f.section, f.body FROM filings f
               LEFT JOIN chunks c ON c.filing_id = f.id
               WHERE c.id IS NULL"""
        )
        return cur.fetchall()
