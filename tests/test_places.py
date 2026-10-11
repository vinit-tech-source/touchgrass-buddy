import pytest
from app.places import classify_text, get_categorized_places, get_nearby_places, CATEGORY_FALLBACK_IMAGES

class TestClassifyText:
    def test_fort_classification(self):
        assert classify_text("Sinhagad Fort") == "fort"
        assert classify_text("Historic Citadel Ruins") == "fort"

    def test_temple_classification(self):
        assert classify_text("Dagadusheth Mandir") == "temple"
        assert classify_text("St. Mary's Church") == "temple"

    def test_mountain_classification(self):
        assert classify_text("Vetal Tekdi") == "mountain"
        assert classify_text("Scenic Mountain Peak") == "mountain"

    def test_cafe_classification(self):
        assert classify_text("Cafe Goodluck") == "cafe"
        assert classify_text("Artisan Coffee Roasters") == "cafe"

    def test_park_classification(self):
        assert classify_text("Central Botanical Garden") == "park"
        assert classify_text("Nature Reserve") == "park"

@pytest.mark.asyncio
async def test_get_categorized_places_structure():
    # Test that get_categorized_places returns proper schema even if offline or live
    res = await get_categorized_places(18.627, 73.813, radius_km=2, place_label="Pimpri")
    assert "best_destination" in res
    assert "categories" in res
    assert "all_places" in res
    assert "cafe" in res["categories"]
    assert "mountain" in res["categories"]
    assert "temple" in res["categories"]
    assert "fort" in res["categories"]
    assert "park" in res["categories"]

    best = res["best_destination"]
    assert best is not None
    assert "name" in best
    assert "category" in best
    assert "maps_url" in best
    assert "image" in best
