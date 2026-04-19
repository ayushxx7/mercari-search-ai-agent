import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Default to local SQLite if no Postgres URL is provided
# This ensures the app works immediately on local machines
DB_URL = os.environ.get("DB_URL", "sqlite:///./mercari_local.db")

# SQLite needs special handling for concurrent access in some cases
if DB_URL.startswith("sqlite"):
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
