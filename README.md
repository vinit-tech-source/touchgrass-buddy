# 🌿 TouchGrass Buddy 3.0

> **Get off your screen and go outside!**
> A local web app that generates fun, AI-powered outdoor missions using a
> **completely local, open-weight LLM** through Ollama. No cloud APIs, no API
> keys, no data leaves your machine.

---

## ✨ What's New in 3.0 (The Multi-Page Upgrade)

TouchGrass Buddy has grown from a single-page prototype into a fully fleshed-out SPA (Single Page Application)!

1. **Interactive Location Picker**: Search for any city using forward-geocoding, or use your GPS location to drop a pin on the **Leaflet map**.
2. **Deep Mission Context**: You can now define your **Energy Level**, **Group Size**, **Accessibility**, and a huge variety of **Interests**.
3. **Journaling & Stats**: View your past missions in the **Journal tab**. Progress through levels, maintain your streak, and unlock **Badges**.
4. **Robust & Resilient**: Added `tenacity` retries across the backend. If Open-Meteo or Overpass goes down, the app gracefully continues offline so you can still generate missions.
5. **Real Map Integration**: Nearby parks and nature reserves fetched from OpenStreetMap are now rendered directly onto an interactive map in your mission card.

---

## 🌍 Why Open-Source AI Matters Here

| Benefit | Details |
|---------|---------|
| **Privacy First** | Your mood, location, and **photos** never leave your computer. |
| **Works offline** | Once models are downloaded, no internet is needed for AI generation. |
| **No API cost** | Run it forever — zero recurring charges. |
| **Hackable** | Swap models, tweak prompts, add features — it's all yours. |

---

## 📋 Prerequisites

- **Python 3.10+**
- **Ollama** — [ollama.com](https://ollama.com/download)

### Install Ollama & pull the models

```bash
# Text generation model:
ollama pull llama3.2:3b

# Vision model for photo verification:
ollama pull moondream
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repo & create venv
git clone https://github.com/your-username/touchgrass-buddy.git
cd touchgrass-buddy
python -m venv venv
venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and edit .env
copy .env.example .env

# 4. Run the app
uvicorn app.main:app --reload

# 5. Open in your browser
# → http://localhost:8000
```

---

## 🏗️ Project Structure

```
touchgrass-buddy/
├── app/
│   ├── main.py          # FastAPI routes & geocoding endpoints
│   ├── ai.py            # Ollama text & vision integration
│   ├── weather.py       # Open-Meteo forward/reverse geocode & forecast
│   ├── places.py        # Overpass API for nearby parks
│   └── static/
│       └── index.html   # Complete Vue-like SPA (Vanilla JS + Leaflet)
├── tests/
├── .env.example
├── README.md
└── requirements.txt
```

---

## ⚙️ How It Works (Architecture Diagram)

```
┌─────────────┐   GET /api/geocode /reverse_geocode ┌───────────────┐
│ Browser     │ ───────────────────────────────────▸│ FastAPI       │
│ SPA (Views, │   POST /api/mission                 │ main.py       │
│ Maps, XP)   │ ───────────────────────────────────▸│               │
│             │   POST /api/verify                  │               │
│             │ ───────────────────────────────────▸│               │
└─────────────┘                                     └──────┬────────┘
                                                           │
                             ┌─────────────────────────────▼───┐
                             │       Backend Modules           │
                             │  weather.py (Open-Meteo)        │
                             │  places.py (Overpass API)       │
                             │  ai.py (Ollama Integration)     │
                             └───────────────┬─────────────────┘
                                             │
                       ┌─────────────────────┴───────────────────────┐
                       ▼                                             ▼
               Ollama (llama3.2:3b)                      Ollama (moondream)
             Generates mission JSON                    Verifies proof photos
```
