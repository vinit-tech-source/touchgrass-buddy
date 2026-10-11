<div align="center">

# 🌿 TouchGrass Buddy 3.0
### The Local-First Outdoor Companion & Gamified Field Journal

*Reduce screen time, reconnect with nature, and explore the real world through AI-powered physical missions.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![PWA Ready](https://img.shields.io/badge/PWA-Installable-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Zero Cloud Costs](https://img.shields.io/badge/%240.00-Zero%20API%20Costs-22C55E?style=for-the-badge)](https://github.com/vinit-tech-source/touchgrass-buddy)

</div>

---

## 📖 Overview

**TouchGrass Buddy** is a privacy-first Single-Page Application (SPA) designed to solve modern screen fatigue. Instead of just telling you to take a break, it generates **context-aware outdoor micro-adventures** tailored to your exact neighborhood, current live weather, energy level, and personal interests.

Every aspect of the application runs **100% locally on your computer**:
* **Zero Cloud AI API Billing:** Driven entirely by local open-weight models via **Ollama** (`llama3.2:3b` for mission generation and `moondream` for photo verification).
* **Total Privacy:** Your GPS coordinates, health energy levels, personal journal logs, and camera photos never leave your device.
* **Modern Outdoor Field Journal UI:** An organic, forest-night design aesthetic (AllTrails meets Duolingo) built with high-performance Vanilla JavaScript, CSS custom properties, and Leaflet maps.

---

## ✨ Key Features in Version 3.0

### 🗺️ 1. Guided 3-Step Mission Planner
* **Step 1 — Smart Location Detection:** Detect your exact GPS coordinates with one click (`[ ⌖ Use My Location ]`) or search for any neighborhood/city globally. Integrated with OpenStreetMap and Leaflet.
* **Step 2 — Mood & Energy Customization:** Tailor adventures based on available time (10–120 mins), energy level (*Low Key, Moderate, Energetic, Trail Runner*), group size (*Solo, Pair, Dog, Kids*), and accessibility requirements.
* **Step 3 — Interests & AI Generation:** Pick interests (Parks, Botany, History, Cafes, Photography, Meditation) and generate missions with real-time weather integration (temperature, rain chance, sunrise/sunset).

### 📍 2. Curated Destinations with Real Photos
* **Top Recommended Spot:** Step 1 of your mission points directly to the best nearby outdoor destination near you (e.g., *"Walk towards Forest Park"*).
* **Rich Visual Discovery:** Automatically fetches high-resolution photos via Wikipedia Commons and OpenStreetMap.
* **Turn-by-Turn Navigation:** One-tap *"Get Directions"* links directly into Google Maps from your current GPS pin.
* **Categorized Discovery:** Instant search filters for:
  * ☕ **Cafes & Coffee Spots**
  * ⛰️ **Mountains, Hills & Peaks**
  * 🛕 **Temples, Shrines & Sacred Spaces**
  * 🏰 **Forts, Monuments & Heritage Sites**
  * 🌳 **Parks, Forests & Nature Reserves**

### 📜 3. Persistent Field Journal & Saved Plans
* **Plan History:** Every generated excursion is automatically archived into your Field Journal. Re-open, review, or resume past plans at any time with a single tap.
* **Mission Proof Verification:** Complete your mini-photo challenge (e.g., photographing a unique leaf or landmark) and verify it using the local vision model (`moondream`) or camera upload.
* **Journal Entries:** Record your thoughts, reflections, and outdoor notes for every excursion.

### 🏆 4. Gamified Progression System
* **XP & Leveling:** Earn Experience Points (XP) for generating plans, completing outdoor walks, verifying photo challenges, and logging journal entries.
* **Streaks & Multipliers:** Maintain daily outdoor streaks to unlock streak badges.
* **Achievement Badges:** Unlock achievements like *First Step*, *Weekend Wanderer*, *Tree Whisperer*, *Rainwalker*, and *Night Owl*.

### 📱 5. PWA (Progressive Web App) & Offline Ready
* **Installable:** Add directly to home screen on iOS, Android, macOS, and Windows with a native app feel.
* **Service Worker:** Offline caching for fast loading even when cellular connection is spotty.

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TOUCHGRASS BUDDY CLIENT                         │
│   (Vanilla JS SPA • Leaflet Maps • LocalStorage • Service Worker PWA)  │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ HTTP REST
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND (main.py)                         │
│  ├── /api/weather            ──► Open-Meteo API (Forecast & Sunrise)   │
│  ├── /api/geocode            ──► OpenStreetMap Nominatim / Photon      │
│  ├── /api/places             ──► OSM Overpass & Wikipedia Commons      │
│  ├── /api/categorized_places ──► Multi-Category Spatial Discovery      │
│  └── /api/mission & /verify  ──► Local Ollama LLM Services             │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ Local Loopback (Port 11434)
                  ┌──────────────────┴──────────────────┐
                  ▼                                     ▼
      ┌───────────────────────┐             ┌───────────────────────┐
      │  Ollama (llama3.2:3b) │             │   Ollama (moondream)  │
      │  Mission Text & Logic │             │   Vision Photo Judge  │
      └───────────────────────┘             └───────────────────────┘
```

---

## 🚀 Getting Started

### 1. Prerequisites
* **Python 3.10+**
* **Ollama:** Download and install from [ollama.com](https://ollama.com)

Pull the local AI models (one-time download, completely free):
```bash
# Text generation model (~2.0 GB):
ollama pull llama3.2:3b

# Vision model for photo challenge verification (~1.7 GB, optional):
ollama pull moondream
```

### 2. Clone & Setup Repository
```bash
# Clone the repository
git clone https://github.com/vinit-tech-source/touchgrass-buddy.git
cd touchgrass-buddy

# Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the sample environment file:
```bash
# Windows:
copy .env.example .env

# macOS / Linux:
cp .env.example .env
```

Default `.env` configuration:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_VISION_MODEL=moondream
PORT=8000
HOST=127.0.0.1
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser at **[http://localhost:8000](http://localhost:8000)**.

---

## 🧪 Running Automated Tests

TouchGrass Buddy includes unit and integration tests covering the AI engine, weather service, spatial geocoding, categorized places, and mission schemas.

```bash
# Run the complete test suite
pytest -v
```

---

## 📁 Repository Structure

```
touchgrass-buddy/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application, CORS, routers & geocoding
│   ├── ai.py                # Ollama prompt engineering, JSON schema validator & vision judge
│   ├── places.py            # OpenStreetMap Overpass, Wikipedia geo-search & photo resolvers
│   ├── weather.py           # Open-Meteo weather forecast & daylight calculation
│   └── static/
│       ├── index.html       # Single Page Application (UI layout, CSS tokens & client logic)
│       ├── manifest.json    # Progressive Web App manifest
│       ├── sw.js            # PWA Service Worker caching
│       ├── icon.svg         # SVG app icon
│       └── *.jpg            # Optimized hero background assets
├── tests/
│   ├── __init__.py
│   ├── test_ai.py           # Ollama prompt building & fallback mission tests
│   ├── test_places.py       # Nearby places & photo URL resolver tests
│   ├── test_v3_features.py  # Health check & categorized places endpoint tests
│   └── test_weather.py      # Weather formatters & WMO code tests
├── .env.example             # Template environment variables
├── .gitignore               # Ignored cache, virtual envs, and large media files
├── LICENSE                  # MIT License
├── README.md                # Project documentation
└── requirements.txt         # Production Python dependencies
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/health` | `GET` | Verifies server and local Ollama connectivity status |
| `/api/weather` | `GET` | Fetches live temperature, rain probability, wind, and sunrise/sunset |
| `/api/geocode` | `GET` | Forward geocodes city or address name to coordinates |
| `/api/reverse_geocode` | `GET` | Reverse geocodes latitude/longitude into human-readable city/suburb |
| `/api/places` | `GET` | Retrieves nearby parks and green spaces within radius |
| `/api/categorized_places` | `GET` | Finds nearby cafes, mountains, temples, forts, and nature spots with photos |
| `/api/mission` | `POST` | Generates a structured outdoor adventure using local Ollama model |
| `/api/verify` | `POST` | Validates user mission photos with local vision AI model |

---

## 🔒 Privacy & Local-First Philosophy

* **No tracking:** Zero analytics scripts, tracking cookies, or third-party advertising SDKs.
* **No cloud AI lock-in:** No OpenAI, Claude, or Gemini API keys required. All inference happens on your local GPU/CPU.
* **Client-side storage:** Your journal logs, photos, stats, and completed missions live in your browser's `localStorage` and never sync to any external server without your explicit command.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
