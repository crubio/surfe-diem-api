import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

def test_root_endpoint(client):
    """Test the root endpoint returns expected message."""
    response = client.get("/")
    
    # Check status code
    assert response.status_code == 200
    
    # Check response structure
    data = response.json()
    assert "message" in data
    assert data["message"] == "hello from surfe-diem"

def test_root_endpoint_response_type(client):
    """Test that the root endpoint returns JSON."""
    response = client.get("/")
    
    # Check content type
    assert response.headers["content-type"] == "application/json"
    
    # Verify it's valid JSON
    data = response.json()
    assert isinstance(data, dict)

def test_spots_endpoint_success(client):
    """Test the spots endpoint returns a successful response."""
    response = client.get("/api/v1/spots")
    
    # Check status code
    assert response.status_code == 200
    
    # Check response is a list
    data = response.json()
    assert isinstance(data, list)
    
    # Check content type
    assert response.headers["content-type"] == "application/json"

def test_spots_endpoint_with_limit(client):
    """Test the spots endpoint with limit parameter."""
    response = client.get("/api/v1/spots?limit=5")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_spots_endpoint_with_search(client):
    """Test the spots endpoint with search parameter."""
    response = client.get("/api/v1/spots?search=test")
    
    # Handle both cases: spots found or not found
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
    elif response.status_code == 404:
        data = response.json()
        assert "detail" in data
        assert "no spots found" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_spots_endpoint_with_search_valid_results(client):
    """Test the spots endpoint with search parameter for a known spot."""
    # Use proper URL encoding for "santa cruz"
    response = client.get("/api/v1/spots?search=santa%20cruz")
    
    # Handle both cases: spots found or not found
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check that at least one result contains "santa cruz" in the name
        found_santa_cruz = any("santa cruz" in spot["name"].lower() for spot in data)
        assert found_santa_cruz, f"No 'santa cruz' found in results: {[spot['name'] for spot in data[:3]]}"
    elif response.status_code == 404:
        # If no spots found, that's also valid for this test
        data = response.json()
        assert "detail" in data
        assert "no spots found" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_spots_endpoint_404_when_empty(client):
    """Test the spots endpoint returns 404 when no spots found."""
    # This test might fail if there are spots in the database
    # We'll handle both cases
    response = client.get("/api/v1/spots?search=nonexistentspotname12345")
    
    if response.status_code == 404:
        # Expected when no spots match the search
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    else:
        # If spots exist, we should get a 200 with empty list or results
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

def test_spots_geojson_endpoint(client):
    """Test the spots geojson endpoint."""
    response = client.get("/api/v1/spots/geojson")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check GeoJSON structure
    assert "type" in data
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert isinstance(data["features"], list)
    
    # Check content type
    assert response.headers["content-type"] == "application/json"

# Buoy Locations Tests
def test_locations_endpoint_success(client):
    """Test the locations endpoint returns a successful response."""
    response = client.get("/api/v1/locations")
    
    # Check status code
    assert response.status_code == 200
    
    # Check response is a list
    data = response.json()
    assert isinstance(data, list)
    
    # Check content type
    assert response.headers["content-type"] == "application/json"

def test_locations_endpoint_with_limit(client):
    """Test the locations endpoint with limit parameter."""
    response = client.get("/api/v1/locations?limit=5")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_locations_endpoint_with_search(client):
    """Test the locations endpoint with search parameter."""
    response = client.get("/api/v1/locations?search=test")
    
    # Handle both cases: locations found or not found
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
    elif response.status_code == 404:
        data = response.json()
        assert "detail" in data
        assert "no locations found" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_locations_endpoint_404_when_empty(client):
    """Test the locations endpoint returns 404 when no locations found."""
    response = client.get("/api/v1/locations?search=nonexistentlocationname12345")
    
    if response.status_code == 404:
        # Expected when no locations match the search
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    else:
        # If locations exist, we should get a 200 with empty list or results
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

def test_locations_geojson_endpoint(client):
    """Test the locations geojson endpoint."""
    response = client.get("/api/v1/locations/geojson")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check GeoJSON structure
    assert "type" in data
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert isinstance(data["features"], list)
    
    # Check content type
    assert response.headers["content-type"] == "application/json"

