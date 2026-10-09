"""
places.py — Look up real nearby outdoor places using OpenStreetMap Overpass API.
"""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=0.5, min=1, max=3),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
)
async def fetch_overpass_places(lat: float, lon: float, radius_m: int, limit: int) -> list[dict]:
    query = f"""
    [out:json][timeout:5];
    (
      node["leisure"="park"](around:{radius_m},{lat},{lon});
      way["leisure"="park"](around:{radius_m},{lat},{lon});
      node["leisure"="garden"](around:{radius_m},{lat},{lon});
      way["leisure"="garden"](around:{radius_m},{lat},{lon});
      node["leisure"="nature_reserve"](around:{radius_m},{lat},{lon});
      way["leisure"="nature_reserve"](around:{radius_m},{lat},{lon});
    );
    out center {limit};
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(OVERPASS_URL, data={"data": query})
        resp.raise_for_status()
        data = resp.json()
    
    places = []
    seen_names = set()
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name")
        if name and name not in seen_names:
            seen_names.add(name)
            # Ways have 'center' lat/lon, Nodes have 'lat'/'lon' directly
            plat = element.get("lat") or (element.get("center", {})).get("lat")
            plon = element.get("lon") or (element.get("center", {})).get("lon")
            if plat and plon:
                places.append({
                    "name": name,
                    "lat": plat,
                    "lon": plon
                })
    return places[:limit]

async def get_nearby_places(lat: float, lon: float, radius_m: int = 2000, limit: int = 3) -> list[dict]:
    """
    Find nearby parks, gardens, or nature reserves using Overpass API.
    Returns a list of dicts: [{'name': 'Park Name', 'lat': 51.5, 'lon': -0.1}]
    Falls back to [] gracefully if the API fails entirely.
    """
    try:
        return await fetch_overpass_places(lat, lon, radius_m, limit)
    except Exception:
        # Graceful fallback: return empty list so the app continues without places
        return []
