import requests
import datetime
import pytz

# ============= CONFIG =============
# Coingecko API untuk Top 100 coins
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
# Contoh sumber KOL (dummy untuk demo, bisa ganti API/news valid nanti)
KOL_SOURCES = [
    {
        "source": "The Defiant",
        "title": "Crypto Market Drops as Upbeat US Economic Data Dashes Rate Cut Hopes",
        "link": "https://thedefiant.io/article1",
        "coins": ["BTC", "ETH"],
        "sentiment": "Neutral",
        "time": datetime.datetime.utcnow(),
    },
    {
        "source": "Glassnode Insights",
        "title": "From Rally to Correction",
        "link": "https://glassnode.com/insight/article2",
        "coins": ["BTC"],
        "sentiment": "Negative",
        "time": datetime.datetime.utcnow() - datetime.timedelta(hours=2),
    },
    {
        "source": "The Defiant",
        "title": "Joe Lubin’s SharpLink to Tokenize $BET Shares on Ethereum via Superstate",
        "link": "https://thedefiant.io/article3",
        "coins": ["ETH"],
        "sentiment": "Positive",
        "time": datetime.datetime.utcnow() - datetime.timedelta(hours=3),
    },
]

# WIB timezone
WIB = pytz.timezone("Asia/Jakarta")


def fetch_top_coins(limit=100):
    """Ambil top coin dari Coingecko"""
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False,
    }
    resp = requests.get(COINGECKO_URL, params=params, timeout=30)
    if resp.status_code == 200:
        return resp.json()
    else:
        print("Error fetch top coins:", resp.text)
        return []


def format_time_wib(dt):
    """Convert UTC ke WIB"""
    return dt.replace(tzinfo=pytz.utc).astimezone(WIB).strftime("%Y-%m-%d %H:%M:%S")


def main():
    # Fetch dynamic trending coins
    coins = fetch_top_coins(100)

    with open("KOL_TRENDING.md", "w", encoding="utf-8") as f:
        # Header
        f.write("# 📊 KOL Narratives & Trending Coins (24h)\n\n")

        # KOL Narratives
        f.write("## 🔎 KOL Narratives (24h)\n\n")
        f.write("| Time (WIB) | Source | Coins | Sentiment | Title |\n")
        f.write("|------------|--------|-------|-----------|-------|\n")

        for item in KOL_SOURCES:
            f.write(
                f"| {format_time_wib(item['time'])} "
                f"| {item['source']} "
                f"| {','.join(item['coins'])} "
                f"| {item['sentiment']} "
                f"| [{item['title']}]({item['link']}) |\n"
            )

        # Dynamic Trending Coins
        f.write("\n\n## 🚀 Dynamic Trending Coins (Top 100)\n\n")
        f.write("| Rank | Coin | Symbol | Market Cap (USD) | 24h Volume (USD) |\n")
        f.write("|------|------|--------|------------------|-----------------|\n")

        for c in coins:
            f.write(
                f"| {c['market_cap_rank']} "
                f"| {c['name']} "
                f"| {c['symbol'].upper()} "
                f"| {c['market_cap']:,} "
                f"| {c['total_volume']:,} |\n"
            )


if __name__ == "__main__":
    main()
