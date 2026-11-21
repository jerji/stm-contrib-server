from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import BusVote, BusSubmission, ApiKey
from app.schemas import BusVoteRequest, BusSubmitRequest
from app.auth import verify_api_key

router = APIRouter(prefix="/api/v1/bus", tags=["bus"])


@router.post("/vote")
def vote_bus(req: BusVoteRequest, db: Session = Depends(get_db), key: ApiKey = Depends(verify_api_key)):
    """Vote to confirm (+1) or reject (-1) a bus name → operator/bus ID mapping."""
    vote = BusVote(
        bus_name=req.bus_name,
        operator_id=req.operator_id,
        bus_id=req.bus_id,
        vote=req.vote,
        api_key_id=key.id,
    )
    db.add(vote)
    db.commit()

    # Count net votes for this bus name + operator_id + bus_id combo
    net = db.query(BusVote).filter(
        BusVote.bus_name == req.bus_name,
        BusVote.operator_id == req.operator_id,
        BusVote.bus_id == req.bus_id,
    ).with_entities(db.func.coalesce(db.func.sum(BusVote.vote), 0)).scalar()

    return {"status": "ok", "bus_name": req.bus_name, "operator_id": req.operator_id, "bus_id": req.bus_id, "net_score": net}


@router.post("/submit")
def submit_bus(req: BusSubmitRequest, db: Session = Depends(get_db), key: ApiKey = Depends(verify_api_key)):
    """Submit an unknown bus/operator pair for manual review."""
    sub = BusSubmission(
        bus_name=req.bus_name,
        operator_name=req.operator_name,
        card_data=req.card_data or "",
        api_key_id=key.id,
    )
    db.add(sub)
    db.commit()
    return {"status": "ok", "id": sub.id}


@router.get("/votes")
def get_bus_votes(bus_name: str, db: Session = Depends(get_db)):
    """Get aggregated vote counts for a bus name. No auth required (read-only)."""
    results = db.query(
        BusVote.operator_id, BusVote.bus_id,
        db.func.coalesce(db.func.sum(BusVote.vote), 0).label("score")
    ).filter(BusVote.bus_name == bus_name).group_by(BusVote.operator_id, BusVote.bus_id).all()

    return {"bus_name": bus_name, "mappings": [
        {"operator_id": r.operator_id, "bus_id": r.bus_id, "score": r.score} for r in results
    ]}