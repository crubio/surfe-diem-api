import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app import models, schemas

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    with patch('app.routers.batch.get_db') as mock_get_db:
        mock_session = MagicMock(spec=Session)
        mock_get_db.return_value = mock_session
        yield mock_session

@pytest.fixture
def sample_buoy_locations():
    """Sample buoy location data for testing."""
    return [
        models.BuoyLocation(
            id=1,
            location_id="46276",
            name="Santa Barbara Buoy",
            url="https://example.com/46276",
            description="Santa Barbara Channel",
            location="34.5 N 120.5 W",
            active=True,
            weight=1
        ),
        models.BuoyLocation(
            id=2,
            location_id="46268",
            name="San Pedro Buoy",
            url="https://example.com/46268", 
            description="San Pedro Channel",
            location="33.5 N 118.5 W",
            active=True,
            weight=1
        )
    ]

@pytest.fixture
def sample_spot_locations():
    """Sample spot location data for testing."""
    return [
        models.SpotLocation(
            id=1,
            name="Rincon",
            timezone="America/Los_Angeles",
            latitude="34.38",
            longitude="-119.48",
            subregion_name="Southern California"
        ),
        models.SpotLocation(
            id=3,
            name="Malibu",
            timezone="America/Los_Angeles", 
            latitude="34.04",
            longitude="-118.68",
            subregion_name="Southern California"
        )
    ]

@pytest.fixture
def mock_weather_data():
    """Mock weather API response data."""
    return {
        "current": {
            "wind_speed_10m": 15.5,
            "wind_direction_10m": 180
        },
        "hourly": {
            "wave_height": [3.2, 3.5, 3.8],
            "wave_direction": [245, 250, 255],
            "wave_period": [12, 13, 14]
        }
    }

@pytest.fixture
def mock_current_weather_data():
    """Mock current weather API response data."""
    return {
        "currentobservation": {
            "Temp": "68",
            "Weather": "Partly Cloudy"
        }
    }

@pytest.fixture
def mock_buoy_observation_data():
    """Mock buoy observation data."""
    return [
        {'wave_height': '2.3 ft', 'peak_period': '13 sec', 'air_temp': '61.2 °F', 'water_temp': '63.5 °F'},
        {'swell_height': '1.0 ft', 'period': '13.3 sec', 'direction': 'SW'},
        {'wind_wave_height': '2.0 ft', 'period': '3.1 sec', 'direction': 'W'}
    ]

