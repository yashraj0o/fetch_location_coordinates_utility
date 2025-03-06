import pytest
import subprocess
import sys
import os
import requests_mock
from main import BASE_URL, get_coordinates_by_name, get_coordinates_by_zipcode, process_locations, extract_input_locations

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')

@pytest.fixture
def run_command():
    """Fixture for running CLI commands"""
    def _run_command(locations):
        command = ['python', script_path] + locations
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    return _run_command

@pytest.fixture
def test_data():
    """Fixture containing test data"""
    return {
        'valid_city_state': "Vancouver, WA",
        'valid_zip': "53703",
        'mixed_input': "Madison, WI 53703 Chicago, IL 60601",
        'invalid_input': "Invalid Input 123",
        'special_char_input': "!@#$%^&*()]{, ?/>"
    }

@pytest.fixture
def mock_city_response():
    """Fixture providing mock response for city/state API calls"""
    return [{
        "name": "Madison",
        "state": "Wisconsin",
        "lat": 43.0731,
        "lon": -89.4012,
        "country": "US"
    }]

@pytest.fixture
def mock_zip_response():
    """Fixture providing mock response for zip code API calls"""
    return {
        "name": "New York",
        "lat": 40.7128,
        "lon": -74.0060,
        "country": "US"
    }

class TestInputParsing:
    def test_01_extract_input_locations_city_state(self, test_data):
        city_state, zip_code = extract_input_locations(test_data['valid_city_state'])
        assert city_state == ["Vancouver, WA"], "City, state should be extracted correctly"
        assert zip_code == [], "Zip code should be empty"

    def test_02_extract_input_locations_zip(self, test_data):
        city_state, zip_code = extract_input_locations(test_data['valid_zip'])
        assert city_state == [], "City, state should be empty"
        assert zip_code == ["53703"], "Zip code should be extracted correctly"

    def test_03_extract_input_locations_mixed(self, test_data):
        city_state, zip_code = extract_input_locations(test_data['mixed_input'])
        assert set(city_state) == {"Madison, WI", "Chicago, IL"}, "City, state should be extracted correctly"
        assert set(zip_code) == {"53703", "60601"}, "Zip code should be extracted correctly"

    def test_04_extract_input_locations_special_chars(self, test_data):
        city_state, zip_code = extract_input_locations(test_data['special_char_input'])
        assert city_state == [], "City, state should be empty"
        assert zip_code == [], "Zip code should be empty"

