from newsapi import NewsApiClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

newsapi = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))

def fetch_articles(category: str, days_back: int = 1) -> list[dict]:
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    response = newsapi.get_top_headlines(
        category=category,
        language="en",
        page_size=10
    )

    articles = []
    for article in response.get("articles", []):
        if not article.get("content") or not article.get("description"):
            continue

        articles.append({
            "title": article["title"],
            "content": article.get("content", "") or article.get("description", ""),
            "description": article.get("description", ""),
            "source": article["source"]["name"],
            "url": article["url"],
            "published_at": article["publishedAt"],
            "category": category,
        })

    return articles

if __name__ == "__main__":
    articles = fetch_articles("technology")
    for a in articles:
        print(f"{a['title']} — {a['source']}")
    print(f"\nFetched {len(articles)} articles")