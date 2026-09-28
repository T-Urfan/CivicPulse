"""Smoke tests for the CivicPulse backend foundation."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_endpoint_returns_alive() -> None:
    """GET /health must return 200 with liveness status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_health_returns_request_id() -> None:
    """GET /health must propagate or generate X-Request-ID."""
    response = client.get("/health", headers={"X-Request-ID": "test-req-001"})
    assert response.headers["X-Request-ID"] == "test-req-001"


def test_health_generates_request_id_when_absent() -> None:
    """GET /health must generate X-Request-ID when not provided."""
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_openapi_schema_available() -> None:
    """FastAPI must expose an OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "CivicPulse API"


def test_domain_enums_match_assignment_contract() -> None:
    """Domain enums must exactly match the assignment specification."""
    from app.models import Category, Priority, Status

    assert set(Category) == {
        Category.WATER, Category.ELECTRICITY, Category.SANITATION,
        Category.ROADS, Category.STREETLIGHTS, Category.OTHER,
    }
    assert set(Priority) == {Priority.HIGH, Priority.NORMAL, Priority.LOW}
    assert set(Status) == {
        Status.OPEN, Status.IN_PROGRESS, Status.RESOLVED, Status.REJECTED,
    }


def test_state_machine_valid_transitions() -> None:
    """Valid status transitions must be accepted."""
    from app.models import Status, is_valid_transition

    assert is_valid_transition(Status.OPEN, Status.IN_PROGRESS)
    assert is_valid_transition(Status.OPEN, Status.REJECTED)
    assert is_valid_transition(Status.IN_PROGRESS, Status.RESOLVED)
    assert is_valid_transition(Status.IN_PROGRESS, Status.REJECTED)


def test_state_machine_invalid_transitions() -> None:
    """Invalid status transitions must be rejected."""
    from app.models import Status, is_valid_transition

    # Terminal states cannot transition
    assert not is_valid_transition(Status.RESOLVED, Status.OPEN)
    assert not is_valid_transition(Status.REJECTED, Status.OPEN)
    # Backward transitions
    assert not is_valid_transition(Status.IN_PROGRESS, Status.OPEN)
    assert not is_valid_transition(Status.RESOLVED, Status.IN_PROGRESS)
    # Skip transitions
    assert not is_valid_transition(Status.OPEN, Status.RESOLVED)


def test_complaint_create_validation_text_too_short() -> None:
    """ComplaintCreate must reject text shorter than 10 characters."""
    from app.models import ComplaintCreate
    from pydantic import ValidationError

    try:
        ComplaintCreate(text="short", location="Test Location")
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        errors = e.errors()
        assert any("text" in str(err.get("loc", "")) for err in errors)


def test_complaint_create_validation_accepts_valid_input() -> None:
    """ComplaintCreate must accept valid inputs."""
    from app.models import ComplaintCreate

    complaint = ComplaintCreate(
        text="Water pipe burst near main market causing flooding on the road",
        location="Gulberg III, Lahore",
        reporter_contact="citizen@example.com",
    )
    assert complaint.text.startswith("Water pipe")
    assert complaint.location == "Gulberg III, Lahore"
    assert complaint.reporter_contact == "citizen@example.com"
