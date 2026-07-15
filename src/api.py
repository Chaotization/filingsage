"""FastAPI entrypoint. POST /ask {"question": "..."}"""
from fastapi import FastAPI
from pydantic import BaseModel
from src import config
from src.answer.generate import answer
from src.retrieve.hybrid import hybrid_search
from src.retrieve.rerank import rerank

app = FastAPI(title="FilingSage")


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(req: AskRequest):
    # Phase 4: hybrid retrieval (BM25 + vector, RRF) + cross-encoder reranking
    chunks = rerank(req.question, hybrid_search(req.question, top_k=30), top_k=config.TOP_K)
    if not chunks:
        return {"answer": "No documents indexed yet.", "sources": []}
    return {
        "answer": answer(req.question, chunks),
        "sources": [
            {"ticker": c["ticker"], "section": c["section"], "score": round(float(c["score"]), 3)}
            for c in chunks
        ],
    }