from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ApiKey

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(db: Session = Depends(get_db), api_key: str = Depends(API_KEY_HEADER)):
    """Verify API key exists and is active."""
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    key_record = db.query(ApiKey).filter(ApiKey.key == api_key, ApiKey.is_active == True).first()
    if not key_record:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or inactive API key")
    return key_record


def verify_admin_key(key: ApiKey = Depends(verify_api_key)):
    """Verify the API key has admin privileges."""
    if not key.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return key