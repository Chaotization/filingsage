"""Central config loaded from .env"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://filingsage:dev@localhost:5432/filingsage")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "FilingSage dev@example.com")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5.6-luna")

EMBED_DIM = 384          # all-MiniLM-L6-v2 output size
CHUNK_WORDS = 380        # ~500 tokens
CHUNK_OVERLAP_WORDS = 40
TOP_K = 8                # chunks fed to the LLM
