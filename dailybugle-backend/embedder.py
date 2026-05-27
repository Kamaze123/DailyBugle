from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import CHUNK_SIZE, CHUNK_OVERLAP
from dotenv import load_dotenv
import hashlib
import os

load_dotenv()

COLLECTION_NAME = "dailybugle"
VECTOR_SIZE = 384  # HuggingFace all-mpnet-base-v2 output size

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=os.getenv("HF_API_KEY")
)

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# create collection if it doesn't exist
existing = [c.name for c in client.get_collections().collections]
if COLLECTION_NAME not in existing:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection: {COLLECTION_NAME}")

vectorstore = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings
)


def chunk_and_store(articles: list[dict]):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    all_chunks = []
    all_metadata = []
    all_ids = []

    for article in articles:
        full_text = f"{article['title']}.\n\n{article['content']}"
        chunks = splitter.split_text(full_text)

        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{article['url']}_{i}".encode()).hexdigest()

            all_chunks.append(chunk)
            all_metadata.append({
                "title": article["title"],
                "source": article["source"],
                "url": article["url"],
                "category": article["category"],
                "published_at": article["published_at"],
                "summary": article.get("summary", ""),
            })
            all_ids.append(chunk_id)

    vectorstore.add_texts(texts=all_chunks, metadatas=all_metadata, ids=all_ids)
    print(f"Stored {len(all_chunks)} chunks from {len(articles)} articles")


def purge_old_articles(days: int):
    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    # scroll all points and delete old ones manually
    results, _ = client.scroll(collection_name=COLLECTION_NAME, with_payload=True, limit=10000)
    
    ids_to_delete = [
        point.id for point in results
        if point.payload.get("metadata", {}).get("published_at", "") < cutoff
    ]
    
    if ids_to_delete:
        client.delete(collection_name=COLLECTION_NAME, points_selector=ids_to_delete)
        print(f"Purged {len(ids_to_delete)} old chunks")
    else:
        print("Nothing to purge")

if __name__ == "__main__":
    info = client.get_collection(COLLECTION_NAME)
    print(f"Total vectors in DB: {info.points_count}")