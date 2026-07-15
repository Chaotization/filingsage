import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.db import init_schema

if __name__ == "__main__":
    init_schema()
