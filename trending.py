import os
import requests
from textwrap import shorten

API_KEY = (os.getenv("SENTIMENT_API_KEY") or "").strip()
URL = "https://api.santiment.net/graphql"

QUERY = """
{
  getTrendingWords {
    word
    score
  }
}
"""

def write_md(lines):
    with open("TRENDING.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

lines = ["# 🔥 Crypto Trending Words (Santiment)\n", "| Word | Score |", "|------|-------|"]

# 1) Validasi token dulu
if not API_KEY:
    lines.append("| ❌ Missing token | Set secret `SENTIMENT_API_KEY` |")
    write_md(lines)
    raise SystemExit(0)

# JWT normalnya punya 3 segmen dipisah "."
if API_KEY.count(".") < 2:
    lines.append("| ❌ Invalid token format | Token bukan JWT (harus ada dua titik) |")
    write_md(lines)
    raise SystemExit(0)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

try:
    resp = requests.post(URL, json={"query": QUERY}, headers=headers, timeout=60)
    if resp.status_code == 200:
        data = resp.json()
        items = (data.get("data") or {}).get("getTrendingWords") or []
        if not items:
            # bisa jadi karena scope token nggak cocok
            err = shorten(str(data), width=60, placeholder="…")
            lines.append(f"| ⚠️ No data | {err} |")
        else:
            for it in items:
                lines.append(f"| {it['word']} | {it['score']} |")
    else:
        # tulis sebagian pesan error untuk debug
        msg = shorten(resp.text.replace("\n", " "), width=70, placeholder="…")
        lines.append(f"| ❌ Error {resp.status_code} | {msg} |")
except Exception as e:
    lines.append(f"| ❌ Exception | {type(e).__name__}: {str(e)} |")

write_md(lines)
print("TRENDING.md updated")
