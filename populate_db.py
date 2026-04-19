import uuid
from datetime import datetime, timezone
from models import Product, Base
from config import engine, SessionLocal
import random

# Initial keywords map for SEO tags
KEYWORD_TAG_MAP = {
    "iPhone": ["apple", "smartphone", "ios"],
    "Samsung": ["android", "smartphone"],
    "Switch": ["gaming", "nintendo"],
    "MacBook": ["laptop", "apple"],
    "Sony": ["audio", "camera"],
    "Nike": ["shoes", "sneakers"],
    "Bag": ["fashion", "bag"]
}

def populate():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as session:
        # Check if we already have data
        if session.query(Product).count() > 0:
            print("Database already has data. Skipping population.")
            return

        print("Populating database with sample products...")
        
        products = []
        for i in range(50):
            brand = random.choice(list(KEYWORD_TAG_MAP.keys()))
            tags = KEYWORD_TAG_MAP[brand]
            price = random.randint(5000, 150000)
            rating = random.randint(10, 500)
            
            p = Product(
                id=str(uuid.uuid4()),
                title=f"{brand} {random.choice(['Pro', 'Max', 'Ultra', 'Elite'])} Edition {i+1}",
                price=float(price),
                condition=random.choice(["New", "Used - Like New", "Used - Good"]),
                seller_rating=float(rating),
                image_url=f"https://picsum.photos/seed/{i}/400/400",
                product_url=f"https://jp.mercari.com/item/m{random.randint(100000000, 999999999)}",
                category="Electronics" if brand in ["iPhone", "Samsung", "Switch", "MacBook", "Sony"] else "Fashion",
                seo_tags=tags,
                scraped_at=datetime.now(timezone.utc)
            )
            products.append(p)
            
        session.add_all(products)
        session.commit()
        print(f"✅ Added {len(products)} sample products to the database.")

if __name__ == "__main__":
    populate()
