import os
import requests
from datetime import datetime
import pytz

API_KEY = os.getenv("CRYPTOPANIC_API_KEY", "").strip()
BASE_URL = "https://cryptopanic.com/api/v1/posts/"

def md_escape(s: str) -> str:
    return s.replace("|", " ").replace("\n", " ").strip()

def to_wib(utc_time: str) -> str:
    # Convert UTC ISO8601 → WIB
    try:
        dt_utc = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = dt_utc.replace(tzinfo=pytz.utc)
        dt_wib = dt_utc.astimezone(pytz.timezone("Asia/Jakarta"))
        return dt_wib.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return utc_time  # fallback

def fetch_kol_narratives(hours=4, limit=5):
    if not API_KEY:
        return []

    url = f"{BASE_URL}?auth_token={API_KEY}&public=true"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return [{"time": "-", "source": "Error", "coins": "-", "sentiment": "-", "title": f"API error: {e}"}]

    rows = []
    posts = data.get("results", [])
    for item in posts[:limit]:
        time_wib = to_wib(item.get("published_at", ""))
        source = md_escape(item.get("source", {}).get("title", "Unknown"))
        title = md_escape(item.get("title", ""))
        url = item.get("url", "")
        link = f"[{title}]({url})" if url else title
        coins = ",".join([c.upper() for c in item.get("currencies", [])]) if item.get("currencies") else "-"
        sentiment = item.get("votes", {}).get("sentiment", "Neutral")

        rows.append(f"| {time_wib} | {source} | {coins} | {sentiment} | {link} |")

    return rows

def write_md(kol_rows, trending_rows, filename="KOL_TRENDING.md"):
    header = [
        "# 📊 KOL Narratives & Trending Coins (4h)\n",
        "## 🔍 KOL Narratives (≤4h)\n",
        "| Time (WIB) | Source | Coins | Sentiment | Title |",
        "|-----------|--------|-------|-----------|-------|",
    ]
    if kol_rows:
        content = header + kol_rows
    else:
        content = header + ["| - | - | - | - | No data |"]

    content.append("\n## 🚀 Dynamic Trending Coins (Top 100)\n")
    content.extend(trending_rows)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

if __name__ == "__main__":
    kol = fetch_kol_narratives(hours=4, limit=10)

    # dummy contoh trending coins → lo udah punya fetch nya sendiri
    trending = [
        "| Rank | Coin | Symbol | Market Cap (USD) | 24h Volume (USD) |",
        "|------|------|--------|------------------|------------------|",
        "| 1 | Bitcoin | BTC | 2,181,722,215,953 | 67,678,466,782 |",
        "| 2 | Ethereum | ETH | 468,791,578,153 | 57,025,867,628 |",
    ]

    write_md(kol, trending)
