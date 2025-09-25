import requests
import re
import os
from datetime import datetime, timedelta
import pytz

# ======================
# Ambil Top 100 Market Cap
# ======================
def get_top_coins(limit=100):
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "false"
    }
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()

    mapping = {}
    for coin in data:
        symbol = coin["symbol"].upper()
        name = coin["name"].lower()
        mapping[symbol] = [name, symbol.lower()]
    return mapping

# ======================
# Ambil Trending Coins (CoinGecko)
# ======================
def get_trending_coins():
    url = "https://api.coingecko.com/api/v3/search/trending"
    resp = requests.get(url, timeout=30)
    data = resp.json()

    mapping = {}
    for item in data.get("coins", []):
        coin = item["item"]
        symbol = coin["symbol"].upper()
        name = coin["name"].lower()
        mapping[symbol] = [name, symbol.lower()]
    return mapping

# ======================
# Gabungkan Top + Trending
# ======================
def get_tickers_map():
    top100 = get_top_coins(100)
    trending = get_trending_coins()
    return {**top100, **trending}   # merge dict

# ======================
# Parse berita
# ======================
def detect_coins_in_text(text, tickers_map):
    found = []
    text_lower = text.lower()
    for symbol, keywords in tickers_map.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                found.append(symbol)
                break
    return found

def classify_sentiment(title):
    title = title.lower()
    if any(w in title for w in ["surge", "rise", "rally", "bull", "positive", "gain", "up"]):
        return "🟢 Positive"
    elif any(w in title for w in ["drop", "fall", "bear", "negative", "loss", "down", "crash"]):
        return "🔴 Negative"
    else:
        return "🟣 Neutral"

# ======================
# Main
# ======================
def main():
    tickers_map = get_tickers_map()
    print(f"✅ Loaded {len(tickers_map)} coins (Top 100 + Trending)")

    # Contoh dummy news (nanti diganti API real news)
    dummy_news = [
        {"time": "2025-09-26T01:00:00Z", "source": "The Defiant", "title": "Solana rises as new projects join ecosystem"},
        {"time": "2025-09-26T02:00:00Z", "source": "CoinDesk", "title": "Bitcoin drops after FED comments"},
        {"time": "2025-09-26T03:00:00Z", "source": "Glassnode", "title": "Arbitrum gaining traction among L2s"},
    ]

    tz = pytz.timezone("Asia/Jakarta")
    with open("TRENDING.md", "w", encoding="utf-8") as f:
        f.write("## 🔍 KOL Narratives (24h)\n\n")
        f.write("| Time (WIB) | Source | Coins | Sentiment | Title |\n")
        f.write("|------------|--------|-------|-----------|-------|\n")

        for item in dummy_news:
            coins = detect_coins_in_text(item["title"], tickers_map)
            if not coins:
                continue

            time_wib = datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC).astimezone(tz)
            sentiment = classify_sentiment(item["title"])
            f.write(f"| {time_wib.strftime('%Y-%m-%d %H:%M:%S')} | {item['source']} | {','.join(coins)} | {sentiment} | {item['title']} |\n")

if __name__ == "__main__":
    main()
