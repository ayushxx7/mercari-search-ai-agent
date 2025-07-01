from config import SessionLocal
from models import Product
from sqlalchemy import func

def get_products_by_tags(tags: list, limit=10):
    session = SessionLocal()
    q = session.query(Product).filter(Product.seo_tags.contains(tags))
    return [p.__dict__ for p in q.limit(limit)]

def get_products_by_category(category: str, limit=10):
    session = SessionLocal()
    q = session.query(Product).filter(func.lower(Product.category) == category.lower())
    return [p.__dict__ for p in q.limit(limit)]

def search_products_by_title(keyword: str, limit=None):
    session = SessionLocal()
    q = session.query(Product).filter(Product.title.ilike(f"%{keyword}%"))
    if limit:
        return [p.__dict__ for p in q.limit(limit)]
    else:
        return [p.__dict__ for p in q] 