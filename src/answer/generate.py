"""Grounded answer generation via the OpenAI API (Phase 3, working).

Contract: answer ONLY from retrieved chunks, cite sources, refuse when the
context is insufficient.
"""
from openai import OpenAI
from src import config

SYSTEM = """You are a research assistant answering questions about SEC filings.
Rules:
- Answer ONLY from the provided context passages.
- Cite each claim with its source in the form [ticker, section].
- If the context does not contain enough information to answer, say exactly:
  "I don't have enough information in the indexed filings to answer that." Do not guess.
- Be concise and factual."""


def build_context(chunks: list[dict]) -> str:
    blocks = []
    for i, c in enumerate(chunks, 1):
        blocks.append(
            f"[{i}] ({c['ticker']}, {c['section']}, filed {c['filing_date']})\n{c['text']}"
        )
    return "\n\n---\n\n".join(blocks)


def answer(question: str, chunks: list[dict]) -> str:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=config.CHAT_MODEL,
        max_completion_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": f"Context passages:\n\n{build_context(chunks)}\n\nQuestion: {question}",
            },
        ],
    )
    return resp.choices[0].message.content
