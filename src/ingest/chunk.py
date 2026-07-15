"""Word-window chunking (~500 tokens with overlap) and local embeddings."""
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from src import config


def chunk_text(text: str) -> list[str]:
    words = text.split()
    step = config.CHUNK_WORDS - config.CHUNK_OVERLAP_WORDS
    chunks = []
    for start in range(0, len(words), step):
        piece = " ".join(words[start : start + config.CHUNK_WORDS])
        if len(piece) > 200:  # skip trailing slivers
            chunks.append(piece)
    return chunks


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBED_MODEL)


def embed(texts: list[str]):
    """Return list of 384-dim vectors. Batched; CPU-friendly."""
    return _model().encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
