import streamlit as st
from query import get_products_by_tags, search_products_by_title
from llm_agent import extract_search_intent, recommend_products, translate_text
import json
import os

st.set_page_config(layout="wide", page_title="🛒 Mercari Product Explorer")

st.sidebar.title("🔍 Filter Products")

tag_filter = st.sidebar.multiselect("SEO Tags", ["apple", "android", "smartphone", "gaming", "bag", "audio"])
min_price, max_price = st.sidebar.slider("Price Range", 0, 50000, (0, 20000))
min_rating = st.sidebar.slider("Min Seller Rating", 0.0, 5.0, 0.0, 0.1)

# Add a search bar at the top of the main page
search_term = st.text_input("🔎 Search for products", "")

# AI Assistant toggle
use_ai = st.checkbox("🤖 AI Assistant (LLM-powered search & recommendations)")

# LLM provider selection (only visible if AI Assistant is enabled)
if use_ai:
    provider = st.sidebar.radio(
        "LLM Provider",
        ["openai", "openrouter"],
        format_func=lambda x: "OpenAI" if x == "openai" else "OpenRouter",
        index=0
    )
else:
    provider = None

st.title("🛍️ Mercari Product Explorer")

products = []
recommendations = []
llm_reasoning = None

if use_ai and search_term:
    with st.spinner("AI is understanding your request and searching..."):
        try:
            intent_json = extract_search_intent(search_term, provider=provider)
            intent = json.loads(intent_json)
            # Priority: tags > keywords
            if intent.get("tags"):
                products = get_products_by_tags(intent["tags"], limit=30)
            elif intent.get("keywords"):
                kw = " ".join(intent["keywords"])
                products = search_products_by_title(kw, limit=30)
            else:
                products = search_products_by_title("", limit=30)
            if intent.get("min_price") or intent.get("max_price"):
                min_p = intent.get("min_price", 0)
                max_p = intent.get("max_price", 1e9)
                products = [p for p in products if min_p <= p["price"] <= max_p]
            if products:
                rec_json = recommend_products(products[:10], search_term, provider=provider)
                try:
                    recommendations = json.loads(rec_json)
                    if isinstance(recommendations, dict):
                        # If the LLM returns a dict with a 'recommendations' key, extract the list
                        if 'recommendations' in recommendations and isinstance(recommendations['recommendations'], list):
                            recommendations = recommendations['recommendations']
                        else:
                            # If dict but no 'recommendations' key, wrap in a list
                            recommendations = [recommendations]
                    elif not isinstance(recommendations, list):
                        # If not a list, wrap in a list
                        recommendations = [recommendations]
                except Exception as e:
                    st.warning(f"Failed to parse recommendations: {e}\nRaw: {rec_json}")
                    recommendations = []
        except Exception as e:
            st.error(f"AI Assistant error: {e}")
else:
    # Classic search logic
    if search_term:
        products = search_products_by_title(search_term)
    elif tag_filter:
        products = get_products_by_tags(tag_filter)
    else:
        products = search_products_by_title("")

# Show recommendations if AI Assistant is enabled
if use_ai and recommendations:
    st.subheader("🤖 Top 3 AI Recommendations")
    for rec in recommendations:
        if isinstance(rec, dict):
            st.markdown(f"**{rec['title']}**  ")
            st.markdown(f"💴 ¥{rec['price']}")
            st.markdown(f"📝 {rec['reason']}")
            st.link_button("View on Mercari", rec["url"])
            st.markdown("---")
        else:
            st.warning(f"Unexpected recommendation format: {rec}")
    st.subheader("Other Matching Products")

# Show product cards
cols = st.columns(3)
for idx, product in enumerate(products):
    with cols[idx % 3]:
        st.image(product["image_url"], width=180)
        st.markdown(f"**{product['title']}**")
        st.markdown(f"💴 ¥{product['price']}")
        if product.get("condition"):
            st.markdown(f"📦 Condition: {product['condition']}")
        if product.get("seo_tags"):
            st.markdown("🏷️ Tags: " + ", ".join(product["seo_tags"]))
        st.link_button("View on Mercari", product["product_url"])