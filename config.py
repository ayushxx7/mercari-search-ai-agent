import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st

# Helper to get secret from Streamlit or Environment
def get_secret(key, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)

# Default to local SQLite if no Postgres URL is provided
DB_URL = get_secret("DB_URL", "sqlite:///./mercari_local.db")

# SQLite needs special handling for concurrent access in some cases
if DB_URL.startswith("sqlite"):
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
