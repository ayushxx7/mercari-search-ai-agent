import os
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env if it exists
load_dotenv()

# Helper to get secret from Streamlit or Environment
def get_secret(key, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)

# Groq and OpenRouter keys
GROQ_API_KEY = get_secret("GROQ_API_KEY")
OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = get_secret("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Helper to get client for either Groq or OpenRouter
def get_client(provider):
    if provider == "groq":
        return OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
    elif provider == "openrouter":
        return OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
    return None

# Helper to get model name for each provider
def get_model_name(provider):
    if provider == "groq":
        return "llama-3.3-70b-versatile"
    if provider == "openrouter":
        return "deepseek/deepseek-chat"
    return None

# Fallback logic: try Groq, then OpenRouter
def call_with_fallback(fn, *args, provider=None, **kwargs):
    providers = ["groq", "openrouter"]
    
    last_exc = None
    for prov in providers:
        if prov == "groq" and not GROQ_API_KEY:
            continue
        if prov == "openrouter" and not OPENROUTER_API_KEY:
            continue
            
        try:
            return fn(*args, provider=prov, **kwargs)
        except Exception as e:
            last_exc = e
            print(f"LLM Provider {prov} failed: {e}")
            continue
    
    if last_exc:
        raise last_exc
    raise Exception("No LLM provider available. Please check your .env or st.secrets for GROQ_API_KEY or OPENROUTER_API_KEY.")

# Translate text using LLM
def translate_text(text, dest_lang, provider=None):
    def _translate(text, dest_lang, provider):
        client = get_client(provider)
        model = get_model_name(provider)
        prompt = f"Translate the following text to {'Japanese' if dest_lang == 'ja' else 'English'}:\n{text}"
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=256,
        )
        return response.choices[0].message.content.strip()
    return call_with_fallback(_translate, text, dest_lang, provider=provider)

# Use LLM to extract search intent and filters
def extract_search_intent(user_query, language="en", provider=None):
    def _extract(user_query, language, provider):
        client = get_client(provider)
        model = get_model_name(provider)
        system_prompt = (
            "You are a shopping assistant for Mercari Japan. "
            "Given a user's request, extract search filters as JSON. "
            "IMPORTANT: Mercari Japan titles are mostly in Japanese. "
            "If the user query is in English, you MUST include both English and translated Japanese keywords in the 'keywords' list to ensure high recall. "
            "For example, if the user asks for 'backpack', include ['backpack', 'リュック', 'バックパック'].\n\n"
            "Return JSON with:\n"
            "- keywords (list of strings)\n"
            "- category (string, optional)\n"
            "- min_price (float, optional)\n"
            "- max_price (float, optional)\n"
            "- tags (list of strings, optional)\n"
            "IMPORTANT: Return ONLY valid JSON."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=512,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    return call_with_fallback(_extract, user_query, language, provider=provider)

# Use LLM to generate reasoned recommendations
def recommend_products(products, user_query, language="en", provider=None):
    def _recommend(products, user_query, language, provider):
        client = get_client(provider)
        model = get_model_name(provider)
        system_prompt = (
            "You are a highly skilled shopping assistant for Mercari Japan. "
            "Given a user's request and a list of products (as JSON), "
            "select the top 3 products that best match the user's needs. "
            "For each recommendation, provide a concise reason in the user's query language. "
            "Output as a JSON object with a 'recommendations' key containing a list of objects: "
            "{\"recommendations\": [{\"title\": \"...\", \"price\": 123, \"reason\": \"...\", \"url\": \"...\", \"reason\": \"...\", \"url\": \"...\", \"image_url\": \"...\"}]} "
            "Return only the JSON object, no extra text."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User request: {user_query}\nProducts: {products}"}
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    return call_with_fallback(_recommend, products, user_query, language, provider=provider)
