import os
import requests

API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={API_KEY}&public=true"

def fetch_news():
    try:
        r = requests.get(URL, timeout=10)
        r.raise_for_status()
        data = r.json()

        results = []
        for post in data.get("results", []):
            title = post.get("title", "No title")
            source = post.get("source", {}).get("title", "Unknown")
            results.append((title, source))

        return results
    except Exception as e:
        return [(f"Error: {str(e)}", "Check API key or quota")]

def save_markdown(news):
    with open("TRENDING.md", "w", encoding="utf-8") as f:
        f.write("# 📰 Crypto News (CryptoPanic)\n\n")
        f.write("| Title | Source |\n")
        f.write("|-------|--------|\n")
        if not news:
            f.write("| ❌ No data | Check API key or quota |\n")
        else:
            for title, source in news:
                f.write(f"| {title} | {source} |\n")

if __name__ == "__main__":
    news = fetch_news()
    save_markdown(news)
