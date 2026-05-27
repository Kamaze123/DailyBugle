from fetcher import fetch_articles
from embedder import chunk_and_store, purge_old_articles
from summarizer import summarize_all
from config import CATEGORIES, ARTICLES_TO_KEEP_DAYS

def run_pipeline():
    print("Starting daily pipeline\n")

    purge_old_articles(ARTICLES_TO_KEEP_DAYS)
    # deleting old articles
    
    all_summarized = []
    for c in CATEGORIES:

        print(f"Fetching {c} articles...\n")
        article = fetch_articles(c)
        # fetching articles

        print(f"Summarizing {c} articles...\n")
        summarized = summarize_all(article)

        print("Chunking and storing articles...\n")
        chunk_and_store(summarized)
        #can make a change over here
        # we are adding the summarized articles to DB, not the entire articles

        all_summarized.extend(summarized)

    print(f"Pipeline complete - {len(all_summarized)} articles completed")
    return all_summarized

if __name__ == "__main__":
    run_pipeline()




