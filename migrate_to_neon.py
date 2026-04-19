import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Product, Base
from config import DB_URL

# Path to local SQLite
LOCAL_DB_PATH = "mercari_local.db"
LOCAL_DB_URL = f"sqlite:///./{LOCAL_DB_PATH}"

def migrate():
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"❌ Local database '{LOCAL_DB_PATH}' not found. Nothing to migrate.")
        return

    # In this script, we assume the DB_URL in config is the TARGET (NeonDB)
    # and LOCAL_DB_URL is the source.
    if "sqlite" in DB_URL:
        print("❌ Error: DB_URL in config is currently set to SQLite. Please set DB_URL in your .env to your NeonDB URL before running this script.")
        return

    print(f"🔄 Migrating data from {LOCAL_DB_URL} to {DB_URL}...")

    # Engines for both
    local_engine = create_engine(LOCAL_DB_URL)
    neon_engine = create_engine(DB_URL)

    # Ensure tables exist in Neon
    print("🛠️ Creating tables in NeonDB if they don't exist...")
    Base.metadata.create_all(bind=neon_engine)

    # Sessions
    LocalSession = sessionmaker(bind=local_engine)
    NeonSession = sessionmaker(bind=neon_engine)

    with LocalSession() as local_session:
        # Fetch all products from SQLite
        products = local_session.query(Product).all()
        print(f"📦 Found {len(products)} products in local database.")

        if not products:
            print("No data to migrate.")
            return

        with NeonSession() as neon_session:
            # Check for existing URLs in Neon to avoid duplicates
            existing_urls = {p.product_url for p in neon_session.query(Product.product_url).all()}
            
            new_products = []
            for p in products:
                if p.product_url not in existing_urls:
                    # Clear session state for the object to add it to a new session
                    # We create a new Product instance to be safe
                    new_p = Product(
                        id=p.id,
                        title=p.title,
                        price=p.price,
                        condition=p.condition,
                        seller_rating=p.seller_rating,
                        image_url=p.image_url,
                        product_url=p.product_url,
                        category=p.category,
                        seo_tags=p.seo_tags,
                        scraped_at=p.scraped_at
                    )
                    new_products.append(new_p)
            
            if new_products:
                neon_session.add_all(new_products)
                neon_session.commit()
                print(f"✅ Successfully migrated {len(new_products)} NEW products to NeonDB.")
            else:
                print("✨ No new products to migrate (they already exist in Neon).")

if __name__ == "__main__":
    migrate()
