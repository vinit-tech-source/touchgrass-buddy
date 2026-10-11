import pytest
from starlette.testclient import TestClient
from app.main import app
from app.ai import DEFAULT_MISSION, validate_mission, ask_forest_chat

client = TestClient(app)

def test_default_mission_scavenger_items():
    assert "scavenger_items" in DEFAULT_MISSION
    assert len(DEFAULT_MISSION["scavenger_items"]) == 3

def test_validate_mission_adds_scavenger_items():
    raw = {
        "title": "A Walk",
        "steps": ["Step 1", "Step 2"],
        "mini_challenge": "Spot a leaf",
        "safety_tip": "Stay alert",
        "duration_min": 25
    }
    validated = validate_mission(raw)
    assert validated is not None
    assert "scavenger_items" in validated
    assert len(validated["scavenger_items"]) == 3

def test_pwa_manifest_route():
    response = client.get("/manifest.json")
    assert response.status_code == 200
    assert "application/manifest+json" in response.headers["content-type"]
    data = response.json()
    assert data["name"] == "TouchGrass Buddy"
    assert data["short_name"] == "TouchGrass"
    assert data["theme_color"] == "#0B120F"

def test_pwa_service_worker_route():
    response = client.get("/sw.js")
    assert response.status_code == 200
    assert response.headers.get("Service-Worker-Allowed") == "/"
    assert "javascript" in response.headers["content-type"]
    assert "CACHE_NAME" in response.text

def test_forest_chat_api():
    response = client.post("/api/forest_chat", json={
        "message": "What is the best way to spot birds quietly?",
        "context": "Sunset walk in Central Park"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 5
