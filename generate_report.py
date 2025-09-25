import requests
import datetime
import os

OUTPUT_FILE = "KOL_TRENDING.md"

# === PART 1: KOL Narratives (dummy API sementara) ===
def fetch_kol_narratives():
    # nanti integrasi ke sumber real → misalnya Defiant, Glassnode, Santiment
    # sementara gua kasih dummy 2 berita
    now = datetime.datetime.utcnow()
    return [
        {
            "time": (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "The Defiant",
            "coins": "BTC,ETH",
            "sentiment": "Neutral",
            "title": "Crypto Market Drops as US Data Dashes Rate Cut Hopes",
            "url": "https://thedefiant.io/example1"
        },
        {
            "time": (now - datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Glassnode",
            "coins": "BTC",
            "sentiment": "Negative",
            "title": "Bitcoin On-Chain Signals Weakening Momentum",
            "url": "https://glassnode.com/example2"
        }
    ]

# === PART 2: Trending Coins from CoinGecko ===
def fetch_trending_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "price_change_percentage": "24h"
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

# === Writer ===
def write_md(narratives, coins):
    header = ["# 📊 KOL Narratives & Trending Coins (4h)\n"]

    # --- KOL Narratives ---
    header.append("## 🔍 KOL Narratives (≤4h)\n")
    header.append("| Time (WIB) | Source | Coins | Sentiment | Title |")
    header.append("|------------|--------|-------|-----------|-------|")

    if narratives:
        for n in narratives:
            row = f"| {n['time']} | {n['source']} | {n['coins']} | {n['sentiment']} | [{n['title']}]({n['url']}) |"
            header.append(row)
    else:
        header.append("| - | - | - | - | No narratives found |")

    # --- Trending Coins ---
    header.append("\n## 🚀 Dynamic Trending Coins (Top 100)\n")
    header.append("| Rank | Coin | Symbol | Market Cap (USD) | 24h Volume (USD) |")
    header.append("|------|------|--------|------------------|------------------|")

    for i, coin in enumerate(coins, 1):
        header.append(
            f"| {i} | {coin['name']} | {coin['symbol'].upper()} | "
            f"{coin['market_cap']:,} | {coin['total_volume']:,} |"
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(header))

def main():
    narratives = fetch_kol_narratives()
    coins = fetch_trending_coins()
    write_md(narratives, coins)

if __name__ == "__main__":
    main()
