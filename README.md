# Daily Bugle 

An AI-powered news aggregator that fetches, summarizes, and lets you chat with today's headlines. Built with FastAPI, React, and a full RAG (Retrieval-Augmented Generation) pipeline.

**Live Demo:** [daily-bugle-mu.vercel.app](https://daily-bugle-mu.vercel.app)

---

## What It Does

- Automatically fetches top headlines across multiple categories every day at 7am
- Summarizes each article into 3 clean sentences using Groq 
- Stores articles as vector embeddings in Qdrant for semantic search
- Lets you ask natural language questions grounded in today's news
- Displays articles in a newspaper-style dark editorial UI

---

## Tech Stack

**Backend**
- FastAPI — REST API
- APScheduler — daily pipeline automation
- NewsAPI — news fetching
- Groq (Llama 3.3 70B) — article summarization + RAG answers
- HuggingFace Inference API — text embeddings (`all-MiniLM-L6-v2`)
- Qdrant Cloud — vector database
- LangChain — RAG chain orchestration

**Frontend**
- React + Vite
- Axios — API calls
- React Router — client-side routing
- Plain CSS with CSS variables — dark editorial theme
- Playfair Display + DM Sans — typography

**Deployment**
- Backend → Render
- Frontend → Vercel
- Vector DB → Qdrant Cloud (free tier)
- Uptime monitoring → cron-job.org

---

## Backend Architecture

The backend is the core of the project. Here's exactly how data flows through the system:

### Pipeline Flow

```
NewsAPI
   │
   ▼
fetcher.py          — fetches top 10 headlines per category
   │
   ▼
summarizer.py       — sends each article to Groq, returns 3-sentence summary
   │
   ▼
embedder.py         — chunks article text, generates embeddings via HuggingFace API,
   │                   stores chunks + metadata (title, source, url, category,
   │                   published_at, summary) in Qdrant Cloud
   ▼
Qdrant Cloud        — persistent vector store, survives redeploys
```

### Daily Automation

The scheduler is embedded inside FastAPI using APScheduler and the `lifespan` context manager. When the server boots, the scheduler starts in a background thread and fires `run_pipeline()` every day at 7am — no separate process or cron job needed.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_pipeline, "cron", hour=7, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()
```

### RAG Flow (Ask Anything)

```
User question
   │
   ▼
Qdrant retriever    — finds top 5 semantically similar article chunks
   │
   ▼
LangChain RAG chain — injects chunks as context into Groq prompt
   │
   ▼
Groq (Llama 3.3)    — generates grounded answer
   │
   ▼
Response            — answer + source names returned to frontend
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/categories` | List available categories |
| `POST` | `/ask` | Ask a question, get RAG answer + sources |
| `POST` | `/pipeline/run` | Manually trigger the full pipeline |
| `GET` | `/articles/today` | Fetch latest articles grouped by category |

---

## Project Structure

```
dailybugle/
├── dailybugle-backend/
│   ├── app.py              — FastAPI app + scheduler + routes
│   ├── pipeline.py         — orchestrates fetch → summarize → store
│   ├── fetcher.py          — NewsAPI integration
│   ├── summarizer.py       — Groq summarization
│   ├── embedder.py         — chunking, embedding, Qdrant storage
│   ├── rag.py              — LangChain RAG chain
│   ├── config.py           — constants (categories, chunk size, etc.)
│   ├── requirements.txt
│   └── Procfile
└── dailybugle-frontend/
    ├── src/
    │   ├── api/index.js        — all API calls
    │   ├── components/
    │   │   ├── Navbar.jsx
    │   │   └── ArticleCard.jsx
    │   ├── pages/
    │   │   ├── DigestPage.jsx  — newspaper-style article feed
    │   │   └── ChatPage.jsx    — RAG chat interface
    │   ├── App.jsx
    │   └── index.css
    └── package.json
```

---

## Running Locally

**Backend:**
```bash
cd dailybugle-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# create .env with your keys
cp .env.example .env

uvicorn app:app --reload
```

**Frontend:**
```bash
cd dailybugle-frontend
npm install
npm run dev
```

**Populate the database:**
```bash
curl -X POST http://localhost:8000/pipeline/run
```

---

## Environment Variables

```
NEWSAPI_KEY=
GROQ_API_KEY=
HF_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
```

---

## Notes

- The free Render tier spins down after 15 minutes of inactivity. Cron-job.org pings the backend every 5 minutes to keep it alive and ensure the 7am scheduler fires reliably.
- Articles are deduped by URL hash before storing in Qdrant, so running the pipeline twice won't create duplicates.
