from sqlalchemy import Column, String, Float, DateTime, create_engine, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    condition = Column(String)
    seller_rating = Column(Float)
    image_url = Column(String)
    product_url = Column(String, nullable=False, unique=True)
    category = Column(String)
    seo_tags = Column(JSONB)
    scraped_at = Column(DateTime, default=datetime.utcnow)

Index('ix_products_title', Product.title)
Index('ix_products_category', Product.category)
Index('ix_products_seo_tags', Product.seo_tags, postgresql_using='gin', postgresql_ops={'seo_tags': 'jsonb_path_ops'}) 