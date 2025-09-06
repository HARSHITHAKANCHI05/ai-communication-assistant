
from sqlalchemy.orm import Session
from backend import models
from datetime import datetime

def get_emails(db: Session, limit: int = 200):
    return db.query(models.Email).order_by(models.Email.received_at.desc()).limit(limit).all()

def get_email(db: Session, email_id: int):
    return db.query(models.Email).filter(models.Email.id == email_id).first()

def create_email(db: Session, sender, subject, body, received_at=None):
    if received_at is None:
        received_at = datetime.utcnow()
    e = models.Email(sender=sender, subject=subject, body=body, received_at=received_at)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

def update_email(db: Session, email: models.Email):
    db.add(email)
    db.commit()
    db.refresh(email)
    return email
