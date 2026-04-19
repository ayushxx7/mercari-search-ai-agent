import streamlit as st
from query import get_products
from llm_agent import extract_search_intent, recommend_products, translate_text
import json
import os
from sqlalchemy import text
from config import engine

st.set_page_config(layout="wide", page_title="🛒 Mercari Product Explorer")

# Check database connectivity first
db_ready = False
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        db_ready = True
except Exception as e:
    st.error(f"❌ Database connection failed. Please check your DB_URL environment variable.\nError: {e}")
    st.info("💡 Hint: If you're running locally, make sure PostgreSQL is running. If on Streamlit Cloud, add DB_URL to your secrets.")

st.sidebar.title("🔍 Filter Products")

tag_filter = st.sidebar.multiselect("SEO Tags", ["apple", "android", "smartphone", "gaming", "bag", "audio"])
min_price, max_price = st.sidebar.slider("Price Range", 0, 100000, (0, 50000))
min_rating = st.sidebar.slider("Min Seller Rating", 0.0, 1000.0, 0.0, 1.0)

search_term = st.text_input("🔎 Search for products", "")
use_ai = st.checkbox("🤖 AI Assistant (LLM-powered search & recommendations)")

if use_ai:
    provider = st.sidebar.radio(
        "LLM Provider",
        ["groq", "openrouter"],
        format_func=lambda x: "Groq" if x == "groq" else "OpenRouter",
        index=0
    )
else:
    provider = None

st.title("🛍️ Mercari Product Explorer")

products = []
recommendations = []

if db_ready and (search_term or tag_filter or (min_price > 0 or max_price < 100000)):
    with st.spinner("Searching..."):
        intent = {}
        if use_ai and search_term:
            try:
                intent_json = extract_search_intent(search_term, provider=provider)
                intent = json.loads(intent_json)
            except Exception as e:
                st.error(f"AI Assistant error: {e}")
        
        final_tags = list(set((intent.get("tags") or []) + tag_filter))
        final_keyword = " ".join(intent.get("keywords", [])) if intent.get("keywords") else search_term
        
        # Safely handle potential None values from intent
        intent_min = intent.get("min_price")
        if intent_min is None: intent_min = 0
        intent_max = intent.get("max_price")
        if intent_max is None: intent_max = 1e9
        
        final_min_price = max(intent_min, min_price)
        final_max_price = min(intent_max, max_price)
        final_category = intent.get("category")
        
        products = get_products(
            tags=final_tags if final_tags else None,
            category=final_category,
            keyword=final_keyword if final_keyword else None,
            min_price=final_min_price,
            max_price=final_max_price,
            min_rating=min_rating if min_rating > 0 else None,
            limit=30
        )

        if use_ai and products and search_term:
            with st.spinner("AI is recommending the best matches..."):
                try:
                    # Filter out SQLAlchemy internal state and keep essential fields for LLM
                    clean_products = []
                    for p in products[:15]:
                        clean_products.append({
                            "title": p.get("title"),
                            "price": p.get("price"),
                            "condition": p.get("condition"),
                            "seller_rating": p.get("seller_rating"),
                            "product_url": p.get("product_url"),
                            "image_url": p.get("image_url")
                        })
                    
                    rec_json = recommend_products(clean_products, search_term, provider=provider)
                    res = json.loads(rec_json)
                    recommendations = res.get("recommendations", [])
                except Exception as e:
                    st.warning(f"Failed to parse recommendations: {e}")
                    recommendations = []

if recommendations:
    st.subheader("🤖 Top 3 AI Recommendations")
    rec_cols = st.columns(3)
    for idx, rec in enumerate(recommendations[:3]):
        with rec_cols[idx]:
            if rec.get("image_url"):
                st.image(rec["image_url"], width="stretch")
            st.markdown(f"### {rec.get('title', 'Unknown Product')}")
            st.markdown(f"💴 **¥{rec.get('price', '???')}**")
            st.info(f"💡 {rec.get('reason', 'No reason provided.')}")
            url = rec.get('url') or rec.get('product_url')
            if url:
                st.link_button("View on Mercari", url)
    st.markdown("---")
    st.subheader("Other Matching Products")

if products:
    cols = st.columns(3)
    for idx, product in enumerate(products):
        with cols[idx % 3]:
            if product.get("image_url"):
                st.image(product["image_url"], width="stretch")
            else:
                st.write("No image available")
                
            st.markdown(f"**{product['title']}**")
            st.markdown(f"💴 ¥{product['price']}")
            
            if product.get("condition"):
                st.markdown(f"📦 Condition: {product['condition']}")
            
            rating = product.get("seller_rating")
            if rating is not None:
                st.markdown(f"⭐ Seller Rating: {int(rating)}")
                
            if product.get("seo_tags"):
                tags = product["seo_tags"]
                if isinstance(tags, list):
                    st.markdown("🏷️ " + ", ".join(tags))
                elif isinstance(tags, str):
                    st.markdown(f"🏷️ {tags}")
            
            st.link_button("View on Mercari", product["product_url"])
else:
    if not db_ready:
        st.warning("⚠️ Database is not connected. Connect your database to browse products.")
    elif search_term or tag_filter:
        st.info("No products found matching your criteria. Try adjusting the filters or search term.")
    else:
        st.info("Enter a search term or select tags to explore products.")
