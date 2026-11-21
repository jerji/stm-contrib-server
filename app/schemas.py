from pydantic import BaseModel, Field
from typing import Optional


class BusVoteRequest(BaseModel):
    bus_name: str = Field(..., min_length=1, max_length=128)
    operator_id: int = Field(..., ge=0, le=255)
    bus_id: int = Field(..., ge=0, le=511)
    vote: int = Field(default=1, ge=-1, le=1)  # 1 = confirm, -1 = reject


class BusSubmitRequest(BaseModel):
    bus_name: str = Field(..., min_length=1, max_length=128)
    operator_name: str = Field(..., min_length=1, max_length=128)
    card_data: Optional[str] = Field(default=None, max_length=65535)


class ProductSubmitRequest(BaseModel):
    product_code: int = Field(..., ge=0, le=65535)
    product_name: str = Field(..., min_length=1, max_length=256)
    operator_id: int = Field(default=0, ge=0, le=255)


class ProductVoteRequest(BaseModel):
    submission_id: int = Field(..., ge=1)
    vote: int = Field(default=1, ge=-1, le=1)


class ProductResponse(BaseModel):
    product_code: int
    product_name: str
    operator_id: int
    confirmed: bool
    vote_score: int