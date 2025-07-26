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