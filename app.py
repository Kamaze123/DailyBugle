from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
 
from rag import ask
from pipeline import run_pipeline
from config import CATEGORIES
 
app = FastAPI(
    title="DailyBugle API",
    description="AI-powered news summarizer and Q&A backend",
    version="1.0.0"
)
 
# ---- CORS ---- (allows React frontend to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite + CRA ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# ---- in-memory article store ----
# populated when pipeline runs; survives as long as server is up
article_store: list[dict] = []
 
 
# ---- request/response models ----
class AskRequest(BaseModel):
    question: str
 
class AskResponse(BaseModel):
    answer: str
    sources: list[str]
 
class PipelineResponse(BaseModel):
    message: str
    articles_processed: int
 
class ArticlesResponse(BaseModel):
    total: int
    category: Optional[str]
    articles: list[dict]
 
  
@app.get("/")
def health_check():
    return {"status": "ok", "message": "NewsDaily API is running"}
 
 
@app.get("/categories")
def get_categories():
    """Return available news categories."""
    return {"categories": CATEGORIES}
 
 
@app.post("/ask", response_model=AskResponse)
def ask_question(body: AskRequest):
    """
    Ask a question grounded in today's news.
    Returns the answer and the sources it was pulled from.
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
 
    try:
        result = ask(body.question)
        return AskResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.post("/pipeline/run", response_model=PipelineResponse)
def trigger_pipeline():
    """
    Manually trigger the full pipeline:
    fetch → summarize → embed → store in ChromaDB.
    Also refreshes the in-memory article store.
    """
    global article_store
    try:
        articles = run_pipeline()
        article_store = articles
        return PipelineResponse(
            message="Pipeline completed successfully",
            articles_processed=len(articles)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/articles/grouped")
def get_articles_grouped():
    """Returns articles grouped by category"""
    if not article_store:
        raise HTTPException(
            status_code=404,
            detail="No articles loaded yet. Run /pipeline/run first."
        )

    grouped = {}
    for article in article_store:
        category = article.get("category", "uncategorized").lower()
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(article)

    return {
        "total": len(article_store),
        "sections": grouped
    }