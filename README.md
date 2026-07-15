<<<<<<< HEAD
# FilingSage — Hybrid RAG Research Assistant over SEC Filings

Ask natural-language questions over SEC 10-K filings and get citation-grounded answers.

Pipeline: EDGAR ingestion → section parsing → chunking → local embeddings (sentence-transformers)
→ pgvector semantic search → grounded generation via the OpenAI API.

Phases 4–6 (hybrid BM25 + reranking, agentic query decomposition, eval harness) have stubs in place.

---

## Phase 0 — Setup (do this first)

Works on Windows, macOS, and Linux. Windows commands below assume **PowerShell**.

1. Install:
   - Python 3.10+ — on Windows, from python.org; check "Add python.exe to PATH" during install
   - **Docker Desktop** — on Windows it requires the WSL 2 backend (the installer sets this up;
     if prompted, run `wsl --install` in an admin PowerShell and reboot)

2. Start Postgres with pgvector (same on all platforms):
   ```
   docker compose up -d
   ```

3. Create a virtualenv and install dependencies:

   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   If activation is blocked by execution policy, run once:
   `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

   **macOS/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   Note: the first install pulls PyTorch (CPU) for sentence-transformers — it's large
   (~200MB+); let it finish.

4. Copy `.env.example` to `.env` and fill in:
   - `OPENAI_API_KEY` — from https://platform.openai.com (API keys page; add ~$5 billing credit)
   - `SEC_USER_AGENT` — SEC requires a contact string, e.g. "Chao Zheng czheng1735@gmail.com"

   Windows copy command: `copy .env.example .env`   (macOS/Linux: `cp .env.example .env`)

5. Initialize the database schema:
   ```
   python scripts/init_db.py
   ```

## Phase 1 — Ingest filings

Download and parse 10-Ks for the tickers in `scripts/run_ingest.py` (start with ~10, scale later):

```bash
python scripts/run_ingest.py
```

This downloads each company's latest 10-K from EDGAR, strips HTML, splits it into
Items (1, 1A, 7, 7A, 8...), and stores sections in Postgres.

## Phase 2 — Chunk + embed

```bash
python scripts/run_embed.py
```

Splits sections into ~500-token chunks with overlap, embeds them locally with
sentence-transformers (all-MiniLM-L6-v2, 384-dim, CPU-friendly), and writes vectors to pgvector.
First run downloads the model (~90MB). Embedding is the slow step — let it run.

## Phase 3 — Ask questions

Start the API (all platforms):
```
uvicorn src.api:app --reload
```

Ask a question from a second terminal (cross-platform — avoids curl quoting issues on Windows):
```
python scripts/ask.py "What are the main risk factors Apple discusses?"
```

You get an answer grounded in retrieved chunks with citations, or a refusal when
the context is insufficient (try asking about a company you did not ingest).

## Phase 4 — Hybrid retrieval (your next build step)

Implement `src/retrieve/bm25.py` and merge with vector results using Reciprocal Rank Fusion
in `src/retrieve/hybrid.py` (skeleton provided), then add cross-encoder reranking in
`src/retrieve/rerank.py`. Why: embeddings miss exact terms (tickers, dollar figures);
BM25 catches them; the cross-encoder re-scores a shortlist far more accurately.

## Phase 5 — Agentic query decomposition

Implement `src/answer/decompose.py`: one model call classifies the question, splits
multi-hop questions ("compare X and Y risk factors") into sub-queries, runs each through
retrieval, then synthesizes a final cited answer.

## Phase 6 — Evaluation harness

Fill `src/eval/questions.json` with 25–40 Q/A pairs from your corpus, then build
`src/eval/harness.py` to score faithfulness and context precision with an LLM-as-judge
call. Use the scores to tune chunk size, retrieval depth, and reranking.

---

## Repo layout

```
filingsage/
├── docker-compose.yml        # Postgres + pgvector
├── requirements.txt
├── .env.example
├── scripts/
│   ├── init_db.py            # create tables + indexes
│   ├── run_ingest.py         # Phase 1: download + parse filings
│   └── run_embed.py          # Phase 2: chunk + embed
└── src/
    ├── config.py
    ├── db.py
    ├── api.py                # FastAPI /ask endpoint
    ├── ingest/
    │   ├── download.py       # EDGAR client
    │   ├── parse.py          # HTML → sections
    │   └── chunk.py
    ├── retrieve/
    │   ├── vector.py         # pgvector search (working)
    │   ├── bm25.py           # Phase 4 stub
    │   ├── hybrid.py         # Phase 4 stub (RRF skeleton)
    │   └── rerank.py         # Phase 4 stub
    ├── answer/
    │   ├── generate.py       # OpenAI API grounded answer (working)
    │   └── decompose.py      # Phase 5 stub
    └── eval/
        ├── questions.json    # Phase 6: your test set
        └── harness.py        # Phase 6 stub
```
=======
# filingsage
>>>>>>> b3a35c7c5cd4d241be94856344b7cd3a617c54b0
