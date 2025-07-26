import pytest
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