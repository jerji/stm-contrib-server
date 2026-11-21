from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets
import os

from app.database import init_db
from app.endpoints import bus, products
from app.auth import CONFIG_PATH

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
    # Generate API key on first boot
    if not os.path.exists(CONFIG_PATH):
        key = secrets.token_hex(32)
        with open(CONFIG_PATH, "w") as f:
            f.write(key)
        print(f"\n{'='*60}")
        print(f"  API KEY: {key}")
        print(f"  Saved to {CONFIG_PATH}")
        print(f"{'='*60}\n")


@app.get("/")
def root():
    return {"service": "STM Contrib API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}