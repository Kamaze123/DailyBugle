CATEGORIES = ["technology", "sports", "business", "science", "health"]
MAX_ARTICLES_PER_CATEGORY = 10
ARTICLES_TO_KEEP_DAYS = 7  #context window is only 7 days, switch to 30 days later
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHROMA_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"