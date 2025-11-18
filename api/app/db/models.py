# api/app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(128), unique=True, index=True, nullable=True)
    raw = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    service = Column(String(128), index=True)
    message = Column(Text, nullable=True)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    severity = Column(String(32), default="low")
    status = Column(String(32), default="open")  # open, mitigating, mitigated, resolved
    recommended_actions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    event = relationship("Event", backref="anomalies")

class Mitigation(Base):
    __tablename__ = "mitigations"
    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=False)
    action = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    status = Column(String(32), default="pending")  # pending, done, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