class TestBatchForecastEndpoint:
    """Test suite for the batch forecast endpoint."""
    
    def test_batch_forecast_success_buoys_only(self, mock_db_session, sample_buoy_locations, 
                                             mock_weather_data, mock_buoy_observation_data):
        """Test successful batch forecast with buoys only."""
        # Mock database query
        mock_db_session.query.return_value.filter.return_value.all.return_value = sample_buoy_locations
        
        # Mock external API calls
        with patch('app.routers.batch.get_latest_observation_async', new_callable=AsyncMock) as mock_obs, \
             patch('app.routers.batch.get_weather_forecast_async', new_callable=AsyncMock) as mock_weather:
            
            mock_obs.return_value = mock_buoy_observation_data
            mock_weather.return_value = mock_weather_data
            
            # Make request
            response = client.post(
                "/api/v1/batch-forecast",
                json={"buoy_ids": ["46276", "46268"], "spot_ids": []}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "buoys" in data
            assert "spots" in data
            assert "errors" in data
            assert len(data["buoys"]) == 2
            assert len(data["spots"]) == 0
            assert len(data["errors"]) == 0
            
            # Check buoy data structure
            buoy = data["buoys"][0]
            assert "id" in buoy
            assert "name" in buoy
            assert "observation" in buoy
            assert "weather" in buoy
            
            # Check weather data structure
            weather = buoy["weather"]
            assert "swell" in weather
            assert "wind" in weather
            assert weather["swell"]["height"] == 3.2
            assert weather["wind"]["speed"] == 15.5
    
    def test_batch_forecast_success_spots_only(self, mock_db_session, sample_spot_locations,
                                             mock_weather_data, mock_current_weather_data):
        """Test successful batch forecast with spots only."""
        # Mock database query
        mock_db_session.query.return_value.filter.return_value.all.return_value = sample_spot_locations
        
        # Mock external API calls
        with patch('app.routers.batch.get_weather_forecast_async', new_callable=AsyncMock) as mock_weather, \
             patch('app.routers.batch.get_current_weather_async', new_callable=AsyncMock) as mock_current:
            
            mock_weather.return_value = mock_weather_data
            mock_current.return_value = mock_current_weather_data
            
            # Make request
            response = client.post(
                "/api/v1/batch-forecast",
                json={"buoy_ids": [], "spot_ids": [1, 3]}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert len(data["buoys"]) == 0
            assert len(data["spots"]) == 2
            assert len(data["errors"]) == 0
            
            # Check spot data structure
            spot = data["spots"][0]
            assert "id" in spot
            assert "name" in spot
            assert "weather" in spot
            
            # Check weather data structure
            weather = spot["weather"]
            assert "swell" in weather
            assert "wind" in weather
            assert "current" in weather
            assert weather["current"]["temperature"] == "68"
    
    def test_batch_forecast_mixed_request(self, mock_db_session, sample_buoy_locations, 
                                        sample_spot_locations, mock_weather_data, 
                                        mock_current_weather_data, mock_buoy_observation_data):
        """Test successful batch forecast with both buoys and spots."""
        # Mock database queries - need to handle both buoy and spot queries
        def mock_query_side_effect():
            mock_query = MagicMock()
            mock_query.filter.return_value.all.side_effect = [
                sample_buoy_locations,  # First call for buoys
                sample_spot_locations   # Second call for spots
            ]
            return mock_query
        
        mock_db_session.query.side_effect = mock_query_side_effect
        
        # Mock external API calls
        with patch('app.routers.batch.get_latest_observation_async', new_callable=AsyncMock) as mock_obs, \
             patch('app.routers.batch.get_weather_forecast_async', new_callable=AsyncMock) as mock_weather, \
             patch('app.routers.batch.get_current_weather_async', new_callable=AsyncMock) as mock_current:
            
            mock_obs.return_value = mock_buoy_observation_data
            mock_weather.return_value = mock_weather_data
            mock_current.return_value = mock_current_weather_data
            
            # Make request
            response = client.post(
                "/api/v1/batch-forecast",
                json={"buoy_ids": ["46276"], "spot_ids": [1]}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert len(data["buoys"]) == 1
            assert len(data["spots"]) == 1
            assert len(data["errors"]) == 0
    
    def test_batch_forecast_missing_buoy(self, mock_db_session, sample_buoy_locations):
        """Test batch forecast with missing buoy ID."""
        # Mock database query - return only one buoy
        mock_db_session.query.return_value.filter.return_value.all.return_value = [sample_buoy_locations[0]]
        
        # Mock external API calls
        with patch('app.routers.batch.get_latest_observation_async', new_callable=AsyncMock) as mock_obs, \
             patch('app.routers.batch.get_weather_forecast_async', new_callable=AsyncMock) as mock_weather:
            
            mock_obs.return_value = []
            mock_weather.return_value = {}
            
            # Make request with one valid and one invalid buoy ID
            response = client.post(
                "/api/v1/batch-forecast",
                json={"buoy_ids": ["46276", "invalid_id"], "spot_ids": []}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should have one buoy and one error
            assert len(data["buoys"]) == 1
            assert len(data["errors"]) == 1
            assert data["errors"][0]["type"] == "buoy"
            assert data["errors"][0]["id"] == "invalid_id"
    
    def test_batch_forecast_api_failure(self, mock_db_session, sample_buoy_locations):
        """Test batch forecast when external API calls fail."""
        # Mock database query
        mock_db_session.query.return_value.filter.return_value.all.return_value = sample_buoy_locations
        
        # Mock external API calls to fail
        with patch('app.routers.batch.get_latest_observation_async', new_callable=AsyncMock) as mock_obs, \
             patch('app.routers.batch.get_weather_forecast_async', new_callable=AsyncMock) as mock_weather:
            
            mock_obs.side_effect = Exception("API Error")
            mock_weather.side_effect = Exception("API Error")
            
            # Make request
            response = client.post(
                "/api/v1/batch-forecast",
                json={"buoy_ids": ["46276"], "spot_ids": []}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should still return the buoy with None values for failed API calls
            assert len(data["buoys"]) == 1
            assert data["buoys"][0]["observation"] is None
            assert data["buoys"][0]["weather"]["swell"] is None
    
    def test_batch_forecast_empty_request(self):
        """Test batch forecast with empty request."""
        response = client.post(
            "/api/v1/batch-forecast",
            json={"buoy_ids": [], "spot_ids": []}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty arrays
        assert len(data["buoys"]) == 0
        assert len(data["spots"]) == 0
        assert len(data["errors"]) == 0
    
    def test_batch_forecast_invalid_request(self):
        """Test batch forecast with invalid request format."""
        response = client.post(
            "/api/v1/batch-forecast",
            json={"invalid_field": "value"}
        )
        
        # Should return 422 validation error
        assert response.status_code == 422

class TestCacheEndpoints:
    """Test suite for cache management endpoints."""
    
    def test_cache_status(self):
        """Test cache status endpoint."""
        response = client.get("/api/v1/cache/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "cache_size" in data
        assert "cache_keys" in data
        assert isinstance(data["cache_size"], int)
        assert isinstance(data["cache_keys"], list)
    
    def test_clear_cache(self):
        """Test clear cache endpoint."""
        response = client.post("/api/v1/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "message" in data
        assert data["message"] == "Cache cleared"

class TestWeatherDataExtraction:
    """Test suite for weather data extraction function."""
    
    def test_extract_essential_weather_valid_data(self, mock_weather_data, mock_current_weather_data):
        """Test extracting essential weather data with valid inputs."""
        from app.routers.batch import extract_essential_weather
        
        result = extract_essential_weather(mock_weather_data, mock_current_weather_data)
        
        # Check structure
        assert "swell" in result
        assert "wind" in result
        assert "current" in result
        
        # Check swell data
        assert result["swell"]["height"] == 3.2
        assert result["swell"]["direction"] == 245
        assert result["swell"]["period"] == 12
        
        # Check wind data
        assert result["wind"]["speed"] == 15.5
        assert result["wind"]["direction"] == 180
        
        # Check current data
        assert result["current"]["temperature"] == "68"
        assert result["current"]["conditions"] == "Partly Cloudy"
    
    def test_extract_essential_weather_none_data(self):
        """Test extracting essential weather data with None inputs."""
        from app.routers.batch import extract_essential_weather
        
        result = extract_essential_weather(None, None)
        
        # Should return structure with None values
        assert result["swell"] is None
        assert result["wind"] is None
        assert result["current"] is None
    
    def test_extract_essential_weather_partial_data(self, mock_weather_data):
        """Test extracting essential weather data with partial data."""
        from app.routers.batch import extract_essential_weather
        
        result = extract_essential_weather(mock_weather_data, None)
        
        # Should have swell and wind data but no current data
        assert result["swell"] is not None
        assert result["wind"] is not None
        assert result["current"] is None 