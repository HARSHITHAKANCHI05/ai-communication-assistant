
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.db import SessionLocal, engine
from backend import models, crud, schemas
import os

app = FastAPI(title='Email Assistant Prototype')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event('startup')
def startup():
    models.Base.metadata.create_all(bind=engine)

@app.get('/emails', response_model=list[schemas.EmailOut])
def list_emails(limit: int = 200):
    db = SessionLocal()
    emails = crud.get_emails(db, limit=limit)
    db.close()
    return emails

@app.get('/emails/{email_id}', response_model=schemas.EmailOut)
def get_email(email_id: int):
    db = SessionLocal()
    e = crud.get_email(db, email_id)
    db.close()
    if not e:
        raise HTTPException(status_code=404, detail='Email not found')
    return e

@app.post('/emails/{email_id}/send')
def send_email(email_id: int):
    # In prototype, just mark as sent
    db = SessionLocal()
    e = crud.get_email(db, email_id)
    if not e:
        db.close()
        raise HTTPException(status_code=404, detail='Email not found')
    e.status = 'sent'
    crud.update_email(db, e)
    db.close()
    return {'ok': True, 'message': f'Email {email_id} marked as sent'}

@app.post('/fetch_mock')
def fetch_mock():
    # loads sample_emails.csv into DB (helper in backend.fetch_mock)
    from backend.fetch_mock import load_mock_csv
    n = load_mock_csv()
    return {'imported': n}
