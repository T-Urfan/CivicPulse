"""Unit tests for FastAPI routes and core business paths."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the liveness probe."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_request_id_middleware():
    """Test that X-Request-ID is generated and returned."""
    response = client.get("/health")
    assert "X-Request-ID" in response.headers


def test_validation_error_contract():
    """Test that validation errors return 400 instead of 422."""
    # Attempting to create a complaint with an empty text should trigger validation
    payload = {
        "text": "",  # Too short
        "location": "Test"
    }
    
    # We don't actually hit the DB because validation happens in the route signature
    response = client.post("/api/complaints", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
