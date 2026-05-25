from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import CHUNK_SIZE, CHUNK_OVERLAP, CHROMA_DB_PATH, EMBEDDING_MODEL
from datetime import datetime, timedelta

embeddings = HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL)

vectorstore = Chroma(
    persist_directory=CHROMA_DB_PATH,
    embedding_function=embeddings
)


def chunk_and_store(articles : list[dict]):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    all_chunks = []
    all_metadata = []

    for article in articles:
        full_text = f"{article['title']}.\n\n{article['content']}"
        chunks = splitter.split_text(full_text)


        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append({
                "title": article["title"],
                "source": article["source"],
                "url": article["url"],
                "category": article["category"],
                "published_at": article["published_at"],
            })

    vectorstore.add_texts(texts=all_chunks, metadatas=all_metadata)
    print(f"Stored {len(all_chunks)} chunks from {len(articles)} articles")

def purge_old_articles(days: int):
    # ChromaDB doesn't support date filtering natively
    # so we delete and rebuild from scratch when purging
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    all_data = vectorstore.get(include=["metadatas"])

    ids_to_delete = [
        id for id, meta in zip(all_data["ids"], all_data["metadatas"])
        if meta.get("published_at", "") < cutoff
    ]

    if ids_to_delete:
        vectorstore.delete(ids=ids_to_delete)
        print(f"Purged {len(ids_to_delete)} old chunks")
    else:
        print("Nothing to purge")

if __name__ == "__main__":
    from fetcher import fetch_articles
    articles = fetch_articles("technology")
    chunk_and_store(articles)