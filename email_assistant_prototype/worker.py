
import re, os, time, json
from datetime import datetime, timezone
from backend.db import SessionLocal
from backend import crud, models
from sqlalchemy import select
from sqlalchemy.orm import Session

# Optional OpenAI usage if OPENAI_API_KEY set
USE_OPENAI = bool(os.environ.get('OPENAI_API_KEY'))

if USE_OPENAI:
    import openai

FILTER_RE = re.compile(r'\b(support|help|request|query|urgent|issue|billing|refund|error|unable to log|cannot access|down)\b', re.I)
URGENT_RE = re.compile(r'\b(immediately|urgent|critical|down|cannot access|completely inaccessible|charged twice)\b', re.I)

PHONE_RE = re.compile(r'(\+?\d{7,15})')
EMAIL_RE = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')

def simple_sentiment(text: str):
    # Naive heuristic: count negative tokens
    neg_words = ['not', 'unable', "can't", 'cannot', 'never', 'error', 'fail', 'down', 'frustrat', 'angry']
    score = sum(text.lower().count(w) for w in neg_words)
    label = 'negative' if score>0 else 'neutral'
    return label, score

def generate_draft_simple(sender, subject, body, extracted):
    # short template
    summary = (body[:200] + '...') if len(body)>200 else body
    draft = f"Hi {sender.split('@')[0].title()},\\n\\nThanks for reaching out about \\\"{subject}\\\". We understand the issue: {summary}\\n\\nNext steps:\\n1) Please try logging out and logging back in.\\n2) If the issue persists, reply with any error messages or screenshots.\\n\\nBest,\\nSupport Team"
    return draft

def score_priority(text: str, sentiment_score: int, received_at: datetime):
    score = 0
    if URGENT_RE.search(text): score += 40
    if re.search(r'\\b(billing|charged twice|refund)\\b', text, re.I): score += 30
    if re.search(r'\\b(password|reset|login)\\b', text, re.I): score += 25
    if sentiment_score>0: score += 10
    # recency
    if received_at:
        delta = datetime.now(timezone.utc) - received_at.replace(tzinfo=timezone.utc)
        if delta.total_seconds() < 3600:
            score += 5
    return score

def extract_fields(text: str):
    phones = PHONE_RE.findall(text)
    emails = EMAIL_RE.findall(text)
    return {'phones': list(set(phones)), 'emails': list(set(emails))}

def process_once():
    db = SessionLocal()
    q = db.query(models.Email).filter(models.Email.status=='pending').limit(50).all()
    if not q:
        print('No pending emails to process.')
        db.close()
        return
    for e in q:
        print(f'Processing email id={e.id} subject={e.subject[:60]}')
        text = (e.subject or '') + '\\n' + (e.body or '')
        filtered = 1 if FILTER_RE.search(text) else 0
        e.filtered = filtered
        extracted = extract_fields(text)
        # sentiment
        if USE_OPENAI:
            try:
                resp = openai.Completion.create(model='text-davinci-003', prompt=f"Classify sentiment as Positive, Neutral, or Negative.\\n\\nText:\\n{text}", max_tokens=6, temperature=0)
                label = resp.choices[0].text.strip().lower()
                score = 1 if 'negative' in label else 0
            except Exception as ex:
                print('OpenAI error, falling back to simple:', ex)
                label, score = simple_sentiment(text)
        else:
            label, score = simple_sentiment(text)
        e.sentiment = label
        e.sentiment_score = score
        # priority
        received = e.received_at if e.received_at else datetime.now()
        pscore = score_priority(text, score, received)
        e.priority_score = pscore
        e.priority = 'Urgent' if pscore >= 60 else ('High' if pscore>=30 else 'Normal')
        e.extracted = extracted
        # draft
        if USE_OPENAI:
            try:
                prompt = f\"\"\"You are a helpful support agent. Given the email subject and body, write a concise, empathetic reply (<=200 words).\\nSubject: {e.subject}\\nBody: {e.body}\\n\"\"\"
                resp = openai.Completion.create(model='text-davinci-003', prompt=prompt, max_tokens=300, temperature=0.2)
                draft = resp.choices[0].text.strip()
            except Exception as ex:
                print('OpenAI draft error, using simple template', ex)
                draft = generate_draft_simple(e.sender, e.subject, e.body, extracted)
        else:
            draft = generate_draft_simple(e.sender, e.subject, e.body, extracted)
        e.draft = draft
        e.status = 'processed'
        db.add(e)
        db.commit()
        print(f'Processed id={e.id} priority={e.priority}')
    db.close()

if __name__ == '__main__':
    process_once()
