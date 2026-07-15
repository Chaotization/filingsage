"""EDGAR client — downloads the latest 10-K for a ticker.

EDGAR is free but requires a User-Agent identifying you (set SEC_USER_AGENT in .env)
and asks for <=10 requests/sec; we sleep between calls to be polite.
"""
import time
import requests
from src import config

HEADERS = {"User-Agent": config.SEC_USER_AGENT}
TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:0>10}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}"

_ticker_map = None


def _load_ticker_map():
    global _ticker_map
    if _ticker_map is None:
        data = requests.get(TICKER_URL, headers=HEADERS, timeout=30).json()
        _ticker_map = {v["ticker"].upper(): v for v in data.values()}
    return _ticker_map


def latest_10k(ticker: str):
    """Return (company_name, filing_date, url, html) for the most recent 10-K, or None."""
    info = _load_ticker_map().get(ticker.upper())
    if not info:
        print(f"  ! unknown ticker {ticker}")
        return None
    cik = info["cik_str"]

    subs = requests.get(SUBMISSIONS_URL.format(cik=cik), headers=HEADERS, timeout=30).json()
    recent = subs["filings"]["recent"]
    for form, date, accession, doc in zip(
        recent["form"], recent["filingDate"], recent["accessionNumber"], recent["primaryDocument"]
    ):
        if form == "10-K":
            url = ARCHIVE_URL.format(cik=cik, accession=accession.replace("-", ""), doc=doc)
            time.sleep(0.2)
            html = requests.get(url, headers=HEADERS, timeout=60).text
            return subs.get("name", ticker), date, url, html
    print(f"  ! no 10-K found for {ticker}")
    return None