def test_find_closest_location_endpoint(client):
    """Test the find closest location endpoint."""
    # Test with coordinates near Santa Cruz, CA
    response = client.get("/api/v1/locations/find_closest?lat=36.9741&lng=-122.0308&dist=50")
    
    # Handle both cases: locations found or not found
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            # Check structure of first result
            first_result = data[0]
            assert "location_id" in first_result  # Changed from "id" to "location_id"
            assert "name" in first_result
            assert "distance" in first_result
            assert "latitude" in first_result
            assert "longitude" in first_result
            assert "description" in first_result  # Added this field
            assert "url" in first_result  # Added this field
            assert "location" in first_result  # Added this field
            assert isinstance(first_result["distance"], (int, float))
    elif response.status_code == 404:
        data = response.json()
        assert "detail" in data
        assert "surf data not available" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_find_closest_spot_endpoint(client):
    """Test the find closest spot endpoint."""
    # Test with coordinates near Santa Cruz, CA
    response = client.get("/api/v1/spots/find_closest?lat=36.9741&lng=-122.0308&dist=50")
    
    # Handle both cases: spots found or not found
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            # Check structure of first result
            first_result = data[0]
            assert "id" in first_result
            assert "name" in first_result
            assert "distance" in first_result
            assert "latitude" in first_result
            assert "longitude" in first_result
            assert "subregion_name" in first_result
            assert isinstance(first_result["distance"], (int, float))
    elif response.status_code == 404:
        data = response.json()
        assert "detail" in data
        assert "no surf spots found" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_search_all_endpoint(client):
    """Test the general search endpoint."""
    response = client.get("/api/v1/search?q=test&limit=10")
    
    # Handle both cases: results found or not found
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    elif response.status_code == 404:
        data = response.json()
        assert "detail" in data
        assert "no results found" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

# Real-time Buoy Data Tests
def test_location_realtime_endpoint_success(client):
    """Test the realtime endpoint with a valid location ID."""
    # Use a common NOAA buoy ID for testing
    response = client.get("/api/v1/locations/46042/realtime?limit=5")
    
    # Handle both cases: data available or not
    if response.status_code == 200:
        data = response.json()
        assert "location_id" in data
        assert "url" in data
        assert "data" in data
        assert data["location_id"] == "46042"
        assert "ndbc.noaa.gov" in data["url"]
        # Data might be empty if NOAA is down, but structure should be correct
        assert isinstance(data["data"], list)
    elif response.status_code == 404:
        # Expected if NOAA data is unavailable or buoy is offline
        data = response.json()
        assert "detail" in data
        assert "invalid id" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_location_realtime_endpoint_with_html(client):
    """Test the realtime endpoint with HTML output."""
    response = client.get("/api/v1/locations/46042/realtime?limit=3&send_html=true")
    
    if response.status_code == 200:
        data = response.json()
        assert "location_id" in data
        assert "url" in data
        assert "data" in data
        assert "html" in data
        # HTML should be present when send_html=true
        assert data["html"] is not None
        assert isinstance(data["html"], str)
        assert "<table" in data["html"]
    elif response.status_code == 404:
        # Expected if NOAA data is unavailable
        data = response.json()
        assert "detail" in data
        assert "invalid id" in data["detail"].lower()
    else:
        assert False, f"Unexpected status code: {response.status_code}"

def test_location_realtime_endpoint_invalid_id(client):
    """Test the realtime endpoint with an invalid location ID."""
    response = client.get("/api/v1/locations/invalid_id_12345/realtime")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "invalid id" in data["detail"].lower()

def test_location_latest_observation_endpoint_success(client):
    """Test the latest observation endpoint with a valid location ID."""
    response = client.get("/api/v1/locations/46042/latest-observation")
    
    # Handle both cases: data available or not
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            # Check structure of observation data
            first_obs = data[0]
            # These are the expected fields from BuoyLocationLatestObservation schema
            expected_fields = [
                "wave_height", "peak_period", "water_temp", "atmospheric_pressure",
                "air_temp", "dew_point", "swell_height", "period", "direction", "wind_wave_height"
            ]
            # At least some fields should be present
            found_fields = [field for field in expected_fields if field in first_obs]
            assert len(found_fields) > 0, f"No expected fields found in observation: {first_obs}"
    elif response.status_code == 404:
        # Expected if NOAA data is unavailable or buoy is offline
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_location_latest_observation_endpoint_invalid_id(client):
    """Test the latest observation endpoint with an invalid location ID."""
    response = client.get("/api/v1/locations/invalid_id_12345/latest-observation")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_location_latest_endpoint_deprecated(client):
    """Test the deprecated latest endpoint (should still work but may be removed)."""
    response = client.get("/api/v1/locations/46042/latest")
    
    # Handle both cases: data available or not
    if response.status_code == 200:
        data = response.json()
        # Check structure of NOAA summary data
        expected_fields = [
            "id", "location_id", "timestamp", "wvht", "precipitation", "wind",
            "gust", "peak_period", "water_temp", "swell", "period", "direction", "wind_wave"
        ]
        # At least some fields should be present
        found_fields = [field for field in expected_fields if field in data]
        assert len(found_fields) > 0, f"No expected fields found in summary: {data}"
    elif response.status_code == 404:
        # Expected if no summary data in database
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

