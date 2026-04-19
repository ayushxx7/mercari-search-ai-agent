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

try:
    if DB_URL.startswith("sqlite"):
        engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
    else:
        # For Postgres, use pool_pre_ping to handle idle connections
        engine = create_engine(DB_URL, pool_pre_ping=True)
except Exception as e:
    print(f"❌ Critical: Could not create database engine for {DB_URL}. Error: {e}")
    # Fallback to local SQLite if Postgres engine creation fails
    engine = create_engine("sqlite:///./mercari_local.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
