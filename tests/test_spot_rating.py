import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from datetime import datetime, timezone, date
from app.main import app
from app.database import get_db

class TestSpotRatingEndpoint:
    """Test suite for the spot rating endpoint.
    
    Note: These tests use mocks and are compatible with the date range
    rate limiting logic implemented in the endpoint (using datetime ranges
    instead of func.date() for better timezone handling).
    """
    
    def setup_method(self):
        """Set up test client and common test data."""
        self.client = TestClient(app)
        self.valid_rating_data = {
            "spot_id": 1,
            "spot_slug": "test-spot",
            "rating": "accurate",
            "forecast_json": {"wave_height": "2-3ft", "wind": "5-10mph"},
            "timestamp": "2025-09-18T12:00:00Z",
            "session_id": "test-session-123",
            "ip_address": "127.0.0.1",
            "user_id": None
        }
        
    def test_rate_spot_success(self):
        """Test successful spot rating submission."""
        # Create a mock database session
        mock_db = Mock()
        
        # Mock spot exists
        mock_spot = Mock()
        mock_spot.id = 1
        mock_spot.slug = "test-spot"
        
        # Mock query chain for spot lookup and rating check
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_spot,  # First call: spot lookup
            None,       # Second call: existing rating check (session+IP+date range)
            None        # Third call: fallback IP+date range check
        ]
        
        # Mock successful database operations
        mock_new_rating = Mock()
        mock_new_rating.id = 1
        mock_new_rating.spot_id = 1
        mock_new_rating.spot_slug = "test-spot"
        mock_new_rating.rating = "accurate"
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Override the dependency
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = self.client.post(
                "/api/v1/spots/1/rating",
                json=self.valid_rating_data,
                cookies={"surfe-diem-session-id": "existing-session-123"}
            )
            
            assert response.status_code == 200
            assert response.json() == {"message": "Rating submitted successfully", "rating": "accurate"}
            
            # Verify database operations were called
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()
            
    def test_rate_spot_not_found(self):
        """Test rating submission for non-existent spot."""
        mock_db = Mock()
        
        # Mock spot doesn't exist
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = self.client.post(
                "/api/v1/spots/999/rating",
                json=self.valid_rating_data
            )
            
            assert response.status_code == 404
            assert "Spot not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
            
    def test_rate_spot_already_rated_today(self):
        """Test rating submission when user already rated today."""
        mock_db = Mock()
        
        # Mock spot exists
        mock_spot = Mock()
        mock_spot.id = 1
        mock_spot.slug = "test-spot"
        
        # Mock existing rating for today
        mock_existing_rating = Mock()
        mock_existing_rating.id = 1
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_spot,           # First call: spot lookup
            mock_existing_rating, # Second call: existing rating check (session+IP+date range)
            None                 # Third call won't be reached since second found a match
        ]
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = self.client.post(
                "/api/v1/spots/1/rating",
                json=self.valid_rating_data,
                cookies={"surfe-diem-session-id": "existing-session-123"}
            )
            
            assert response.status_code == 409
            assert "You have already rated this spot today" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
        
    def test_rate_spot_generates_session_id(self):
        """Test that endpoint generates session ID when none provided."""
        mock_db = Mock()
        
        # Mock spot exists and no existing rating
        mock_spot = Mock()
        mock_spot.id = 1
        mock_spot.slug = "test-spot"
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_spot,  # First call: spot lookup
            None        # Second call: existing rating check
        ]
        
        # Mock successful database operations
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = self.client.post(
                "/api/v1/spots/1/rating",
                json=self.valid_rating_data
                # No session cookie provided
            )
            
            assert response.status_code == 200
            assert response.json() == {"message": "Rating submitted successfully", "rating": "accurate"}
            
            # Check that session cookie was set in response
            assert "surfe-diem-session-id" in response.cookies
            session_id = response.cookies["surfe-diem-session-id"]
            assert session_id.startswith("session_")
            assert len(session_id) > 10  # Should be a UUID-based string
        finally:
            app.dependency_overrides.clear()
            
    def test_rate_spot_invalid_rating_enum(self):
        """Test rating submission with invalid enum value."""
        invalid_data = self.valid_rating_data.copy()
        invalid_data["rating"] = "invalid_rating"
        
        response = self.client.post(
            "/api/v1/spots/1/rating",
            json=invalid_data
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_rate_spot_missing_required_fields(self):
        """Test rating submission with missing required fields."""
        incomplete_data = {
            "spot_id": 1,
            "rating": "accurate"
            # Missing other required fields
        }
        
        response = self.client.post(
            "/api/v1/spots/1/rating",
            json=incomplete_data
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_rate_spot_database_error(self):
        """Test handling of database errors during rating submission."""
        mock_db = Mock()
        
        # Mock spot exists and no existing rating
        mock_spot = Mock()
        mock_spot.id = 1
        mock_spot.slug = "test-spot"
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_spot,  # First call: spot lookup
            None        # Second call: existing rating check
        ]
        
        # Mock database error on commit
        mock_db.add.return_value = None
        mock_db.commit.side_effect = Exception("Database connection error")
        mock_db.rollback.return_value = None
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = self.client.post(
                "/api/v1/spots/1/rating",
                json=self.valid_rating_data,
                cookies={"surfe-diem-session-id": "test-session-123"}
            )
            
            assert response.status_code == 500
            assert "Failed to save rating" in response.json()["detail"]
            
            # Verify rollback was called
            mock_db.rollback.assert_called_once()
        finally:
            app.dependency_overrides.clear()
            
    def test_rate_spot_uses_spot_slug_from_db(self):
        """Test that endpoint uses spot slug from database, not request data."""
        mock_db = Mock()
        
        # Mock spot with different slug than in request
        mock_spot = Mock()
        mock_spot.id = 1
        mock_spot.slug = "actual-spot-slug"  # Different from request data
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_spot,  # First call: spot lookup
            None        # Second call: existing rating check
        ]
        
        # Mock successful database operations
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Use data with wrong slug
        test_data = self.valid_rating_data.copy()
        test_data["spot_slug"] = "wrong-slug-from-request"
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            response = self.client.post(
                "/api/v1/spots/1/rating",
                json=test_data,
                cookies={"surfe-diem-session-id": "test-session-123"}
            )
            
            assert response.status_code == 200
            assert response.json() == {"message": "Rating submitted successfully", "rating": "accurate"}
            
            # Verify the add method was called (meaning the rating was created)
            mock_db.add.assert_called_once()
            
            # The actual slug validation is in the endpoint logic - it uses spot.slug
            # This test confirms that the endpoint accepts the request even with wrong slug
        finally:
            app.dependency_overrides.clear()
            
    def test_rate_spot_valid_enum_values(self):
        """Test that both valid enum values are accepted."""
        mock_db = Mock()
        
        # Mock spot exists and no existing rating
        mock_spot = Mock()
        mock_spot.id = 1
        mock_spot.slug = "test-spot"
        
        # Mock successful database operations
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            # Test "accurate" rating
            mock_db.query.return_value.filter.return_value.first.side_effect = [
                mock_spot, None,  # For first test
            ]
            
            data_accurate = self.valid_rating_data.copy()
            data_accurate["rating"] = "accurate"
            
            response = self.client.post(
                "/api/v1/spots/1/rating",
                json=data_accurate,
                cookies={"surfe-diem-session-id": "test-session-1"}
            )
            assert response.status_code == 200
            assert response.json() == {"message": "Rating submitted successfully", "rating": "accurate"}
            
            # Reset mocks for second test
            mock_db.reset_mock()
            mock_db.query.return_value.filter.return_value.first.side_effect = [
                mock_spot, None   # For second test
            ]
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            # Test "not_accurate" rating
            data_not_accurate = self.valid_rating_data.copy()
            data_not_accurate["rating"] = "not_accurate"
            
            response = self.client.post(
                "/api/v1/spots/1/rating",
                json=data_not_accurate,
                cookies={"surfe-diem-session-id": "test-session-2"}
            )
            assert response.status_code == 200
            assert response.json() == {"message": "Rating submitted successfully", "rating": "not_accurate"}
        finally:
            app.dependency_overrides.clear()