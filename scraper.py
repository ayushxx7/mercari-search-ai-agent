import asyncio
from mercapi import Mercapi
from models import Product, Base
from config import engine, SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import uuid

Base.metadata.create_all(bind=engine)

KEYWORDS = [
    # Japanese
    "スマートフォン", "バッグ", "イヤホン", "ゲーム", "カメラ", "時計", "服", "パソコン", "おもちゃ", "本", "家具", "家電", "自転車", "靴", "アクセサリー", "コスメ", "スポーツ", "アウトドア", "楽器", "車", "バイク", "タブレット", "テレビ", "冷蔵庫", "洗濯機", "エアコン", "フィギュア", "ドレス", "スニーカー", "財布", "リュック", "ネックレス", "ピアス", "指輪", "香水", "化粧品", "ゴルフ", "釣り", "登山", "ギター", "ピアノ", "バイオリン", "自動車部品", "バイク部品",
    # English
    "smartphone", "bag", "earphones", "game", "camera", "watch", "clothes", "laptop", "toy", "book", "furniture", "appliance", "bicycle", "shoes", "accessory", "cosmetics", "sports", "outdoor", "instrument", "car", "motorcycle", "tablet", "tv", "refrigerator", "washing machine", "air conditioner", "figure", "dress", "sneakers", "wallet", "backpack", "necklace", "earrings", "ring", "perfume", "makeup", "golf", "fishing", "mountain", "guitar", "piano", "violin", "car parts", "motorcycle parts"
]

async def scrape_mercari(keywords=KEYWORDS, items_per_keyword=5):
    scraped_count = 0
    m = Mercapi()
    
    with SessionLocal() as session:
        for keyword in keywords:
            print(f"Searching Mercari for: {keyword}")
            try:
                results = await m.search(keyword)
                print(f"Found {results.meta.num_found} results. Fetching top {items_per_keyword}...")
                
                # Take only the first N items for this keyword
                for idx, item in enumerate(results.items[:items_per_keyword]):
                    try:
                        # Fetch full details for each item
                        full_item = await item.full_item()
                        title = full_item.name
                        price_val = float(full_item.price)
                        product_url = f"https://jp.mercari.com/item/{full_item.id_}"
                        image_url = full_item.photos[0] if full_item.photos else None
                        category = full_item.category_name if hasattr(full_item, 'category_name') else None
                        condition = full_item.item_condition_name if hasattr(full_item, 'item_condition_name') else None
                        
                        # Try to get seller rating if available
                        seller_rating = None
                        if hasattr(full_item, 'seller') and hasattr(full_item.seller, 'ratings'):
                            ratings = full_item.seller.ratings
                            if hasattr(ratings, 'good'):
                                seller_rating = float(ratings.good)

                        if not (title and price_val and product_url):
                            print(f"Skipping item {idx+1}: missing required fields.")
                            continue

                        product = Product(
                            id=str(uuid.uuid4()),
                            title=title.strip(),
                            price=price_val,
                            condition=condition,
                            seller_rating=seller_rating,
                            image_url=image_url,
                            product_url=product_url,
                            category=category,
                            scraped_at=datetime.now(timezone.utc)
                        )
                        session.add(product)
                        
                        # Commit every 10 items or at the end of a keyword
                        if scraped_count % 10 == 0:
                            session.commit()
                            
                        scraped_count += 1
                        print(f"Saved product {idx+1} for keyword '{keyword}': {title}")
                    except IntegrityError:
                        session.rollback()
                        print(f"Product {idx+1} for keyword '{keyword}' already exists in DB. Skipping.")
                    except Exception as e:
                        session.rollback()
                        print(f"Error saving product {idx+1} for keyword '{keyword}': {e}")
                
                # Final commit for the keyword
                session.commit()
                
            except Exception as e:
                print(f"Error searching for keyword '{keyword}': {e}")
                continue
                
    print(f"✅ Scraped and saved {scraped_count} items from Mercari using mercapi.")

if __name__ == "__main__":
    asyncio.run(scrape_mercari())
