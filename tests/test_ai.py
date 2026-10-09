import pytest
from app.ai import validate_mission, _extract_json, verify_photo, DEFAULT_MISSION

class TestValidateMission:
    def test_valid_mission(self):
        data = {
            "title": "Test Walk",
            "steps": ["Step 1", "Step 2"],
            "mini_challenge": "Take a photo",
            "safety_tip": "Stay safe",
            "duration_min": 20
        }
        res = validate_mission(data)
        assert res is not None
        assert res["duration_min"] == 20

    def test_invalid_mission_missing_keys(self):
        data = {"title": "Test Walk", "steps": ["Step 1"]}
        assert validate_mission(data) is None

class TestExtractJson:
    def test_clean_json(self):
        text = '{"title": "x", "steps": ["a", "b"], "mini_challenge": "c", "safety_tip": "d", "duration_min": 10}'
        res = _extract_json(text)
        assert res is not None
        assert res["title"] == "x"

    def test_markdown_fence(self):
        text = "Here is your mission:\n```json\n{\"title\": \"x\"}\n```"
        res = _extract_json(text)
        assert res is not None
        assert res["title"] == "x"

@pytest.mark.asyncio
async def test_verify_photo_fallback():
    """Test that verify_photo handles failures gracefully by returning the fallback."""
    # With a dummy base64 string, HTTP call to Ollama will likely fail
    # or return a 404 if moondream isn't running.
    try:
        result = await verify_photo("dummy_base64", "find a leaf")
        assert "verified" in result
        assert isinstance(result["verified"], bool)
    except ValueError as e:
        assert "Vision model missing" in str(e)

class TestDefaultMission:
    def test_default_mission_is_valid(self):
        result = validate_mission(dict(DEFAULT_MISSION))
        assert result is not None
