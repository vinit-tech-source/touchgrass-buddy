"""
places.py: Look up real nearby outdoor places, categorized spots (cafe, mountain,
temple, fort, park), and high-resolution photos using Wikipedia Geosearch and OpenStreetMap.
"""

from __future__ import annotations

import asyncio
from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

USER_AGENT = "TouchGrassBuddyApp/3.0 (vinit.project@gmail.com)"

CATEGORY_FALLBACK_IMAGES: dict[str, str] = {
    "cafe": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=600&q=80",
    "mountain": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80",
    "temple": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=600&q=80",
    "fort": "https://images.unsplash.com/photo-1585123334904-845d60e97b29?auto=format&fit=crop&w=600&q=80",
    "park": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=600&q=80"
}

import re

def classify_text(text: str) -> str:
    """Classify place into cafe, mountain, temple, fort, or park."""
    t = text.lower()
    if any(k in t for k in ["temple", "mandir", "shrine", "gurdwara", "church", "cathedral", "mosque", "pagoda", "ashram"]):
        return "temple"
    if any(k in t for k in ["cafe", "coffee", "bistro", "bakery", "tea", "espresso", "roastery"]):
        return "cafe"
    if any(k in t for k in ["hill", "mountain", "tekdi", "peak", "ghat", "range", "ridge", "cliff", "mount"]):
        return "mountain"
    if re.search(r"\b(fort|castle|citadel|bastion|monument|ruins|qila)\b", t) or re.search(r"[a-z]+gad\b", t):
        return "fort"
    if any(k in t for k in ["park", "garden", "reserve", "sanctuary", "lake", "forest", "woodland", "botanical"]):
        return "park"
    return "park"


async def fetch_spot_image(client: httpx.AsyncClient, name: str) -> str | None:
    """Try to find a high-resolution Wikipedia/Wikimedia image for a place name."""
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": name,
            "prop": "pageimages",
            "pithumbsize": 600,
            "redirects": 1
        }
        r = await client.get(url, params=params)
        pages = r.json().get("query", {}).get("pages", {})
        for pid, p in pages.items():
            if pid != "-1":
                thumb = p.get("thumbnail", {}).get("source")
                if thumb:
                    return thumb
    except Exception:
        pass

    # Try Wikipedia Opensearch fallback
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={name}&limit=1&namespace=0&format=json"
        sr = await client.get(search_url)
        titles = sr.json()[1]
        if titles:
            title = titles[0]
            r2 = await client.get("https://en.wikipedia.org/w/api.php", params={
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "pageimages",
                "pithumbsize": 600
            })
            pages2 = r2.json().get("query", {}).get("pages", {})
            for pid, p in pages2.items():
                thumb = p.get("thumbnail", {}).get("source")
                if thumb:
                    return thumb
    except Exception:
        pass

    return None

