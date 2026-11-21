from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
CONFIG_PATH = "/app/data/api_key.txt"


def _load_key() -> str:
    """Load the API key from the config file."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return f.read().strip()
    return ""


def verify_api_key(api_key: str = API_KEY_HEADER):
    current = _load_key()
    if not api_key or api_key != current:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return api_key