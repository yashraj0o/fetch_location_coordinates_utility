# Geolocation Coordinates Utility

A command-line utility that fetches coordinates from the OpenWeather Geocoding API for US locations using either city/state combinations or ZIP codes.

## Features

- Fetch coordinates using city/state combination (e.g., "Seattle, WA")
- Fetch coordinates using ZIP code (e.g., "98101")
- Support for multiple locations in a single command
- Error handling for invalid inputs
- Environment-based configuration

## Requirements

- Python 3.x
- OpenWeather API key (free tier works)
- Required Python packages (see requirements.txt)

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root:
   ```bash
   cp .env.sample .env
   ```
4. Add your OpenWeather API key to the `.env` file:
   ```plaintext
   OPENWEATHER_API_KEY=your_api_key_here
   ```

## Usage

Run the script with one or more locations:

```bash
# Single location
python main.py "Seattle, WA"

# Multiple locations
python main.py "Seattle, WA" "98101" "Madison, WI"
```

### Input Formats
- City, State: Must be in format "City, ST" (e.g., "Seattle, WA")
- ZIP Code: Must be a 5-digit US ZIP code (e.g., "98101")

### Example Output
```
Seattle, Washington lat:47.6038321, lon:-122.330062
New York, lat:40.7128, lon:-74.0060
```

## Testing

The project includes both unit tests and integration tests:

```bash
# Run only unit tests
python -m pytest -vv unit_tests.py

# Run only integration tests
python -m pytest -vv integration_tests.py
```

Note: Integration tests require a valid API key in your `.env` file.

## Error Handling

The utility handles several error cases:
- Invalid API key
- Invalid location format
- Non-existent locations
- API request failures

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
