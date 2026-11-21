from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Single built-in API key for the app
# Override via STM_CONTRIB_API_KEY env var for deployment
BUILTIN_API_KEY = os.environ.get("STM_CONTRIB_API_KEY", "lecteuropus-builtin-key-change-me")


def verify_api_key(api_key: str = API_KEY_HEADER):
    if not api_key or api_key != BUILTIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return api_key