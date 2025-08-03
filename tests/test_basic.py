import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import app
from app.classes.spotlocation import SpotLocation

def test_spot_location_creation():
    """Test creating a SpotLocation instance."""
    sample_data = {
        "id": 1,
        "name": "Test Spot",
        "timezone": "America/Los_Angeles",
        "latitude": 36.95,
        "longitude": -121.97,
        "subregion_name": "Central California"
    }
    
    # Create a mock object with the sample data
    mock_spot = type('MockSpot', (), sample_data)()
    spot = SpotLocation.from_obj(mock_spot)
    
    assert spot.id == 1
    assert spot.name == "Test Spot"
    assert spot.latitude == 36.95
    assert spot.longitude == -121.97

def test_spot_location_geojson():
    """Test that SpotLocation generates valid GeoJSON."""
    sample_data = {
        "id": 1,
        "name": "Test Spot",
        "timezone": "America/Los_Angeles",
        "latitude": 36.95,
        "longitude": -121.97,
        "subregion_name": "Central California"
    }
    
    mock_spot = type('MockSpot', (), sample_data)()
    spot = SpotLocation.from_obj(mock_spot)
    geojson = spot.get_geojson()
    
    # Check GeoJSON structure
    assert geojson["type"] == "Feature"
    assert geojson["geometry"]["type"] == "Point"
    assert len(geojson["geometry"]["coordinates"]) == 2
    
    # Check coordinates are in correct order [longitude, latitude]
    assert geojson["geometry"]["coordinates"][0] == -121.97  # longitude
    assert geojson["geometry"]["coordinates"][1] == 36.95    # latitude
    
    # Check properties
    assert geojson["properties"]["id"] == 1
    assert geojson["properties"]["name"] == "Test Spot"

def test_buoy_location_parsing():
    """Test BuoyLocation coordinate parsing."""
    from app.classes.buoylocation import BuoyLocation
    
    sample_data = {
        "location": "36.95 N 121.97 W",
        "location_id": "test123",
        "name": "Test Buoy",
        "url": "https://example.com",
        "description": "Test buoy location"
    }
    
    mock_buoy = type('MockBuoy', (), sample_data)()
    buoy = BuoyLocation.from_obj(mock_buoy)
    coords = buoy.parse_location()
    
    # Should return [longitude, latitude]
    assert coords[0] == -121.97  # longitude
    assert coords[1] == 36.95    # latitude 

