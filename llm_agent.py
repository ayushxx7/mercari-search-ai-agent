import os
from openai import OpenAI
import requests

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Helper to get OpenAI-compatible client for either provider
def get_client(provider):
    if provider == "openrouter":
        return OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
    # Default to OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)

# Helper to get model name for each provider
def get_model_name(provider):
    if provider == "openrouter":
        return "deepseek/deepseek-chat-v3-0324:free"
    return "gpt-4o-mini"

# Fallback logic: try primary, then secondary provider
def call_with_fallback(fn, *args, provider="openai", **kwargs):
    providers = [provider, "openrouter" if provider == "openai" else "openai"]
    last_exc = None
    for prov in providers:
        try:
            return fn(*args, provider=prov, **kwargs)
        except Exception as e:
            last_exc = e
            continue
    raise last_exc

# Translate text between English and Japanese using LLM
def translate_text(text, dest_lang, provider="openai"):
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

# Use LLM to extract search intent and filters from a user query
def extract_search_intent(user_query, language="en", provider="openai"):
    def _extract(user_query, language, provider):
        client = get_client(provider)
        model = get_model_name(provider)
        system_prompt = (
            "You are a shopping assistant for Mercari Japan. "
            "Given a user's request, extract the following as JSON: "
            "- keywords (list of strings)\n"
            "- category (string, optional)\n"
            "- min_price (float, optional)\n"
            "- max_price (float, optional)\n"
            "- tags (list of strings, optional)\n"
            "If the query is in Japanese, return keywords in Japanese. If in English, return in English. "
            "If the user specifies a language, respect it."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=256,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    return call_with_fallback(_extract, user_query, language, provider=provider)

# Use LLM to generate reasoned recommendations for top products
def recommend_products(products, user_query, language="en", provider="openai"):
    def _recommend(products, user_query, language, provider):
        client = get_client(provider)
        model = get_model_name(provider)
        system_prompt = (
            "You are a highly skilled shopping assistant for Mercari Japan. "
            "Given a user's request (which may be in English, Japanese, or a mix) and a list of products (as JSON), "
            "select the top 3 products that best match the user's needs. "
            "Consider product titles, tags, and descriptions in both English and Japanese, including transliterations and synonyms. "
            "If the user query is in English but products are in Japanese (or vice versa), use your knowledge to match them semantically. "
            "For each recommendation, provide a concise reason in the user's query language. "
            "Output as a JSON list: [{title, price, reason, url}]. "
            "Return only the JSON list, no extra text."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User request: {user_query}\nProducts: {products}"}
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=512,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    return call_with_fallback(_recommend, products, user_query, language, provider=provider)