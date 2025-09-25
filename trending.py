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

try:
    response = requests.post(url, json={"query": query}, headers=headers)

    lines = ["# 🔥 Crypto Trending Words (Santiment)\n"]
    lines.append("| Word | Score |")
    lines.append("|------|-------|")

    if response.status_code == 200:
        data = response.json()
        if "data" in data and "getTrendingWords" in data["data"]:
            for item in data["data"]["getTrendingWords"]:
                lines.append(f"| {item['word']} | {item['score']} |")
        else:
            lines.append("| ⚠️ No data returned | - |")
    else:
        lines.append(f"| ❌ Error {response.status_code} | Check API key / query |")

    # Always write file (biar gak bikin error pas commit)
    with open("TRENDING.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("TRENDING.md generated successfully ✅")

except Exception as e:
    with open("TRENDING.md", "w", encoding="utf-8") as f:
        f.write("# 🔥 Crypto Trending Words (Santiment)\n\n")
        f.write(f"⚠️ Exception occurred: {str(e)}\n")
    print("Error while fetching data:", str(e))
