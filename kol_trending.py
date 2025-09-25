import os
import requests
from datetime import datetime, timedelta
import pytz

# 🔑 API Keys
CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY", "").strip()

# Endpoint
CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/"
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

# Convert UTC → WIB
def to_wib(utc_time: str) -> str:
    try:
        dt_utc = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = dt_utc.replace(tzinfo=pytz.utc)
        dt_wib = dt_utc.astimezone(pytz.timezone("Asia/Jakarta"))
        return dt_wib.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return utc_time

# Escape Markdown (biar link ga rusak)
def md_escape(text: str) -> str:
    return (
        text.replace("|", "｜")
        .replace("[", "【")
        .replace("]", "】")
        .replace("\n", " ")
        .strip()
    )

# 🔍 Fetch KOL Narratives ≤ 4h
def fetch_kol(limit=10):
    if not CRYPTOPANIC_API_KEY:
        return []

    params = {"auth_token": CRYPTOPANIC_API_KEY, "filter": "news", "public": "true"}
    try:
        r = requests.get(CRYPTOPANIC_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return [f"| Error | {str(e)} | - | - | - |"]

    cutoff = datetime.utcnow() - timedelta(hours=4)
    rows = []

    for item in data.get("results", [])[:limit]:
        published = item.get("published_at", "")
        try:
            dt_utc = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
        except:
            continue
        if dt_utc < cutoff:
            continue

        time_wib = to_wib(published)
        source = item.get("source", {}).get("title", "Unknown")
        title = md_escape(item.get("title", "No title"))
        url = item.get("url", "")
        link = f"[{title}]({url})" if url else title
        coins = ",".join([c.get("code", "").upper() for c in item.get("currencies", [])]) or "-"
        sentiment = "Neutral"

        rows.append(f"| {time_wib} | {source} | {coins} | {sentiment} | {link} |")

    return rows

# 🚀 Fetch Top 100 Coins
def fetch_trending(limit=100):
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": limit, "page": 1}
    try:
        r = requests.get(COINGECKO_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return [f"| Error | {str(e)} | - | - | - |"], "N/A"

    rows = []
    for idx, coin in enumerate(data, 1):
        rows.append(
            f"| {idx} | {coin['name']} | {coin['symbol'].upper()} | "
            f"{coin['market_cap']:,} | {coin['total_volume']:,} |"
        )

    ts_wib = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Jakarta"))
    timestamp = ts_wib.strftime("%Y-%m-%d %H:%M:%S WIB")

    return rows, timestamp

# 📝 Write Markdown
def write_md(kol_rows, coin_rows, coin_timestamp):
    header = [
        "# 📊 KOL Narratives & Trending Coins (4h)\n",
        "## 🔍 KOL Narratives (≤4h)\n",
        "| Time (WIB) | Source | Coins | Sentiment | Title |",
        "|-----------|--------|-------|-----------|-------|",
    ] + kol_rows + [
        f"\n## 🚀 Dynamic Trending Coins (Top 100)\n",
        f"Last updated: **{coin_timestamp}**\n",
        "| Rank | Coin | Symbol | Market Cap (USD) | 24h Volume (USD) |",
        "|------|------|--------|------------------|------------------|",
    ] + coin_rows

    with open("KOL_TRENDING.md", "w", encoding="utf-8") as f:
        f.write("\n".join(header))

# 🚦 Main
def main():
    kol_rows = fetch_kol(limit=20)
    coin_rows, coin_timestamp = fetch_trending(limit=100)
    write_md(kol_rows, coin_rows, coin_timestamp)

if __name__ == "__main__":
    main()
