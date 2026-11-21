from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import ProductSubmission, ProductVote
from app.schemas import ProductSubmitRequest, ProductVoteRequest, ProductResponse
from app.auth import verify_api_key

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.post("/submit")
async def submit_product(req: ProductSubmitRequest, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    """Submit or upvote a product code → name mapping."""
    existing = db.query(ProductSubmission).filter(
        ProductSubmission.product_code == req.product_code,
        ProductSubmission.product_name == req.product_name,
    ).first()

    if existing:
        vote = ProductVote(submission_id=existing.id, api_key_id=0, vote=1)
        db.add(vote)
        existing.vote_score += 1
        db.commit()
        return {"status": "upvoted", "id": existing.id, "score": existing.vote_score}

    sub = ProductSubmission(
        product_code=req.product_code,
        product_name=req.product_name,
        operator_id=req.operator_id,
        api_key_id=0,
        vote_score=1,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    vote = ProductVote(submission_id=sub.id, api_key_id=0, vote=1)
    db.add(vote)
    db.commit()

    return {"status": "submitted", "id": sub.id}


@router.post("/vote")
async def vote_product(req: ProductVoteRequest, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    """Vote on a product name submission."""
    sub = db.query(ProductSubmission).filter(ProductSubmission.id == req.submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    vote = ProductVote(submission_id=req.submission_id, api_key_id=0, vote=req.vote)
    db.add(vote)
    sub.vote_score += req.vote
    db.commit()

    return {"status": "ok", "id": req.submission_id, "score": sub.vote_score}


@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    """Get all product code submissions with score >= 3 (community consensus)."""
    results = db.query(ProductSubmission).filter(
        ProductSubmission.vote_score >= 3,
    ).order_by(ProductSubmission.vote_score.desc()).all()

    seen = set()
    unique = []
    for p in results:
        if p.product_code not in seen:
            seen.add(p.product_code)
            unique.append(ProductResponse(
                product_code=p.product_code,
                product_name=p.product_name,
                operator_id=p.operator_id,
                confirmed=True,
                vote_score=p.vote_score,
            ))

    return unique


@router.get("/search")
def search_products(q: str, db: Session = Depends(get_db)):
    """Search product codes by name fragment (score >= 3 only)."""
    results = db.query(ProductSubmission).filter(
        ProductSubmission.product_name.ilike(f"%{q}%"),
        ProductSubmission.vote_score >= 3,
    ).all()

    seen = set()
    unique = []
    for p in results:
        if p.product_code not in seen:
            seen.add(p.product_code)
            unique.append(ProductResponse(
                product_code=p.product_code,
                product_name=p.product_name,
                operator_id=p.operator_id,
                confirmed=True,
                vote_score=p.vote_score,
            ))

    return unique