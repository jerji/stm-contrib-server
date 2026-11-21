from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func
from app.database import Base


class BusVote(Base):
    """A vote associating a bus name → operator ID + bus ID."""
    __tablename__ = "bus_votes"
    id = Column(Integer, primary_key=True, index=True)
    bus_name = Column(String(128), nullable=False, index=True)
    operator_id = Column(Integer, nullable=False)
    bus_id = Column(Integer, nullable=False)
    api_key_id = Column(Integer, nullable=False)
    vote = Column(Integer, default=1)  # +1 confirm, -1 reject
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BusSubmission(Base):
    """A submission of an unknown bus/operator name."""
    __tablename__ = "bus_submissions"
    id = Column(Integer, primary_key=True, index=True)
    bus_name = Column(String(128), nullable=False)
    operator_name = Column(String(128), nullable=False)
    api_key_id = Column(Integer, nullable=False)
    card_data = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProductSubmission(Base):
    """A product code → name mapping submission."""
    __tablename__ = "product_submissions"
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(Integer, nullable=False, index=True)
    product_name = Column(String(256), nullable=False)
    operator_id = Column(Integer, default=0)
    api_key_id = Column(Integer, nullable=False)
    confirmed = Column(Boolean, default=False)
    vote_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProductVote(Base):
    """A vote on a product name submission."""
    __tablename__ = "product_votes"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, nullable=False, index=True)
    api_key_id = Column(Integer, nullable=False)
    vote = Column(Integer, default=1)  # +1 agree, -1 disagree
    created_at = Column(DateTime(timezone=True), server_default=func.now())