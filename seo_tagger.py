from models import Product
from config import SessionLocal

KEYWORD_TAG_MAP = {
    "iphone": ["apple", "smartphone", "ios"],
    "android": ["android", "smartphone"],
    "switch": ["gaming", "nintendo"],
    "macbook": ["laptop", "apple"],
    "バッグ": ["fashion", "bag"],
    "イヤホン": ["audio", "earbuds"]
}

def rule_based_tags(title: str):
    title_lower = title.lower()
    tags = []
    for keyword, mapped_tags in KEYWORD_TAG_MAP.items():
        if keyword in title_lower:
            tags.extend(mapped_tags)
    return list(set(tags))

def tag_unprocessed_products():
    session = SessionLocal()
    products = session.query(Product).filter(Product.seo_tags == None).all()
    for p in products:
        tags = rule_based_tags(p.title)
        if tags:
            p.seo_tags = tags
    session.commit()
    session.close()
    print(f"✅ Tagged {len(products)} products.") 