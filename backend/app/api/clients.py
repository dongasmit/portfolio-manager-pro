"""Client management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Client
from app.api.schemas import ClientCreate, ClientResponse
from app.services.portfolio_service import get_client_summary

router = APIRouter()


@router.get("/")
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "risk_profile": c.risk_profile,
            "target_equity_pct": c.target_equity_pct,
            "target_debt_pct": c.target_debt_pct,
        }
        for c in clients
    ]


@router.get("/{client_id}")
def get_client(client_id: str, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {
        "id": client.id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "risk_profile": client.risk_profile,
        "target_equity_pct": client.target_equity_pct,
        "target_debt_pct": client.target_debt_pct,
    }


@router.post("/")
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    client = Client(
        name=data.name,
        email=data.email,
        phone=data.phone,
        risk_profile=data.risk_profile,
        target_equity_pct=data.target_equity_pct,
        target_debt_pct=data.target_debt_pct,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"id": client.id, "name": client.name, "email": client.email}


@router.get("/{client_id}/summary")
def client_summary(client_id: str, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return get_client_summary(db, client_id)


@router.put("/{client_id}")
def update_client(client_id: str, data: ClientCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.name = data.name
    client.email = data.email
    client.phone = data.phone
    client.risk_profile = data.risk_profile
    client.target_equity_pct = data.target_equity_pct
    client.target_debt_pct = data.target_debt_pct
    db.commit()
    return {"id": client.id, "name": client.name, "status": "updated"}
