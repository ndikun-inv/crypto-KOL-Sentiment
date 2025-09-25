import os
import requests

API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={API_KEY}&public=true"

def fetch_news():
    try:
        res = requests.get(URL, timeout=10)
        res.raise_for_status()
        return res.json().get("results", [])
    except Exception as e:
        print("Error fetch:", e)
        return []

def build_markdown(posts):
    md = ["# 📰 Crypto News (CryptoPanic)\n"]
    md.append("| Title | Source |")
    md.append("|-------|---------|")
    
    if not posts:
        md.append("| ❌ No data | Check API key or quota |")
        return "\n".join(md)

    for p in posts[:10]:  # ambil 10 berita terbaru
        title = p.get("title", "No Title").replace("|", "-")
        url = p.get("url", "")
        source = p.get("source", {}).get("title", "Unknown")
        md.append(f"| [{title}]({url}) | {source} |")
    
    return "\n".join(md)

if __name__ == "__main__":
    posts = fetch_news()
    content = build_markdown(posts)

    with open("TRENDING.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ TRENDING.md updated")
