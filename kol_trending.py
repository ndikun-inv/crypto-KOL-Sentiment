import requests
import datetime

OUTPUT_FILE = "KOL_TRENDING.md"

def fetch_trending():
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

def write_md(coins):
    header = [
        "# 📊 KOL Narratives & Trending Coins (4h)\n",
        "## 🚀 Dynamic Trending Coins (Top 100)\n",
        "| Rank | Coin | Symbol | Market Cap (USD) | 24h Volume (USD) |",
        "|------|------|--------|------------------|------------------|",
    ]
    rows = []
    for i, coin in enumerate(coins, 1):
        rows.append(
            f"| {i} | {coin['name']} | {coin['symbol'].upper()} | "
            f"{coin['market_cap']:,} | {coin['total_volume']:,} |"
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(header + rows))

def main():
    coins = fetch_trending()
    write_md(coins)

if __name__ == "__main__":
    main()