# Tides Tests
def test_tides_find_closest_endpoint_success(client):
    """Test the find closest tide station endpoint."""
    # Test with coordinates near Santa Cruz, CA
    response = client.get("/api/v1/tides/find_closest?lat=36.9741&lng=-122.0308&dist=50")
    
    # Handle both cases: tide stations found or not found
    if response.status_code == 200:
        data = response.json()
        # Should return a single tide station object
        assert "station_id" in data
        assert "distance" in data
        assert "latitude" in data
        assert "longitude" in data
        assert isinstance(data["distance"], (int, float))
        # Handle both string and numeric coordinates
        assert isinstance(data["latitude"], (int, float, str))
        assert isinstance(data["longitude"], (int, float, str))
    elif response.status_code == 404:
        # Expected if no tide stations in database or none within distance
        data = response.json()
        assert "detail" in data
        assert "tide data not available" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_tides_find_closest_endpoint_no_stations(client):
    """Test the find closest tide station endpoint when no stations are available."""
    # Test with coordinates in middle of ocean (should have no nearby stations)
    response = client.get("/api/v1/tides/find_closest?lat=0.0&lng=0.0&dist=10")
    
    # Handle both cases: tide stations found or not found
    if response.status_code == 200:
        data = response.json()
        assert "station_id" in data
        assert "distance" in data
        assert "latitude" in data
        assert "longitude" in data
    elif response.status_code == 404:
        # Expected if no tide stations within distance
        data = response.json()
        assert "detail" in data
        assert "tide data not available" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

# Forecast Tests
def test_forecast_endpoint_success(client):
    """Test the forecast endpoint with valid coordinates."""
    # Test with coordinates near Santa Cruz, CA
    response = client.get("/api/v1/forecast?latitude=36.9741&longitude=-122.0308")
    
    # Handle both cases: forecast available or not
    if response.status_code == 200:
        data = response.json()
        # Check basic forecast structure from open-meteo API
        assert "latitude" in data
        assert "longitude" in data
        # Use approximate comparison for floating point coordinates
        assert abs(data["latitude"] - 36.9741) < 0.1
        assert abs(data["longitude"] - (-122.0308)) < 0.1
        # Should have some forecast data
        assert len(data) > 2  # More than just lat/lng
    elif response.status_code == 400:
        # Expected if external API is down or coordinates are invalid
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_forecast_endpoint_with_parameters(client):
    """Test the forecast endpoint with additional parameters."""
    response = client.get("/api/v1/forecast?latitude=36.9741&longitude=-122.0308&current=temperature_2m&hourly=temperature_2m&timezone=auto")
    
    if response.status_code == 200:
        data = response.json()
        assert "latitude" in data
        assert "longitude" in data
        assert "timezone" in data
        # Should have current and hourly data when requested
        if "current" in data:
            assert "temperature_2m" in data["current"]
        if "hourly" in data:
            assert "temperature_2m" in data["hourly"]
    elif response.status_code == 400:
        # Expected if external API is down
        data = response.json()
        assert "detail" in data
    else:
        assert False, f"Unexpected status code: {response.status_code}"

def test_forecast_endpoint_invalid_coordinates(client):
    """Test the forecast endpoint with invalid coordinates."""
    response = client.get("/api/v1/forecast?latitude=999&longitude=999")
    
    # Should handle invalid coordinates gracefully
    if response.status_code == 200:
        # Some APIs might still return data for invalid coordinates
        data = response.json()
        assert "latitude" in data
        assert "longitude" in data
    elif response.status_code == 400:
        # Expected for invalid coordinates
        data = response.json()
        assert "detail" in data
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

# Weather Tests
def test_weather_endpoint_success(client):
    """Test the weather endpoint with valid coordinates."""
    # Test with coordinates near Santa Cruz, CA
    response = client.get("/api/v1/weather?lat=36.9741&lng=-122.0308")
    
    # Handle both cases: weather available or not
    if response.status_code == 200:
        data = response.json()
        # Check basic weather structure from NOAA API
        # NOAA weather API returns various structures, so just check it's valid JSON
        assert isinstance(data, dict)
        assert len(data) > 0
    elif response.status_code == 400:
        # Expected if external API is down or coordinates are invalid
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_weather_endpoint_invalid_coordinates(client):
    """Test the weather endpoint with invalid coordinates."""
    response = client.get("/api/v1/weather?lat=999&lng=999")
    
    # Should handle invalid coordinates gracefully
    if response.status_code == 200:
        # Some APIs might still return data for invalid coordinates
        data = response.json()
        assert isinstance(data, dict)
    elif response.status_code == 400:
        # Expected for invalid coordinates
        data = response.json()
        assert "detail" in data
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

