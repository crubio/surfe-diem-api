import pytest

@pytest.fixture
def sample_spot_data():
    """Sample data for testing spot locations."""
    return {
        "id": 1,
        "name": "Test Spot",
        "timezone": "America/Los_Angeles",
        "latitude": 36.95,
        "longitude": -121.97,
        "subregion_name": "Central California"
    } 