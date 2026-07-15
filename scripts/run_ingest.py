"""Phase 1: download + parse 10-Ks into the filings table."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.ingest.download import latest_10k
from src.ingest.parse import html_to_text, split_sections
from src.db import insert_filing

# Start small; scale this list (and add more years) in the final phase.
TICKERS = ["AAPL", "MSFT", "TSLA", "F", "WMT", "AMZN", "NVDA", "JPM", "PFE", "KO"]

if __name__ == "__main__":
    for ticker in TICKERS:
        print(f"{ticker}...")
        result = latest_10k(ticker)
        if not result:
            continue
        company, date, url, html = result
        sections = split_sections(html_to_text(html))
        for title, body in sections.items():
            insert_filing(ticker, company, "10-K", date, title, url, body)
        print(f"  stored {len(sections)} sections")
    print("Ingest complete.")
