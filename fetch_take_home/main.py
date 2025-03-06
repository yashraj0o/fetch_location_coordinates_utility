import argparse
import requests
import sys
import os
import re
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv('OPENWEATHER_API_KEY')  # Fetch API key from environment variable
BASE_URL = 'http://api.openweathermap.org/geo/1.0/'
COUNTRY_CODE = 'us'


def get_coordinates_by_name(location: str):
    """
    Get Coordinates by City, State
    """
    city_name, state_code = location.split(', ')
    url = f"{BASE_URL}direct?q={city_name},{state_code},{COUNTRY_CODE}&limit=1&appid={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {'location': location, 'error': f'API request failed with status code: {response.status_code}'}
        
        data = response.json()
    
        if data:
            return f"{data[0]['name']}, {data[0]['state']} lat:{data[0]['lat']}, lon:{data[0]['lon']}"
        else:
            return f"location: {location}, error: No data found for the location."
    
    except requests.exceptions.RequestException as e:
        return f"location: {location}, error: API request failed: {e}"


def get_coordinates_by_zipcode(zip_code: str):
    """
    Get Coordinates by Zip Code
    """
    url = f"{BASE_URL}zip?zip={zip_code},{COUNTRY_CODE}&appid={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {'location': zip_code, 'error': f'API request failed with status code: {response.status_code}'}
        data = response.json()

        if data:
            return f"{data['name']}, lat:{data['lat']}, lon:{data['lon']}"
        else:
            return f"location: {zip_code}, error: No data found for the location."
    
    except requests.exceptions.RequestException as e:
        return f"location: {zip_code}, error: API request failed: {e}"
    
def extract_input_locations(input_string: str):
    """
    Takes CLI input data and extracts city,state and zipcode format e.g. Madison, WI and 12345 to get coordinates.
    """
    city_state_pattern = r'[a-z\s]+,\s[a-z]{2}'
    zip_code_pattern = r'\b\d{5}\b'
    
        # Strip whitespace from each element in the lists
    city_state = [location.strip() for location in re.findall(city_state_pattern, input_string, re.IGNORECASE)]
    zip_code = [code.strip() for code in re.findall(zip_code_pattern, input_string)]
    
    return city_state, zip_code

def process_locations(locations):
    """
    Process a list of locations (city/state or zip) and print their coordinates.
    """
    results = []
    for loc in locations:
        city_states, zip_codes = extract_input_locations(loc)
        if city_states:
            for city_state in city_states:
                results.append(get_coordinates_by_name(city_state))
        elif zip_codes:
            for zip_code in zip_codes:
                results.append(get_coordinates_by_zipcode(zip_code))
        else:
            results.append(f"location: {loc}, error: Invalid location format or Invalid Characters.")
    return results


def main():
    parser = argparse.ArgumentParser(description="Get geolocation coordinates for US cities or zip codes.")
    parser.add_argument('locations', nargs='+', help="List of locations (e.g., 'Madison, WI' '12345')")
    args = parser.parse_args()
    
    if not API_KEY:
        print("Error: OPENWEATHER_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        results = process_locations(args.locations)
        for res in results:
            print(res)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()