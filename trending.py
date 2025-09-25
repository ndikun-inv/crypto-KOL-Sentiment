import os
import requests

API_KEY = os.getenv("SENTIMENT_API_KEY")

url = "https://api.santiment.net/graphql"

query = """
{
  getTrendingWords {
    word
    score
  }
}
"""

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, json={"query": query}, headers=headers)

if response.status_code == 200:
    data = response.json()

    lines = ["# 🔥 Crypto Trending Words (Santiment)\n"]
    if "data" in data and "getTrendingWords" in data["data"]:
        for item in data["data"]["getTrendingWords"]:
            lines.append(f"- **{item['word']}** → score: {item['score']}")
    else:
        lines.append("⚠️ No data returned.")

    with open("TRENDING.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
else:
    print("Error:", response.status_code, response.text)
