# surfe-diem API

A surf and weather forecasting data API built with FastAPI.

## 🚀 Overview

surfe-diem provides surf spot, buoy, tide, and weather data via a modern REST API. Designed for surf forecasting apps, dashboards, and enthusiasts.

## 📁 Project Structure

- `app/` - Main application code (models, routers, classes, etc.)
- `tests/` - Unit and integration tests
- `jobs/` - Shell scripts for setup and maintenance
- `data/` - Static data files (JSON, etc.)
- `tools/` - Utility scripts

## 🏁 Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/crubio/surfe-diem-api.git
cd surfe-diem-api
```

### 2. Install dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Set up your `.env` file
(see Environment Variables section below for details)

### 4. Run the API
```bash
uvicorn app.main:app --host=0.0.0.0 --port=5000 --reload
```

### 5. API Docs
Visit [http://127.0.0.1:5000/api/v1](http://127.0.0.1:5000/api/v1) for interactive docs.

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /api/v1/spots` - Get surf spots
- `GET /api/v1/locations` - Get buoy locations
- `GET /api/v1/forecast` - Get weather forecast
- `GET /api/v1/weather` - Get current weather
- `GET /api/v1/tides/find_closest` - Find nearest tide station

### Batch Forecast Endpoint
- `POST /api/v1/batch-forecast` - Batch forecast for multiple locations

The batch forecast endpoint is designed for efficiency - instead of making multiple API calls from your frontend, send a list of buoy IDs and spot IDs in a single request and get current forecast data for all of them.

**Request:**
```json
{
  "buoy_ids": ["46042", "46232"],
  "spot_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "buoys": [
    {
      "id": "46042",
      "name": "Monterey Bay Buoy",
      "description": "NOAA Buoy",
      "location": "Monterey Bay, CA",
      "url": "https://www.ndbc.noaa.gov/station_page.php?station=46042",
      "latest_observation": {...},
      "weather_forecast": {...}
    }
  ],
  "spots": [
    {
      "id": 1,
      "name": "Steamer Lane",
      "timezone": "America/Los_Angeles",
      "latitude": 36.9519,
      "longitude": -122.0308,
      "subregion_name": "Santa Cruz",
      "weather_forecast": {...},
      "current_weather": {...}
    }
  ],
  "errors": [
    {
      "id": "invalid_id",
      "type": "buoy",
      "error": "Buoy location not found or inactive"
    }
  ]
}
```

## ⚙️ Environment Variables

| Variable                     | Description                        | Example                        |
|------------------------------|------------------------------------|--------------------------------|
| DATABASE_HOSTNAME            | Postgres host                      | localhost                      |
| DATABASE_PORT                | Postgres port                      | 5432                           |
| DATABASE_PASSWORD            | Postgres password                   | yourpassword                   |
| DATABASE_NAME                | Postgres DB name                    | surfe_diem_api                 |
| DATABASE_USERNAME            | Postgres user                       | postgres                       |
| SECRET_KEY                   | JWT secret key                      | (generate your own)            |
| ALGORITHM                    | JWT algorithm                       | HS256                          |
| ACCESS_TOKEN_EXPIRE_MINUTES  | JWT expiry in minutes               | 60                             |
| SQLITE_URI                   | SQLite DB URI                       | sqlite:///./surfe-diem-api.db  |
| DATABASE_URL                 | Alternative DB URL                  | postgresql://user:pass@host/db |
| DATABASE_URI                 | Alternative DB URI                  | postgresql://user:pass@host/db |
| SQLITE_DB                    | SQLite database file path           | ./surfe-diem-api.db            |
| ENVIRONMENT                  | Environment name                    | development                    |

## 🗄️ Database Setup

### PostgreSQL
Create a database in PostgreSQL, then create a `.env` file with:
```bash
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=password_that_you_set
DATABASE_NAME=name_of_database
DATABASE_USERNAME=User_name
SECRET_KEY=1234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### SQLite (Recommended for Development)
Create a `.env` file with:
```bash
SECRET_KEY=1234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./surfe-diem-api.db
DATABASE_URI=sqlite:///./surfe-diem-api.db
SQLITE_URI=sqlite:///./surfe-diem-api.db
SQLITE_DB=./surfe-diem-api.db
ENVIRONMENT=development
```

## 🚀 Deployment

### Render (Production)
The API is deployed on Render with automatic deployments from GitHub:
1. Push changes to the main branch
2. Render automatically deploys the updated code
3. The API runs on port 5000 as configured in the Procfile

### Docker

#### Using Docker Compose
```bash
docker-compose up -d
```

This will start PostgreSQL and the API in containers.

#### Building the Docker Image
```bash
docker build -t surfe-diem-api .
docker run -p 5000:8000 surfe-diem-api
```

## 🧪 Testing

### Dependencies
The testing setup requires these additional packages (already in requirements.txt):
- `pytest` - Testing framework
- `httpx` - HTTP client for testing
- `pytest-asyncio` - Async test support

### Test Structure
- `tests/test_basic.py` - Unit tests for core classes
- `tests/test_integration.py` - Integration tests for API endpoints

### Running Tests
```bash
# Run all tests
python3 -m pytest

# Run specific test file
python3 -m pytest tests/test_integration.py

# Run tests with verbose output
python3 -m pytest -v

# Run tests matching a pattern
python3 -m pytest -k "batch_forecast"
```

### Writing New Tests
1. **Unit Tests**: Test individual functions/classes in isolation
2. **Integration Tests**: Test API endpoints with the full application stack

Example integration test:
```python
def test_batch_forecast_endpoint_empty_request(client):
    """Test the batch forecast endpoint with empty request."""
    response = client.post("/api/v1/batch-forecast", json={
        "buoy_ids": [],
        "spot_ids": []
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "buoys" in data
    assert "spots" in data
    assert "errors" in data
```

## 🛠️ Development

### Code Style
- Use type hints everywhere
- Follow PEP 8 guidelines
- Use dataclasses for data models
- Add docstrings to all functions

### Adding New Endpoints
1. Create a new router in `app/routers/`
2. Add Pydantic models for request/response validation
3. Include the router in `app/main.py`
4. Write integration tests
5. Update this README

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Database Backup
The production database is backed up as `surfe-diem-api.db.backup`. To update the production database:
1. Create a new backup of your local database
2. Commit the backup file to GitHub
3. Deploy the updated code to Render

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 🔧 Troubleshooting

### Common Issues

**Database Connection Errors**
- Check your `.env` file configuration
- Ensure the database is running
- Verify connection credentials

**Import Errors**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path and virtual environment

**Test Failures**
- Ensure the database is properly set up
- Check that external APIs are accessible
- Verify test data exists in the database

### Getting Help
- Check the API documentation at `/api/v1`
- Review the test files for usage examples
- Open an issue with detailed error information

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

Built with ❤️ for the surfing community 