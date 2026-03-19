"""AI Agent API endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.schemas import AgentRequest, AgentResponse
from app.agent.portfolio_agent import PortfolioAgent
from app.models.models import AgentAction

router = APIRouter()


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest, db: Session = Depends(get_db)):
    """Send a message to the AI agent."""
    agent = PortfolioAgent(db)
    result = await agent.process(request.message, request.client_id)
    return AgentResponse(
        response=result["response"],
        actions_taken=result["actions_taken"],
        context_used=result["context_used"],
    )


@router.get("/history")
def agent_history(client_id: str = None, limit: int = 20, db: Session = Depends(get_db)):
    """Get agent action history."""
    query = db.query(AgentAction).order_by(AgentAction.created_at.desc())
    if client_id:
        query = query.filter(AgentAction.client_id == client_id)
    actions = query.limit(limit).all()
    return [
        {
            "id": a.id,
            "client_id": a.client_id,
            "action_type": a.action_type,
            "description": a.description,
            "status": a.status,
            "created_at": str(a.created_at),
        }
        for a in actions
    ]
