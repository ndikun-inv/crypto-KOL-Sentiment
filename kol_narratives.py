import os, re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import feedparser
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

# ==============================
# Konfigurasi
LOOKBACK_HOURS = 24  # ambil artikel 24 jam terakhir
OUT_DIR = "data"
CSV_PATH = os.path.join(OUT_DIR, "kol_narratives.csv")
XLSX_PATH = os.path.join(OUT_DIR, "kol_narratives.xlsx")
MD_PATH = "KOL_TRENDING.md"

# Daftar KOL/Research RSS (tanpa API key)
KOL_FEEDS = [
    {"name": "Bankless",            "url": "https://bankless.substack.com/feed"},
    {"name": "The Defiant",         "url": "https://thedefiant.io/feed"},
    {"name": "Coin Bureau",         "url": "https://www.coinbureau.com/feed/"},
    {"name": "Glassnode Insights",  "url": "https://insights.glassnode.com/rss/"},
    {"name": "Delphi Digital",      "url": "https://delphidigital.substack.com/feed"},
]
# ==============================

# Ambil Top N coin dari CoinGecko (dinamis, no API key)
def get_top_coins(limit=20):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False,
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("[CoinGecko] error:", e)
        return {}

    mapping = {}
    for coin in data:
        symbol = coin["symbol"].upper()
        name = coin["name"].lower()
        # masukkan nama & simbol lower-case buat keyword match
        mapping[symbol] = [name, symbol.lower()]
    return mapping

def strip_html(s: str) -> str:
    return re.sub("<[^<]+?>", " ", s or "")

def detect_tickers(text: str, tickers_map: dict):
    """Deteksi coin dari judul+ringkasan berdasarkan top 20 CoinGecko"""
    found = set()
    low = (text or "").lower()
    # whole-word match untuk nama/simbol
    for sym, kws in tickers_map.items():
        for kw in kws:
            if re.search(rf"\b{re.escape(kw)}\b", low):
                found.add(sym)
    return sorted(found)

def label_sentiment(compound: float) -> str:
    if compound >= 0.2:
        return "🟢 Positive"
    if compound <= -0.2:
        return "🔴 Negative"
    return "⚪ Neutral"

def parse_time(entry):
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if getattr(entry, "updated_parsed", None):
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    analyzer = SentimentIntensityAnalyzer()

    # 1) Ambil top 20 coin
    tickers_map = get_top_coins(20)
    if not tickers_map:
        print("⚠️ Gagal ambil top coins; lanjut tetap jalan (deteksi coin mungkin kosong).")

    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(hours=LOOKBACK_HOURS)

    rows = []

    # 2) Tarik RSS KOL
    for feed in KOL_FEEDS:
        try:
            # pakai user-agent biar feed yang rewel gak nolak
            d = feedparser.parse(feed["url"], request_headers={
                "User-Agent": "Mozilla/5.0 (compatible; KOLCollector/1.0)"
            })
            if d.bozo:
                # feed bermasalah (format/SSL), skip aja
                continue

            for e in d.entries:
                t_utc = parse_time(e)
                if t_utc < cutoff:
                    continue

                title = getattr(e, "title", "") or ""
                summary = getattr(e, "summary", "") or ""
                link = getattr(e, "link", "") or ""

                clean_summary = strip_html(summary)
                text_for_sent = f"{title}. {clean_summary}".strip()

                # 3) Sentiment
                score = analyzer.polarity_scores(text_for_sent)["compound"]
                sentiment = label_sentiment(score)

                # 4) Deteksi coin (judul + ringkasan)
                coins = detect_tickers(f"{title} {clean_summary}", tickers_map)
                # Filter: simpan hanya yang menyebut minimal 1 coin top 20
                if not coins:
                    continue

                ts_utc = t_utc.isoformat()
                ts_wib = t_utc.astimezone(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")

                rows.append({
                    "source": feed["name"],
                    "title": title.replace("\n", " ").strip(),
                    "url": link,
                    "sentiment_score": round(score, 3),
                    "sentiment": sentiment,
                    "coins": ",".join(coins),
                    "timestamp_utc": ts_utc,
                    "timestamp_wib": ts_wib,
                })
        except Exception as ex:
            print(f"[{feed['name']}] error:", ex)
            continue

    if not rows:
        # Tetap bikin file agar step commit gak error
        pd.DataFrame(columns=[
            "source","title","url","sentiment_score","sentiment","coins",
            "timestamp_utc","timestamp_wib"
        ]).to_csv(CSV_PATH, index=False)
        with open(MD_PATH, "w", encoding="utf-8") as f:
            f.write("# 🔎 KOL Narratives (24h)\n\nTidak ada artikel relevan (cek feed/LOOKBACK).\n")
        print("❌ No KOL narratives mentioning top-20 coins.")
        return

    # 5) Simpan CSV/Excel
    df = pd.DataFrame(rows).sort_values("timestamp_utc", ascending=False)
    df.to_csv(CSV_PATH, index=False)
    try:
        df.to_excel(XLSX_PATH, index=False)
    except Exception as ex:
        print("⚠️ Excel save warning:", ex)

    # 6) Ringkasan Markdown (top 10 terbaru)
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("# 🔎 KOL Narratives (24h)\n\n")
        f.write("| Time (WIB) | Source | Coins | Sentiment | Title |\n")
        f.write("|------------|--------|-------|-----------|-------|\n")
        for _, r in df.head(10).iterrows():
            t = r["title"].replace("|", " ")
            f.write(
                f"| {r['timestamp_wib']} | {r['source']} | {r['coins']} | "
                f"{r['sentiment']} | [{t}]({r['url']}) |\n"
            )

    print(f"✅ Saved → {CSV_PATH} | {XLSX_PATH} | {MD_PATH}")

if __name__ == "__main__":
    main()
