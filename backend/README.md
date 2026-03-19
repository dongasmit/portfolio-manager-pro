# Backend — FastAPI Portfolio Manager API

The backend is a **FastAPI** application providing REST APIs for portfolio management, an AI chat agent, and a RAG pipeline for compliance document retrieval.

## Tech Stack

- **Framework:** FastAPI 0.115
- **Database:** PostgreSQL (Neon) via SQLAlchemy 2.0
- **AI/LLM:** Groq (Llama 3.3 70B Versatile)
- **RAG:** ChromaDB + LangChain for document retrieval
- **Market Data:** Kite Connect API (optional)
- **Calculations:** XIRR (pyxirr), CAGR, P&L analytics

## API Endpoints

### Core APIs

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/clients/` | List all clients |
| `GET` | `/api/clients/{id}` | Get client details |
| `GET` | `/api/clients/{id}/summary` | Full client portfolio summary |
| `GET` | `/api/portfolios/{id}` | Portfolio with holdings |
| `GET` | `/api/analytics/dashboard` | Dashboard overview (AUM, all clients) |
| `GET` | `/api/analytics/portfolio/{id}/xirr` | XIRR calculation |
| `GET` | `/api/analytics/portfolio/{id}/allocation` | Asset & sector allocation |

### AI Agent

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/agent/chat` | Chat with AI agent |

**Request body:**
```json
{
  "message": "Show me John's portfolio",
  "client_id": "client-001"
}
```

### Documents (RAG)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/documents/upload` | Upload PDF/text documents |
| `GET` | `/api/documents/` | List indexed documents |

## Local Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your credentials

python seed_data.py        # Seed sample clients & portfolios
python seed_documents.py   # Seed compliance documents into ChromaDB

uvicorn app.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for interactive Swagger API docs.

## Deploy to Render

1. Create a **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Set **Root Directory** to `backend`
4. **Build Command:** `pip install -r requirements.txt && python seed_data.py && python seed_documents.py`
5. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables: `DATABASE_URL`, `GROQ_API_KEY`, `SECRET_KEY`, `FRONTEND_URL`

## Project Structure

```
backend/
├── app/
│   ├── agent/
│   │   ├── gemini_client.py    # LLM client (Groq/Llama 3.3)
│   │   └── portfolio_agent.py  # AI agent logic
│   ├── api/
│   │   ├── agent.py            # /api/agent routes
│   │   ├── analytics.py        # /api/analytics routes
│   │   ├── clients.py          # /api/clients routes
│   │   ├── documents.py        # /api/documents routes
│   │   └── portfolios.py       # /api/portfolios routes
│   ├── models/
│   │   └── models.py           # SQLAlchemy models
│   ├── rag/
│   │   └── pipeline.py         # ChromaDB RAG pipeline
│   ├── services/
│   │   ├── kite_service.py     # Market data service
│   │   └── portfolio_service.py # Portfolio calculations
│   ├── config.py
│   ├── database.py
│   └── main.py
├── data/                       # Seed data JSON files
├── render.yaml                 # Render deployment blueprint
├── requirements.txt
├── seed_data.py
└── seed_documents.py
```
