"""Cross-platform test client (avoids curl quoting issues on Windows).

Usage:  python scripts/ask.py "What are Apple's main risk factors?"
"""
import sys
import requests

question = sys.argv[1] if len(sys.argv) > 1 else "What are Apple's main risk factors?"
resp = requests.post("http://localhost:8000/ask", json={"question": question}, timeout=120)
data = resp.json()
print("\nANSWER:\n" + data["answer"])
print("\nSOURCES:")
for s in data.get("sources", []):
    print(f"  - {s['ticker']} | {s['section']} (score {s['score']})")