class TestProcessingWithMocks:
    def test_01_process_locations(self, mocker):
        mock_city = mocker.patch('main.get_coordinates_by_name', 
                               return_value="Madison, Wisconsin lat:43.0731, lon:-89.4012")
        mock_zip = mocker.patch('main.get_coordinates_by_zipcode', 
                              return_value="New York, lat:40.7128, lon:-74.0060")
        
        results = process_locations(["Madison, WI", "10001"])
        assert len(results) == 2, "Should return exactly 2 results"
        assert "Madison" in results[0], "First result should contain Madison"
        assert "New York" in results[1], "Second result should contain New York"
        mock_city.assert_called_once()
        mock_zip.assert_called_once()

    def test_02_process_invalid_location(self, mocker):
        mock_city = mocker.patch('main.get_coordinates_by_name')
        mock_zip = mocker.patch('main.get_coordinates_by_zipcode')
        results = process_locations(["Invalid@123"])
        assert "Invalid location format" in results[0], "Should return error message for invalid location"
        mock_city.assert_not_called()
        mock_zip.assert_not_called()

    def test_03_get_coordinates_by_name_success(self, mock_city_response):
        """Test successful city/state coordinate lookup"""
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, json=mock_city_response)
            result = get_coordinates_by_name("Madison, WI")
            assert "Madison" in result, "Response should contain city name 'Madison'"
            assert "lat:43.0731" in result, "Response should contain correct latitude"
            assert "lon:-89.4012" in result, "Response should contain correct longitude"

    def test_04_get_coordinates_by_name_failure(self):
        """Test failed city/state coordinate lookup"""
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, status_code=404)
            result = get_coordinates_by_name("Invalid, XX")
            assert "error" in result, "Response should contain error message"
            assert "404" in result['error'], "Response should contain 404 status code"

    def test_05_get_coordinates_by_zipcode_success(self, mock_zip_response):
        """Test successful zip code coordinate lookup"""
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, json=mock_zip_response)
            result = get_coordinates_by_zipcode("10001")
            assert "New York" in result, "Response should contain city name 'New York'"
            assert "lat:40.7128" in result, "Response should contain correct latitude"
            assert "lon:-74.006" in result, "Response should contain correct longitude"

    def test_05_get_coordinates_by_zipcode_failure(self):
        """Test failed zip code coordinate lookup"""
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, status_code=404)
            result = get_coordinates_by_zipcode("00000")
            assert "error" in result, "Response should contain error message"
            assert "404" in result['error'], "Response should contain 404 status code"

    def test_06_api_key_environment_variable(self):
        """Test API key environment variable is set"""
        assert 'OPENWEATHER_API_KEY' in os.environ, "OPENWEATHER_API_KEY should be set in environment variables"
        assert os.environ['OPENWEATHER_API_KEY'] is not None, "OPENWEATHER_API_KEY should not be None"

    def test_07_process_multiple_locations(self):
        """Test processing multiple valid locations"""
        locations = ["Seattle, WA", "10001"]
        with requests_mock.Mocker() as m:
            # Match city API endpoint specifically
            m.get(f"{BASE_URL}direct", json=[{
                "name": "Seattle",
                "state": "Washington",
                "lat": 47.6062,
                "lon": -122.3321
            }])
            
            # Match zip API endpoint specifically
            m.get(f"{BASE_URL}zip", json={
                "name": "New York",
                "lat": 40.7128,
                "lon": -74.0060
            })
            
            results = process_locations(locations)
            
            assert len(results) == 2, "Should return exactly 2 results"
            assert "Seattle" in results[0], "First result should contain Seattle data"
            assert "New York" in results[1], "Second result should contain New York data"

    def test_08_process_mixed_valid_invalid(self):
        """Test processing mixture of valid and invalid locations"""
        locations = ["Seattle, WA", "InvalidCity, XX", "99999"]
        with requests_mock.Mocker() as m:
            # Set up responses for city endpoint (direct)
            m.get(
                f"{BASE_URL}direct",
                [
                    {
                        # First city request (Seattle, WA)
                        'json': [{
                            "name": "Seattle",
                            "state": "Washington",
                            "lat": 47.6062,
                            "lon": -122.3321
                        }],
                        'status_code': 200
                    },
                    {
                        # Second city request (InvalidCity, XX)
                        'status_code': 404
                    }
                ]
            )
            
            # Set up response for zip endpoint
            m.get(f"{BASE_URL}zip", status_code=404)
            
            results = process_locations(locations)
            assert len(results) == 3, "Should return 3 results (1 valid, 2 invalid)"
            assert "Seattle" in results[0], "First result should contain Seattle data"
            assert "error" in str(results[1]), "Second result should contain error for invalid zip"
            assert "error" in str(results[2]), "Third result should contain error for invalid city"

# CLI Tests
class TestCLI:
    """Test suite for CLI functionality"""
    
    def test_01_cli_no_arguments(self, run_command):
        """Test CLI behavior with no arguments"""
        stdout, stderr, code = run_command([])  # Use the fixture instead of direct subprocess.run
        assert code != 0, "Should fail when no arguments provided"
        assert 'usage:' in stderr, "Should show usage message in stderr"

    def test_02_cli_invalid_format(self, run_command):
        """Test CLI behavior with invalid input format"""
        stdout, stderr, code = run_command(["InvalidInput123"])
        assert code == 0, "Should not fail for invalid input"
        assert 'error' in stdout, "Should contain error message"
        assert 'Invalid location format' in stdout, "Should specify invalid format error"

    def test_03_cli_multiple_inputs(self, run_command):
        """Test CLI behavior with multiple valid inputs"""
        stdout, stderr, code = run_command(["Fullerton, CA", "53703"])
        assert code == 0, "Should succeed with valid inputs"
        assert len(stdout.split('\n')) == 2, "Should have exactly two results"
        assert stderr == "", "Should not have any errors"