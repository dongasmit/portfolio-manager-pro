# 🏦 Agentic AI Portfolio Manager

A full-stack **B2B wealth management platform** powered by an AI agent that helps financial advisors manage client portfolios, perform rebalancing, analyze risk, and ensure SEBI compliance.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js_16-000000?style=flat&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Llama_3.3_70B-orange?style=flat)

## ✨ Features

- **AI-Powered Chat Agent** — Natural language portfolio assistant using Llama 3.3 70B (via Groq)
- **Portfolio Tracking** — Real-time holdings, P&L, XIRR, CAGR across multiple portfolios
- **Smart Rebalancing** — AI-driven target allocation with trade calculations
- **Risk Analysis** — Position & sector concentration analysis with warnings
- **RAG-based Compliance** — Upload SEBI circulars, query regulations in natural language
- **Market Data Integration** — Kite Connect API for live equity/MF prices
- **Beautiful Dashboard** — Dark-themed premium UI with charts and analytics

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────────────────────┐
│   Next.js 16    │────▶│         FastAPI Backend           │
│   (Vercel)      │     │                                  │
│                 │     │  ┌──────────┐  ┌──────────────┐  │
│  • Dashboard    │     │  │ AI Agent │  │ RAG Pipeline │  │
│  • Client View  │     │  │ (Groq)   │  │ (ChromaDB)   │  │
│  • AI Chat      │     │  └──────────┘  └──────────────┘  │
│  • Charts       │     │  ┌──────────┐  ┌──────────────┐  │
└─────────────────┘     │  │ Kite API │  │ PostgreSQL   │  │
                        │  │ (Market) │  │ (Neon)       │  │
                        │  └──────────┘  └──────────────┘  │
                        │           (Render)               │
                        └──────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (or [Neon](https://neon.tech) free cloud DB)
- [Groq API key](https://console.groq.com/keys) (free)

### 1. Clone the repo

```bash
git clone https://github.com/dongasmit/portfolio-manager-pro.git
cd portfolio-manager-pro
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from example
cp .env.example .env
# Edit .env with your actual keys

# Seed database
python seed_data.py
python seed_documents.py

# Start server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Start dev server
npm run dev
```

Open **http://localhost:3000** — the dashboard should load with sample data.

## 🤖 AI Agent

The chat agent (bottom-right bubble) understands natural language:

| Command | Example |
|---|---|
| Portfolio queries | *"Show me John's portfolio"* |
| Rebalancing | *"Rebalance to 60% equity / 40% debt"* |
| Risk analysis | *"Analyze portfolio risk"* |
| Compliance | *"What do SEBI guidelines say about concentration?"* |
| Market updates | *"Refresh market prices"* |

The agent uses a hybrid architecture:
1. **Intent classification** (keyword-based) determines the action
2. **Structured data** is gathered from the database
3. **Llama 3.3 70B** (via Groq) generates a natural language response
4. Falls back to raw data if the LLM is unavailable

## 🌐 Deployment

| Service | Platform | Docs |
|---|---|---|
| Frontend | Vercel | [frontend/README.md](./frontend/README.md) |
| Backend | Render | [backend/README.md](./backend/README.md) |
| Database | Neon PostgreSQL | [neon.tech](https://neon.tech) |

## 📁 Project Structure

```
portfolio-manager-pro/
├── backend/
│   ├── app/
│   │   ├── agent/          # AI agent + Groq LLM client
│   │   ├── api/            # FastAPI route handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── rag/            # RAG pipeline (ChromaDB)
│   │   ├── services/       # Business logic
│   │   ├── config.py       # App settings
│   │   ├── database.py     # DB connection
│   │   └── main.py         # FastAPI app entry point
│   ├── data/               # Seed data files
│   ├── render.yaml         # Render deployment config
│   ├── requirements.txt
│   └── seed_data.py        # DB seeder
├── frontend/
│   ├── app/
│   │   ├── components/     # React components
│   │   ├── lib/            # API client
│   │   ├── clients/        # Client pages
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Dashboard page
│   ├── next.config.ts
│   └── package.json
└── .gitignore
```

## 🔑 Environment Variables

See [backend/.env.example](./backend/.env.example) for all required variables.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `GROQ_API_KEY` | ✅ | Groq API key for LLM responses |
| `KITE_API_KEY` | ❌ | Kite Connect for live market data |
| `KITE_API_SECRET` | ❌ | Kite Connect API secret |
| `GEMINI_API_KEY` | ❌ | Google Gemini (for RAG embeddings) |
| `NEXT_PUBLIC_API_URL` | ❌ | Backend API URL (frontend, defaults to localhost:8000) |

## 📄 License

This project is for educational and portfolio demonstration purposes.
