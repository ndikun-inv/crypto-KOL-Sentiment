import os
import requests

API_KEY = os.getenv("CRYPTOPANIC_API_KEY", "").strip()
BASE_URL = "https://cryptopanic.com/api/v1/posts/"

def md_escape(s: str) -> str:
    return (s or "").replace("|", r"\|").replace("\n", " ").strip()

def write_md(rows):
    header = [
        "# 📰 Crypto News (CryptoPanic)\n",
        "| Title | Source |",
        "|-------|--------|",
    ]
    with open("TRENDING.md", "w", encoding="utf-8") as f:
        f.write("\n".join(header + rows))

def main():
    if not API_KEY:
        write_md(["| ❌ Missing API key | Set secret `CRYPTOPANIC_API_KEY` |"])
        return

    params = {"auth_token": API_KEY, "public": "true", "kind": "news"}
    try:
        r = requests.get(BASE_URL, params=params, timeout=20)
        if r.status_code == 429:
            write_md(["| ❌ 429 Too Many Requests | Quota/rate limit hit |"])
            return
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        write_md([f"| ❌ Error | {type(e).__name__}: {e} |"])
        return

    posts = data.get("results") or []
    if not posts:
        write_md(["| ⚠️ No data | Check token/params/quota |"])
        return

    rows = []
    for p in posts[:5]:  # ambil 5 headline terbaru
        title = md_escape(p.get("title", "No title"))
        url = p.get("url") or p.get("source", {}).get("url") or ""
        link = f"[{title}]({url})" if url else title
        source = md_escape(p.get("source", {}).get("title", "Unknown"))
        rows.append(f"| {link} | {source} |")

    write_md(rows)

if __name__ == "__main__":
    main()
