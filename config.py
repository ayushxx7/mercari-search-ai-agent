import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = os.environ.get("DB_URL", "postgresql://postgres:yourpassword@localhost:5432/mercari_db")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine) 