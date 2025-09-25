import os
import requests
import datetime
import pytz

# === Config ===
API_KEY = os.getenv("CRYPTOPANIC_API_KEY")  # simpen di GitHub Secrets
API_URL = "https://cryptopanic.com/api/v1/posts/"

# Timezone
wib = pytz.timezone("Asia/Jakarta")
now_utc = datetime.datetime.now(datetime.timezone.utc)
cutoff = now_utc - datetime.timedelta(hours=4)  # ≤ 4 jam

# === Fetch data from CryptoPanic ===
params = {
    "auth_token": API_KEY,
    "public": "true",
    "kind": "news"  # hanya berita, exclude price alerts
}

resp = requests.get(API_URL, params=params)
data = resp.json()

narratives = []

if "results" in data:
    for item in data["results"]:
        # Parse timestamp
        published_at = datetime.datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
        if published_at >= cutoff:  # filter 4 jam terakhir
            # Konversi ke WIB
            time_wib = published_at.astimezone(wib).strftime("%Y-%m-%d %H:%M:%S")
            title = item.get("title", "No title")
            url = item.get("url", "")
            source = item.get("source", {}).get("title", "Unknown")
            coins = ",".join([c.get("code", "") for c in item.get("currencies", [])]) or "-"
            sentiment = item.get("vote", "Neutral")

            narratives.append({
                "time": time_wib,
                "source": source,
                "coins": coins,
                "sentiment": sentiment,
                "title": title,
                "url": url
            })

# === Save to Markdown ===
with open("KOL_TRENDING.md", "w", encoding="utf-8") as f:
    f.write("# 📊 KOL Narratives & Trending Coins (4h)\n\n")

    # KOL Narratives
    f.write("## 🔎 KOL Narratives (≤4h)\n\n")
    f.write("| Time (WIB) | Source | Coins | Sentiment | Title |\n")
    f.write("|------------|--------|-------|-----------|-------|\n")
    if narratives:
        for n in narratives:
            f.write(f"| {n['time']} | {n['source']} | {n['coins']} | {n['sentiment']} | [{n['title']}]({n['url']}) |\n")
    else:
        f.write("| No data | - | - | - | No recent narratives found |\n")

    f.write("\n")
