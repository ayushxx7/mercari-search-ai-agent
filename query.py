from config import SessionLocal, DB_URL
from models import Product
from sqlalchemy import func, or_

def get_products(tags=None, category=None, keyword=None, min_price=None, max_price=None, min_rating=None, limit=30):
    with SessionLocal() as session:
        q = session.query(Product)
        
        if tags:
            # Handle cross-DB JSON tag searching
            if DB_URL.startswith("postgresql"):
                q = q.filter(Product.seo_tags.contains(tags))
            else:
                # SQLite-compatible tag matching
                for tag in tags:
                    q = q.filter(Product.seo_tags.like(f'%"{tag}"%'))
        
        if category:
            q = q.filter(func.lower(Product.category) == category.lower())
            
        if keyword:
            # Multi-word/Multilingual keyword matching
            # Split by spaces if it's a single string, or handle list
            keywords = keyword if isinstance(keyword, list) else keyword.split()
            
            # Use OR logic for multiple keywords to increase recall (multilingual support)
            keyword_filters = []
            for kw in keywords:
                if len(kw) < 2: continue # Skip very short tokens
                keyword_filters.append(Product.title.ilike(f"%{kw}%"))
            
            if keyword_filters:
                q = q.filter(or_(*keyword_filters))
            
        if min_price is not None:
            q = q.filter(Product.price >= min_price)
            
        if max_price is not None:
            q = q.filter(Product.price <= max_price)
            
        if min_rating is not None:
            q = q.filter(Product.seller_rating >= min_rating)
            
        # Order by price/scraped_at or relevance could be added here
        return [p.__dict__ for p in q.limit(limit).all()]

# Backward compatibility functions
def get_products_by_tags(tags: list, limit=10):
    return get_products(tags=tags, limit=limit)

def get_products_by_category(category: str, limit=10):
    return get_products(category=category, limit=limit)

def search_products_by_title(keyword: str, limit=None):
    return get_products(keyword=keyword, limit=limit if limit else 100)