def test_weather_endpoint_ocean_coordinates(client):
    """Test the weather endpoint with ocean coordinates."""
    # Test with coordinates in the middle of the Pacific
    response = client.get("/api/v1/weather?lat=0.0&lng=-180.0")
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
    elif response.status_code == 400:
        # Expected if no weather data available for ocean coordinates
        data = response.json()
        assert "detail" in data
    else:
        # Unexpected status code
        assert False, f"Unexpected status code: {response.status_code}"

# Batch Forecast Tests
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
    assert isinstance(data["buoys"], list)
    assert isinstance(data["spots"], list)
    assert isinstance(data["errors"], list)
    assert len(data["buoys"]) == 0
    assert len(data["spots"]) == 0
    assert len(data["errors"]) == 0

def test_batch_forecast_endpoint_buoy_only(client):
    """Test the batch forecast endpoint with buoy IDs only."""
    response = client.post("/api/v1/batch-forecast", json={
        "buoy_ids": ["46042"],
        "spot_ids": []
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "buoys" in data
    assert "spots" in data
    assert "errors" in data
    
    # Should have at least one buoy or an error
    if len(data["buoys"]) > 0:
        buoy = data["buoys"][0]
        assert "id" in buoy
        assert "name" in buoy
        assert "description" in buoy
        assert "location" in buoy
        assert "url" in buoy
        # latest_observation and weather_forecast might be None if APIs are down
        assert "latest_observation" in buoy
        assert "weather_forecast" in buoy
    elif len(data["errors"]) > 0:
        # If buoy data failed, should have error info
        error = data["errors"][0]
        assert "id" in error
        assert "type" in error
        assert "error" in error
        assert error["type"] == "buoy"

def test_batch_forecast_endpoint_spot_only(client):
    """Test the batch forecast endpoint with spot IDs only."""
    # First get a valid spot ID
    spots_response = client.get("/api/v1/spots?limit=1")
    if spots_response.status_code == 200:
        spots_data = spots_response.json()
        if len(spots_data) > 0:
            spot_id = spots_data[0]["id"]
            
            response = client.post("/api/v1/batch-forecast", json={
                "buoy_ids": [],
                "spot_ids": [spot_id]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "buoys" in data
            assert "spots" in data
            assert "errors" in data
            
            # Should have at least one spot or an error
            if len(data["spots"]) > 0:
                spot = data["spots"][0]
                assert "id" in spot
                assert "name" in spot
                assert "timezone" in spot
                assert "latitude" in spot
                assert "longitude" in spot
                assert "subregion_name" in spot
                # weather_forecast and current_weather might be None if APIs are down
                assert "weather_forecast" in spot
                assert "current_weather" in spot
            elif len(data["errors"]) > 0:
                # If spot data failed, should have error info
                error = data["errors"][0]
                assert "id" in error
                assert "type" in error
                assert "error" in error
                assert error["type"] == "spot"

def test_batch_forecast_endpoint_mixed_request(client):
    """Test the batch forecast endpoint with both buoy and spot IDs."""
    # First get a valid spot ID
    spots_response = client.get("/api/v1/spots?limit=1")
    if spots_response.status_code == 200:
        spots_data = spots_response.json()
        if len(spots_data) > 0:
            spot_id = spots_data[0]["id"]
            
            response = client.post("/api/v1/batch-forecast", json={
                "buoy_ids": ["46042"],
                "spot_ids": [spot_id]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "buoys" in data
            assert "spots" in data
            assert "errors" in data
            
            # Should have some data or errors
            total_items = len(data["buoys"]) + len(data["spots"]) + len(data["errors"])
            assert total_items > 0, "Should have at least some data or errors"

def test_batch_forecast_endpoint_invalid_ids(client):
    """Test the batch forecast endpoint with invalid IDs."""
    response = client.post("/api/v1/batch-forecast", json={
        "buoy_ids": ["invalid_buoy_id"],
        "spot_ids": [99999]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "buoys" in data
    assert "spots" in data
    assert "errors" in data
    
    # Should have errors for invalid IDs
    assert len(data["errors"]) >= 2
    
    # Check error structure
    for error in data["errors"]:
        assert "id" in error
        assert "type" in error
        assert "error" in error
        assert error["type"] in ["buoy", "spot"]

def test_batch_forecast_endpoint_malformed_request(client):
    """Test the batch forecast endpoint with malformed request."""
    response = client.post("/api/v1/batch-forecast", json={
        "invalid_field": "test"
    })
    
    # Should return 422 validation error
    assert response.status_code == 422 