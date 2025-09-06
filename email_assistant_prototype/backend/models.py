
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True)
    sender = Column(String(256))
    subject = Column(String(512))
    body = Column(Text)
    received_at = Column(DateTime)
    filtered = Column(Integer, default=0)  # 0/1
    sentiment = Column(String(32), default='unknown')
    sentiment_score = Column(Integer, nullable=True)
    priority = Column(String(32), default='unknown')
    priority_score = Column(Integer, nullable=True)
    extracted = Column(JSON, default={})
    draft = Column(Text, nullable=True)
    status = Column(String(32), default='pending')  # pending, processed, sent
