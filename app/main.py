"""
main.py — FastAPI application for TouchGrass Buddy V3.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.ai import generate_mission, check_ollama_health, verify_photo, OLLAMA_VISION_MODEL
from app.weather import get_weather, forward_geocode, reverse_geocode
from app.places import get_nearby_places

app = FastAPI(
    title="TouchGrass Buddy",
    description="Get off your screen and go outside! 🌿",
    version="3.0.0",
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ─── Models ────────────────────────────────────────────────────────────

class MissionRequest(BaseModel):
    lat: float
    lon: float
    place_label: str = Field(..., min_length=1)
    time_min: int = Field(..., ge=5, le=120)
    mood: str
    energy: str
    group: str
    accessibility: str
    interests: list[str] = Field(default_factory=list)
    radius_km: int = Field(default=2, ge=1, le=20)
    custom_notes: str | None = Field(default=None, max_length=500)

class MissionResponse(BaseModel):
    title: str
    steps: list[str]
    mini_challenge: str
    safety_tip: str
    duration_min: int
    weather_description: str
    city: str
    temperature_c: float
    rain_chance: int
    places: list[dict]
    is_day: bool

class VerifyRequest(BaseModel):
    image_base64: str
    challenge: str

class VerifyResponse(BaseModel):
    verified: bool
    confidence: int
    comment: str

# ─── Routes ────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/geocode")
async def api_geocode(q: str = Query(..., min_length=2)):
    """Search for locations by name (Open-Meteo)."""
    try:
        results = await forward_geocode(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service failed: {e}")

@app.get("/api/reverse_geocode")
async def api_reverse_geocode(lat: float, lon: float):
    """Get friendly name for coordinates (Nominatim)."""
    try:
        result = await reverse_geocode(lat, lon)
        return result
    except Exception as e:
        # Fallback if Nominatim is rate-limiting or down
        return {"name": "Current Location", "display_name": f"Lat {lat:.2f}, Lon {lon:.2f}"}

@app.post("/api/mission", response_model=MissionResponse)
async def create_mission(req: MissionRequest) -> MissionResponse:
    # 1. Fetch Weather (graceful fallback)
    try:
        weather = await get_weather(req.lat, req.lon)
    except Exception:
        weather = None

    # 2. Fetch Places (graceful fallback inside the function)
    places = await get_nearby_places(req.lat, req.lon, radius_m=req.radius_km * 1000, limit=5)

    # 3. Generate Mission
    mission = await generate_mission(
        weather=weather,
        place_label=req.place_label,
        time_min=req.time_min,
        mood=req.mood,
        energy=req.energy,
        group=req.group,
        accessibility=req.accessibility,
        interests=req.interests,
        places=places,
        custom_notes=req.custom_notes
    )

    return MissionResponse(
        title=mission["title"],
        steps=mission["steps"],
        mini_challenge=mission["mini_challenge"],
        safety_tip=mission["safety_tip"],
        duration_min=mission["duration_min"],
        weather_description=weather.description if weather else "Unknown",
        city=req.place_label,
        temperature_c=weather.temperature_c if weather else 20.0,
        rain_chance=weather.rain_chance if weather else 0,
        places=places,
        is_day=weather.is_day if weather else True
    )

@app.post("/api/verify", response_model=VerifyResponse)
async def verify_photo_endpoint(req: VerifyRequest) -> VerifyResponse:
    b64_data = req.image_base64
    if "," in b64_data:
        b64_data = b64_data.split(",")[1]
        
    try:
        result = await verify_photo(b64_data, req.challenge)
        return VerifyResponse(**result)
    except ValueError as e:
        if "missing" in str(e).lower():
            raise HTTPException(
                status_code=503, 
                detail=f"Vision model missing. Run: ollama pull {OLLAMA_VISION_MODEL}"
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error verifying photo.")

@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    status = await check_ollama_health()
    return {
        "status": "ok" if status["model_available"] else "degraded",
        **status,
    }