def test_tides_current_endpoint_success():
    """Test successful tides current endpoint call."""
    with patch('httpx.get') as mock_get:
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "predictions": [
                {"t": "2024-01-01 12:00", "v": "5.2"},
                {"t": "2024-01-01 18:00", "v": "1.1"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = TestClient(app)
        response = client.get("/tides/current?station=9414290")
        
        assert response.status_code == 200
        assert "predictions" in response.json()
        
        # Verify the correct URL was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "station=9414290" in str(call_args)
        assert "date=latest" in str(call_args)  # New default
        assert "interval=hour" in str(call_args)  # New parameter

def test_tides_current_endpoint_missing_station():
    """Test tides current endpoint with missing required station parameter."""
    client = TestClient(app)
    response = client.get("/tides/current")
    
    assert response.status_code == 422  # Validation error

def test_tides_current_endpoint_http_error():
    """Test tides current endpoint with HTTP error from NOAA API."""
    with patch('httpx.get') as mock_get:
        # Mock HTTP error
        mock_get.side_effect = Exception("Connection error")
        
        client = TestClient(app)
        response = client.get("/tides/current?station=9414290")
        
        assert response.status_code == 400
        assert "Failed to connect to NOAA API" in response.json()["detail"]

def test_tides_endpoint_with_date_range():
    """Test tides endpoint with begin_date and end_date parameters."""
    with patch('httpx.get') as mock_get:
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "predictions": [
                {"t": "2024-01-01 12:00", "v": "5.2"},
                {"t": "2024-01-02 12:00", "v": "5.1"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = TestClient(app)
        response = client.get("/tides?station=9414290&begin_date=20240101&end_date=20240102")
        
        assert response.status_code == 200
        assert "predictions" in response.json()
        
        # Verify date range parameters were passed
        call_args = mock_get.call_args
        assert "begin_date=20240101" in str(call_args)
        assert "end_date=20240102" in str(call_args)

def test_tides_find_closest_endpoint():
    """Test finding closest tide station endpoint."""
    with patch('app.routers.tides.get_db') as mock_get_db:
        # Mock database session with sample tide stations
        mock_db = Mock()
        mock_stations = [
            Mock(station_id="9414290", latitude=32.7157, longitude=-117.1617),  # San Diego
            Mock(station_id="9410230", latitude=32.8669, longitude=-117.2567),  # La Jolla
        ]
        mock_db.query.return_value.all.return_value = mock_stations
        mock_get_db.return_value = mock_db
        
        client = TestClient(app)
        response = client.get("/tides/find_closest?lat=32.7157&lng=-117.1617&dist=50")
        
        assert response.status_code == 200
        result = response.json()
        assert result["station_id"] == "9414290"  # Should find San Diego station
        assert result["distance"] < 1  # Should be very close to exact coordinates

def test_tides_find_closest_no_stations():
    """Test finding closest tide station when no stations exist."""
    with patch('app.routers.tides.get_db') as mock_get_db:
        # Mock empty database
        mock_db = Mock()
        mock_db.query.return_value.all.return_value = []
        mock_get_db.return_value = mock_db
        
        client = TestClient(app)
        response = client.get("/tides/find_closest?lat=32.7157&lng=-117.1617")
        
        assert response.status_code == 404
        assert "no tide stations found" in response.json()["detail"]

def test_tides_find_closest_out_of_range():
    """Test finding closest tide station when all stations are out of range."""
    with patch('app.routers.tides.get_db') as mock_get_db:
        # Mock stations far from query point
        mock_db = Mock()
        mock_stations = [
            Mock(station_id="9414290", latitude=40.0, longitude=-120.0),  # Far away
        ]
        mock_db.query.return_value.all.return_value = mock_stations
        mock_get_db.return_value = mock_db
        
        client = TestClient(app)
        response = client.get("/tides/find_closest?lat=32.7157&lng=-117.1617&dist=50")
        
        assert response.status_code == 404
        assert "tide data not available" in response.json()["detail"] 

def test_tides_stations_endpoint_success():
    """Test successful get all tide stations endpoint call."""
    with patch('app.routers.tides.get_db') as mock_get_db:
        # Mock database session with sample tide stations
        mock_db = Mock()
        mock_stations = [
            Mock(
                id=1,
                station_id="9414290",
                station_name="San Diego, CA",
                latitude="32.7157",
                longitude="-117.1617"
            ),
            Mock(
                id=2,
                station_id="9410230",
                station_name="La Jolla, CA",
                latitude="32.8669",
                longitude="-117.2567"
            )
        ]
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_stations
        mock_get_db.return_value = mock_db
        
        client = TestClient(app)
        response = client.get("/tides/stations?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert "stations" in data
        assert len(data["stations"]) == 2
        assert data["total"] == 2
        assert data["limit"] == 10
        assert data["offset"] == 0
        
        # Check first station data
        first_station = data["stations"][0]
        assert first_station["station_id"] == "9414290"
        assert first_station["station_name"] == "San Diego, CA"
        assert first_station["latitude"] == "32.7157"
        assert first_station["longitude"] == "-117.1617"

def test_tides_stations_endpoint_no_stations():
    """Test get all tide stations when no stations exist."""
    with patch('app.routers.tides.get_db') as mock_get_db:
        # Mock empty database
        mock_db = Mock()
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_get_db.return_value = mock_db
        
        client = TestClient(app)
        response = client.get("/tides/stations")
        
        assert response.status_code == 404
        assert "No tide stations found" in response.json()["detail"]

def test_tides_stations_endpoint_pagination():
    """Test tide stations endpoint pagination."""
    with patch('app.routers.tides.get_db') as mock_get_db:
        # Mock database session with pagination
        mock_db = Mock()
        mock_stations = [
            Mock(
                id=3,
                station_id="9410660",
                station_name="Los Angeles, CA",
                latitude="33.7203",
                longitude="-118.2728"
            )
        ]
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_stations
        mock_get_db.return_value = mock_db
        
        client = TestClient(app)
        response = client.get("/tides/stations?limit=1&offset=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["stations"]) == 1
        assert data["limit"] == 1
        assert data["offset"] == 2
        assert data["stations"][0]["station_id"] == "9410660"

def test_tides_station_by_id_endpoint_success():
    """Test successful get tide station by ID endpoint call."""
    with patch('app.routers.tides.get_db') as mock_get_db:
        # Mock database session with specific station
        mock_db = Mock()
        mock_station = Mock(
            id=1,
            station_id="9414290",
            station_name="San Diego, CA",
            latitude="32.7157",
            longitude="-117.1617"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_station
        mock_get_db.return_value = mock_db
        
        client = TestClient(app)
        response = client.get("/tides/stations/9414290")
        
        assert response.status_code == 200
        data = response.json()
        assert data["station_id"] == "9414290"
        assert data["station_name"] == "San Diego, CA"
        assert data["latitude"] == "32.7157"
        assert data["longitude"] == "-117.1617"

def test_tides_station_by_id_endpoint_not_found():
    """Test get tide station by ID when station doesn't exist."""
    with patch('app.routers.tides.get_db') as mock_get_db:
        # Mock database session with no station found
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value = mock_db
        
        client = TestClient(app)
        response = client.get("/tides/stations/nonexistent")
        
        assert response.status_code == 404
        assert "Tide station nonexistent not found" in response.json()["detail"] 