# FilingSage

Ask questions about SEC filings in plain English, get answers with citations.

FilingSage is a Retrieval-Augmented Generation (RAG) pipeline that ingests 10-K filings from SEC EDGAR, chunks and embeds them into PostgreSQL with pgvector, and answers natural-language questions through a FastAPI service backed by OpenAI.

## Example

```
$ python scripts/ask.py "What are Apple's main risk factors?"

ANSWER:
Apple's main risk factors include adverse economic conditions, geopolitical
and trade disruptions (tariffs, export controls), supply-chain dependence on
outsourcing partners and single-source components, intense competition and
rapid technological change, ...

SOURCES:
  - AAPL | Item 1A. Risk Factors (score 0.598)
  - AAPL | Item 1A. Risk Factors (score 0.567)
  - AAPL | Item 1. Business      (score 0.553)
```

## Architecture

```
SEC EDGAR ──▶ Ingest ──▶ Section-aware chunking ──▶ Embeddings ──▶ pgvector (Postgres 16)
                                                    (MiniLM-L6)          │
                                                                         ▼
User question ──▶ FastAPI /ask ──▶ Vector similarity search ──▶ Top-k chunks
                                                                         │
                                                                         ▼
                                                     OpenAI chat completion ──▶ Answer + sources
```

**Stack:** Python 3.13 · FastAPI · PostgreSQL 16 + pgvector · sentence-transformers (`all-MiniLM-L6-v2`) · OpenAI API · Docker Compose

## Setup

### Prerequisites

- Python 3.11+
- Docker Desktop
- An OpenAI API key ([platform.openai.com](https://platform.openai.com) — note: API credits are separate from ChatGPT Plus)

### 1. Clone and configure

```bash
git clone https://github.com/Chaotization/filingsage.git
cd filingsage
cp .env.example .env   # then edit .env with your values
```

`.env` contents:

```
OPENAI_API_KEY=sk-...
SEC_USER_AGENT=Your Name your@email.com   # required by SEC EDGAR
DATABASE_URL=postgresql://filingsage:dev@localhost:5433/filingsage
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHAT_MODEL=gpt-5-mini
```

### 2. Start the database

```bash
docker compose up -d
docker exec filingsage-db-1 psql -U filingsage -d filingsage -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 3. Install dependencies

```bash
python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Build the index

```bash
python scripts/init_db.py      # create tables
python scripts/run_ingest.py   # download filings from SEC EDGAR
python scripts/run_embed.py    # chunk + embed into pgvector
```

### 5. Run

```bash
# Terminal 1 — API server
uvicorn src.api:app --reload

# Terminal 2 — ask questions
python scripts/ask.py "Compare Apple and Nvidia's supply chain risks"
```

Interactive API docs available at http://localhost:8000/docs.

## Project structure

```
filingsage/
├── docker-compose.yml      # Postgres 16 + pgvector
├── requirements.txt
├── scripts/
│   ├── init_db.py          # schema creation
│   ├── run_ingest.py       # SEC EDGAR download
│   ├── run_embed.py        # chunking + embedding
│   └── ask.py              # CLI test client
└── src/
    ├── api.py              # FastAPI app (/ask endpoint)
    ├── config.py            # env-driven configuration
    ├── db.py               # connection + schema
    ├── retrieve/           # vector search
    └── answer/             # prompt assembly + OpenAI generation
```

## Implementation notes & gotchas

Real issues hit while building this, kept here for anyone reproducing the setup:

- **Port 5432 conflicts.** If a native PostgreSQL is installed on the host, it silently intercepts connections meant for the Docker container, producing misleading `password authentication failed` errors. This project maps the container to **5433** to avoid the collision.
- **pgvector must be enabled per database.** The `pgvector/pgvector` image ships the extension but does not activate it — `CREATE EXTENSION vector` is required once per database (and again after `docker compose down -v`).
- **psycopg2 can't adapt `numpy.float32`.** Query vectors must be passed as numpy arrays to a connection registered with `pgvector.psycopg2.register_vector` — converting them to Python lists first breaks adaptation.
- **`max_tokens` is deprecated on newer OpenAI models.** Use `max_completion_tokens` in chat completion calls.
- **SEC EDGAR requires a User-Agent** identifying you (name + email) or requests get throttled/blocked.

## Roadmap

- [ ] Ticker-aware filtering (prevent cross-company chunks bleeding into answers)
- [ ] Hybrid retrieval: BM25 + vector scores with reciprocal rank fusion
- [ ] Cross-encoder reranking of top candidates
- [ ] Retrieval evaluation harness (recall@k over a gold question set)
- [ ] Multi-year filings and change-over-time questions
- [ ] Streaming responses (SSE)

## License

MIT
