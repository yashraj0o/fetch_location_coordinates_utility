import pytest
import os

@pytest.fixture(autouse=True)
def mock_env_api_key():
    """Automatically set test API key for all tests"""
    os.environ['OPENWEATHER_API_KEY'] = 'test_api_key'

@pytest.fixture
def mock_city_response():
    return [{
        "name": "Madison",
        "state": "Wisconsin",
        "lat": 43.0731,
        "lon": -89.4012
    }]

@pytest.fixture
def mock_zip_response():
    return {
        "name": "New York",
        "lat": 40.7128,
        "lon": -74.0060
    }
