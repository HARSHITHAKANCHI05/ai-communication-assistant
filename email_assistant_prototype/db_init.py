
from backend.db import engine
from backend import models
models.Base.metadata.create_all(bind=engine)
print('DB initialized at data/emails.db')
