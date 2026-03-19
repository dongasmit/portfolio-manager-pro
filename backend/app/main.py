from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import clients, portfolios, analytics, documents, agent
import os

app = FastAPI(
    title="Agentic AI Portfolio Manager",
    description="B2B portfolio tracking with AI-powered rebalancing and RAG-based compliance",
    version="1.0.0",
)

# Build CORS origins: always allow localhost, plus deployed frontend URL if set
allowed_origins = ["http://localhost:3000"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(portfolios.router, prefix="/api/portfolios", tags=["Portfolios"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(agent.router, prefix="/api/agent", tags=["AI Agent"])


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "portfolio-manager"}
