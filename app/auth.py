from fastapi import HTTPException, status, Request
import os

CONFIG_PATH = "/app/data/api_key.txt"


def _load_key() -> str:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return f.read().strip()
    return ""


async def verify_api_key(request: Request):
    """Extract API key from X-API-Key header and validate it."""
    api_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    current = _load_key()
    if api_key != current:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return api_key