import pytest
import json
from unittest.mock import MagicMock
from llm_agent import extract_search_intent, recommend_products

def test_extract_search_intent_format(monkeypatch):
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"keywords": ["iphone"], "max_price": 50000}'
    mock_client.chat.completions.create.return_value = mock_response
    
    # Mock get_client to return our mock_client
    monkeypatch.setattr("llm_agent.get_client", lambda provider: mock_client)
    
    result_json = extract_search_intent("iphone under 50000")
    result = json.loads(result_json)
    
    assert "keywords" in result
    assert result["keywords"] == ["iphone"]
    assert result["max_price"] == 50000

def test_recommend_products_format(monkeypatch):
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"recommendations": [{"title": "Test Item", "price": 100, "reason": "Good price", "url": "http://test.com"}]}'
    mock_client.chat.completions.create.return_value = mock_response
    
    # Mock get_client to return our mock_client
    monkeypatch.setattr("llm_agent.get_client", lambda provider: mock_client)
    
    products = [{"title": "Test Item", "price": 100, "product_url": "http://test.com"}]
    result_json = recommend_products(products, "cheap item")
    result = json.loads(result_json)
    
    assert "recommendations" in result
    assert len(result["recommendations"]) == 1
    assert result["recommendations"][0]["title"] == "Test Item"
