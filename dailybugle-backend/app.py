from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from embedder import vectorstore, client, COLLECTION_NAME
from rag import ask
from pipeline import run_pipeline
from config import CATEGORIES

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_pipeline, "cron", hour=7, minute=0)
    scheduler.start()
    print("Scheduler started — pipeline runs daily at 7am")
    yield
    scheduler.shutdown()

app = FastAPI(
    title="DailyBugle API",
    description="AI-powered news summarizer and Q&A backend",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: list[str]

class PipelineResponse(BaseModel):
    message: str
    articles_processed: int


@app.get("/")
def health_check():
    return {"status": "ok", "message": "DailyBugle API is running"}


@app.get("/categories")
def get_categories():
    return {"categories": CATEGORIES}


@app.post("/ask", response_model=AskResponse)
def ask_question(body: AskRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        result = ask(body.question)
        return AskResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline/run", response_model=PipelineResponse)
def trigger_pipeline():
    try:
        articles = run_pipeline()
        return PipelineResponse(
            message="Pipeline completed successfully",
            articles_processed=len(articles)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/articles/today")
def get_todays_articles():
    # scroll through all points in Qdrant collection
    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        with_payload=True,
        limit=10000
    )

    if not results:
        raise HTTPException(status_code=404, detail="No articles in database yet.")

    # dedupe by URL
    seen_urls = set()
    articles = []
    for point in results:
        payload = point.payload or {}
        meta = payload.get("metadata", payload)  # handle both payload structures
        url = meta.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            articles.append(meta)

    if not articles:
        raise HTTPException(status_code=404, detail="No articles in database yet.")

    # group by category, sort by date, take top 6
    grouped = {}
    for article in articles:
        cat = article.get("category", "uncategorized").lower()
        grouped.setdefault(cat, []).append(article)

    grouped = {
        cat: sorted(arts, key=lambda x: x.get("published_at", ""), reverse=True)[:6]
        for cat, arts in grouped.items()
    }

    total = sum(len(arts) for arts in grouped.values())
    return {"total": total, "sections": grouped}