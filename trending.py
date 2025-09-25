import os
import requests

API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

url = f"https://cryptopanic.com/api/v1/posts/?auth_token={API_KEY}&public=true"

try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()

    posts = data.get("results", [])
    if not posts:
        content = "| ❌ No data | Check API key or quota |\n"
    else:
        rows = ""
        for post in posts[:5]:  # ambil 5 berita terbaru aja
            title = post.get("title", "No title")
            source = post.get("source", {}).get("title", "Unknown")
            rows += f"| {title} | {source} |\n"
        content = rows

except Exception as e:
    content = f"| ❌ Error | {str(e)} |\n"

with open("TRENDING.md", "w", encoding="utf-8") as f:
    f.write("# 📰 Crypto News (CryptoPanic)\n\n")
    f.write("| Title | Source |\n")
    f.write("|-------|--------|\n
