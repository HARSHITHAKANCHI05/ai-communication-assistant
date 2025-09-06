
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / 'emails.db'
DATABASE_URL = f'sqlite:///{DB_PATH}'
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