async def fetch_wikipedia_geosearch(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    radius_m: int = 10000
) -> list[dict[str, Any]]:
    """Fetch nearby landmarks and places with verified Wikipedia photos and coordinates."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "geosearch",
        "ggscoord": f"{lat}|{lon}",
        "ggsradius": min(radius_m, 10000),
        "ggslimit": "25",
        "prop": "pageimages|description|coordinates",
        "pithumbsize": "600",
        "format": "json"
    }
    spots: list[dict[str, Any]] = []
    try:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            pages = resp.json().get("query", {}).get("pages", {})
            for pid, p in pages.items():
                title = p.get("title", "")
                # Skip political or transit articles
                if any(bad in title.lower() for bad in [
                    "constituency", "assembly", "election", "station", "hospital",
                    "institute", "metro", "virology", "stadium"
                ]):
                    continue
                desc = p.get("description", "")
                thumb = p.get("thumbnail", {}).get("source")
                coords = p.get("coordinates", [{}])[0]
                plat = coords.get("lat", lat)
                plon = coords.get("lon", lon)
                cat = classify_text(f"{title} {desc}")

                spots.append({
                    "name": title,
                    "category": cat,
                    "description": desc or f"Scenic outdoor destination near you",
                    "image": thumb or CATEGORY_FALLBACK_IMAGES[cat],
                    "has_real_photo": bool(thumb),
                    "lat": plat,
                    "lon": plon,
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={plat},{plon}"
                })
    except Exception:
        pass
    return spots

async def fetch_wiki_search_category(
    client: httpx.AsyncClient,
    place_label: str,
    category: str,
    lat: float,
    lon: float
) -> list[dict[str, Any]]:
    """Search Wikipedia for category when local radius is sparse (e.g. regional forts or mountains)."""
    q_term = "fort" if category == "fort" else ("hill" if category == "mountain" else category)
    query = f"{place_label} {q_term}".strip()
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": "2",
        "prop": "pageimages|description|coordinates",
        "pithumbsize": "600",
        "format": "json"
    }
    results: list[dict[str, Any]] = []
    try:
        r = await client.get(url, params=params)
        pages = r.json().get("query", {}).get("pages", {})
        for pid, p in pages.items():
            title = p.get("title", "")
            if any(b in title.lower() for b in ["list of", "transit", "station", "constituency", "assembly", "election"]):
                continue
            coords = p.get("coordinates", [{}])[0]
            plat = coords.get("lat", lat)
            plon = coords.get("lon", lon)
            thumb = p.get("thumbnail", {}).get("source")
            desc = p.get("description", "")
            results.append({
                "name": title,
                "category": category,
                "description": desc or f"Notable regional {category.capitalize()} destination",
                "image": thumb or CATEGORY_FALLBACK_IMAGES[category],
                "has_real_photo": bool(thumb),
                "lat": plat,
                "lon": plon,
                "maps_url": f"https://www.google.com/maps/search/?api=1&query={plat},{plon}"
            })
    except Exception:
        pass
    return results

async def fetch_nominatim_category(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    category: str,
    limit: int = 3
) -> list[dict[str, Any]]:
    """Fetch specific category spots from OpenStreetMap Nominatim."""
    # Forts & mountains are regional landmarks, so expand bounding box accordingly
    d = 0.35 if category == "fort" else (0.20 if category == "mountain" else 0.08)
    viewbox = f"{lon-d},{lat+d},{lon+d},{lat-d}"
    query_map = {
        "cafe": "cafe",
        "mountain": "hill",
        "temple": "temple",
        "fort": "fort",
        "park": "garden"
    }
    q = query_map.get(category, category)
    params = {
        "q": q,
        "format": "json",
        "viewbox": viewbox,
        "bounded": 1,
        "limit": limit
    }
    results: list[dict[str, Any]] = []
    try:
        resp = await client.get("https://nominatim.openstreetmap.org/search", params=params)
        if resp.status_code == 200:
            for item in resp.json():
                raw_name = item.get("name")
                if not raw_name or raw_name.lower() in ["temple", "hill", "cafe", "garden", "fort"]:
                    display = item.get("display_name", "").split(",")
                    name = display[0].strip() if display else f"Local {category.capitalize()}"
                    # If display still matches generic word, take second segment
                    if name.lower() in ["temple", "hill", "cafe", "garden", "fort"] and len(display) > 1:
                        name = f"{display[1].strip()} {category.capitalize()}"
                else:
                    name = raw_name

                plat = float(item["lat"])
                plon = float(item["lon"])
                
                # Check for Wikipedia image for this spot
                img = await fetch_spot_image(client, name)
                results.append({
                    "name": name,
                    "category": category,
                    "description": f"Nearby {category.capitalize()} to visit and explore",
                    "image": img or CATEGORY_FALLBACK_IMAGES[category],
                    "has_real_photo": bool(img),
                    "lat": plat,
                    "lon": plon,
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={plat},{plon}"
                })
    except Exception:
        pass
    return results

async def get_categorized_places(
    lat: float,
    lon: float,
    radius_km: int = 5,
    place_label: str = ""
) -> dict[str, Any]:
    """
    Find nearby categorized spots: cafe, mountain, temple, fort, and park.
    Identifies the best nearby destination with verified images and maps navigation.
    """
    headers = {"User-Agent": USER_AGENT}
    spots_by_cat: dict[str, list[dict[str, Any]]] = {
        "cafe": [],
        "mountain": [],
        "temple": [],
        "fort": [],
        "park": []
    }
    all_spots: list[dict[str, Any]] = []
    seen_names = set()

    async with httpx.AsyncClient(timeout=6.0, headers=headers) as client:
        # 1. Wikipedia Geosearch for landmarks with photos
        wiki_spots = await fetch_wikipedia_geosearch(client, lat, lon, radius_m=radius_km * 1000)
        for s in wiki_spots:
            if s["name"].lower() not in seen_names:
                seen_names.add(s["name"].lower())
                cat = s["category"]
                spots_by_cat[cat].append(s)
                all_spots.append(s)

        # 2. Fill in cafe, mountain, temple, fort, and park via Nominatim concurrently
        tasks = []
        for cat in ["cafe", "mountain", "temple", "fort", "park"]:
            if len(spots_by_cat[cat]) < 2:
                tasks.append(fetch_nominatim_category(client, lat, lon, cat, limit=3))
        
        if tasks:
            cat_results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in cat_results:
                if isinstance(res, list):
                    for spot in res:
                        if spot["name"].lower() not in seen_names:
                            seen_names.add(spot["name"].lower())
                            cat = spot["category"]
                            spots_by_cat[cat].append(spot)
                            all_spots.append(spot)

        # 3. For any remaining empty category (e.g. fort or mountain), search Wikipedia
        missing_tasks = []
        for cat in ["fort", "mountain", "temple", "cafe"]:
            if len(spots_by_cat[cat]) == 0:
                missing_tasks.append(fetch_wiki_search_category(client, place_label, cat, lat, lon))
        if missing_tasks:
            missing_results = await asyncio.gather(*missing_tasks, return_exceptions=True)
            for m_res in missing_results:
                if isinstance(m_res, list):
                    for spot in m_res:
                        if spot["name"].lower() not in seen_names:
                            seen_names.add(spot["name"].lower())
                            cat = spot["category"]
                            spots_by_cat[cat].append(spot)
                            all_spots.append(spot)


    # 3. Determine best recommended destination
    # Filter out whole cities or regions from being the 'best destination'
    candidates = [
        s for s in all_spots
        if not any(w in s["name"].lower() for w in [
            "city", "district", "subdistrict", "constituency"
        ])
    ]
    
    # Priority: Destination with real photo and specific category (fort, temple, mountain, park)
    with_photo = [c for c in candidates if c.get("has_real_photo")]
    scenic_with_photo = [c for c in with_photo if c["category"] in ["fort", "temple", "mountain", "park"]]
    
    if scenic_with_photo:
        best_destination = scenic_with_photo[0]
    elif with_photo:
        best_destination = with_photo[0]
    elif candidates:
        best_destination = candidates[0]
    elif all_spots:
        best_destination = all_spots[0]
    else:
        # Fallback destination based on place label
        clean_label = place_label or "Local Outdoors"
        best_destination = {
            "name": f"{clean_label} Green Trail",
            "category": "park",
            "description": "Scenic local walking route with fresh air and greenery.",
            "image": CATEGORY_FALLBACK_IMAGES["park"],
            "has_real_photo": False,
            "lat": lat,
            "lon": lon,
            "maps_url": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        }

    return {
        "best_destination": best_destination,
        "categories": {
            "cafe": spots_by_cat["cafe"][:4],
            "mountain": spots_by_cat["mountain"][:4],
            "temple": spots_by_cat["temple"][:4],
            "fort": spots_by_cat["fort"][:4],
            "park": spots_by_cat["park"][:4]
        },
        "all_places": all_spots[:10]
    }

async def get_nearby_places(lat: float, lon: float, radius_m: int = 2000, limit: int = 5) -> list[dict]:
    """
    Find nearby places with images, categories, and coordinates.
    Backward compatible helper returning list of places.
    """
    try:
        res = await get_categorized_places(lat, lon, radius_km=max(1, radius_m // 1000))
        return res["all_places"][:limit]
    except Exception:
        return []
