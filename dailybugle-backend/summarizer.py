from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
import re

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=300
)

def clean_content(text: str) -> str:
    return re.sub(r'\[\+\d+ chars\]', '', text).strip()

def summarize_article(article: dict) -> dict:
    prompt = f"""Summarize this news article in exactly 3 sentences.
Be concise and factual. No opinions. No em-dashes.

Title: {article['title']}
Content: {clean_content(article['content'])}

3 sentence summary:"""

    response = llm.invoke(prompt)

    return {
        **article,
        "summary": response.content
    }

def summarize_all(articles: list[dict]) -> list[dict]:    
    summarized = []
    for i, article in enumerate(articles):
        print(f"Summarizing {i+1}/{len(articles)} : {article['title'][:50]}...")
        summarized.append(summarize_article(article))
    return summarized


if __name__ == "__main__":
    from fetcher import fetch_articles
    articles = fetch_articles("technology")
    summarized = summarize_all(articles)
    for a in summarized:
        print(f" {a['title']}")
        print(f" {a['summary']}")
        print(f" {a['url']}")
