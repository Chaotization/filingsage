"""FastAPI entrypoint. POST /ask {"question": "..."}"""
from fastapi import FastAPI
from pydantic import BaseModel
from src import config
from src.retrieve.vector import vector_search
from src.answer.generate import answer

app = FastAPI(title="FilingSage")


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(req: AskRequest):
    # Phase 3: pure vector retrieval. Phase 4: swap in hybrid.search().
    chunks = vector_search(req.question, top_k=config.TOP_K)
    if not chunks:
        return {"answer": "No documents indexed yet.", "sources": []}
    return {
        "answer": answer(req.question, chunks),
        "sources": [
            {"ticker": c["ticker"], "section": c["section"], "score": round(float(c["score"]), 3)}
            for c in chunks
        ],
    }
