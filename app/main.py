from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets

from app.database import init_db, SessionLocal, get_db
from app.models import ApiKey
from app.endpoints import bus, products
from sqlalchemy.orm import Session

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="STM Contrib API",
    description="Community-driven transit card data contribution server",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bus.router)
app.include_router(products.router)


@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    existing = db.query(ApiKey).filter(ApiKey.is_admin == True).first()
    if not existing:
        admin_key = secrets.token_hex(32)
        key_record = ApiKey(key=admin_key, label="auto-generated admin", is_admin=True)
        db.add(key_record)
        db.commit()
        print(f"\n{'='*60}")
        print(f"  ADMIN API KEY: {admin_key}")
        print(f"  Save this! It won't be shown again.")
        print(f"{'='*60}\n")
    db.close()


@app.get("/")
def root():
    return {"service": "STM Contrib API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/keys/generate")
def generate_key(label: str = "", admin: bool = False, db: Session = Depends(get_db)):
    """Generate a new API key."""
    key = secrets.token_hex(32)
    record = ApiKey(key=key, label=label, is_admin=admin)
    db.add(record)
    db.commit()
    return {"api_key": key, "label": label, "is_admin": admin}