
import csv, os
from datetime import datetime
from backend.db import SessionLocal
from backend import crud
from pathlib import Path

def load_mock_csv():
    path = Path(__file__).resolve().parents[1] / 'sample_emails.csv'
    if not path.exists():
        return 0
    db = SessionLocal()
    count = 0
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sender = r.get('sender') or r.get('from') or 'unknown@example.com'
            subject = r.get('subject') or ''
            body = r.get('body') or ''
            received_at = r.get('sent_date') or r.get('date') or None
            try:
                if received_at:
                    received_at = datetime.strptime(received_at, '%d-%m-%Y %H:%M')
                else:
                    received_at = datetime.utcnow()
            except Exception:
                received_at = datetime.utcnow()
            crud.create_email(db, sender=sender, subject=subject, body=body, received_at=received_at)
            count += 1
    db.close()
    return count

if __name__ == '__main__':
    print('Imported:', load_mock_csv())
