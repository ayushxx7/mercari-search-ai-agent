from sqlalchemy import Column, String, Float, DateTime, create_engine, Index, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime, timezone
from config import DB_URL

Base = declarative_base()

# Helper for cross-DB compatibility
def get_json_type():
    if DB_URL.startswith("postgresql"):
        return JSONB
    return JSON

class Product(Base):
    __tablename__ = 'products'

    # Using String for ID if not Postgres to simplify SQLite usage
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    condition = Column(String)
    seller_rating = Column(Float)
    image_url = Column(String)
    product_url = Column(String, nullable=False, unique=True)
    category = Column(String)
    seo_tags = Column(get_json_type())
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

if DB_URL.startswith("postgresql"):
    Index('ix_products_title', Product.title)
    Index('ix_products_category', Product.category)
    Index('ix_products_seo_tags', Product.seo_tags, postgresql_using='gin', postgresql_ops={'seo_tags': 'jsonb_path_ops'})
else:
    # Simpler indices for SQLite
    Index('ix_products_title', Product.title)
    Index('ix_products_category', Product.category)
