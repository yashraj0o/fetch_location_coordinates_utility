from main import get_coordinates_by_name, get_coordinates_by_zipcode
from dotenv import load_dotenv

# Ensure .env is loaded before tests run
load_dotenv()

class TestAPIIntegration:
    #Real API integration tests
    
    def test_01_valid_city_state_lookup(self):
        """Test retrieving coordinates for a valid city"""
        result = get_coordinates_by_name("Seattle, WA")
        assert result is not None, "Response should not be None"
        assert "Seattle" in result, "Response should contain city name"
        assert "Washington" in result, "Response should contain state name"
        assert "lat:47.6038321" in result, "Response should contain latitude"
        assert "lon:-122.330062" in result, "Response should contain longitude"

    def test_02_valid_zip_lookup(self):
        """Test retrieving coordinates for a valid zip code"""
        result = get_coordinates_by_zipcode("98101")  # Seattle zip code
        assert result is not None, "Response should not be None"
        assert "Seattle" in result, "Response should contain city name"
        assert "lat:47.6114" in result, "Response should contain latitude"
        assert "lat:47.6114" in result, "Response should contain longitude"

    def test_03_invalid_city_state(self):
        """Test behavior with invalid city/state"""
        result = get_coordinates_by_name("NotACity, XX")
        assert "error" in str(result), "Response should contain error message"

    def test_04_invalid_zip(self):
        """Test behavior with invalid zip code"""
        result = get_coordinates_by_zipcode("00000")
        assert "error" in str(result), "Response should contain error message"