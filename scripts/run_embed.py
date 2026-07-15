"""Phase 2: chunk + embed all sections that don't have chunks yet."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.db import sections_without_chunks, insert_chunks
from src.ingest.chunk import chunk_text, embed

if __name__ == "__main__":
    pending = sections_without_chunks()
    print(f"{len(pending)} sections to embed")
    for filing_id, ticker, section, body in pending:
        chunks = chunk_text(body)
        if not chunks:
            continue
        vectors = embed(chunks)
        insert_chunks(filing_id, chunks, vectors)
        print(f"  {ticker} | {section}: {len(chunks)} chunks")
    print("Embedding complete.")
