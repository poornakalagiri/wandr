# 🌍 Wandr — Intelligent Travel Planning Agent
### Project 26 — Full Stack Submission

---

## ✅ What's Delivered

| Requirement | Status | Details |
|-------------|--------|---------|
| 10+ destinations | ✅ **50 destinations** | All 6 continents |
| 10+ attractions | ✅ **100+ attractions** | GPS, costs, ratings |
| Multiple budget tiers | ✅ **3 tiers** | Budget / Mid / Luxury |
| Itinerary generation | ✅ AI-optimized | Multi-constraint scoring |
| Map visualizations | ✅ Leaflet.js | Interactive, day-coded |
| Accommodation recs | ✅ **90+ hotels** | All tiers, all destinations |
| User accounts | ✅ JWT auth | Register, login, profile |
| Saved trips | ✅ PostgreSQL | Save, view, delete |
| Reviews | ✅ Endpoints ready | Per destination/attraction |
| Docker deployment | ✅ docker-compose | 1-command start |

---

## 🏗️ Architecture

```
wandr/
├── frontend/
│   └── index.html          ← Complete SPA (no build needed)
│                             HTML + CSS + Vanilla JS + Leaflet Maps
│
├── backend/                ← FastAPI Python Backend
│   ├── main.py             ← App entry point + CORS
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example        ← Copy to .env
│   │
│   ├── db/
│   │   └── database.py     ← PostgreSQL (SQLAlchemy) + MongoDB (Motor)
│   │
│   ├── models/
│   │   ├── orm.py          ← SQLAlchemy ORM: User, SavedTrip, Review
│   │   └── schemas.py      ← Pydantic request/response schemas
│   │
│   ├── routers/
│   │   ├── auth.py         ← POST /register, /login, GET /me
│   │   ├── destinations.py ← GET /destinations, /{id}/overview
│   │   ├── itinerary.py    ← POST /generate (AI engine)
│   │   ├── search.py       ← POST /search, GET /suggest
│   │   ├── trips.py        ← CRUD saved trips (auth required)
│   │   └── reviews.py      ← CRUD reviews
│   │
│   ├── services/
│   │   └── auth.py         ← JWT + bcrypt password hashing
│   │
│   └── data/
│       └── travel_data.py  ← 50 destinations, 100+ attractions, 90+ hotels
│
└── docker-compose.yml      ← PostgreSQL + MongoDB + Backend + Frontend
```

---

## 🚀 How to Run

### Option 1 — Instant (No Server Needed)
```bash
# Just open in any browser:
open frontend/index.html
```
The frontend works completely standalone with all data embedded.

### Option 2 — Docker (Full Stack with DB)
```bash
# 1. Clone / unzip the project
# 2. Run:
docker-compose up --build

# Access:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

### Option 3 — Manual
```bash
# Backend
cd backend
cp .env.example .env          # edit DB credentials
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (any static server)
cd frontend
python -m http.server 3000
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login, get JWT |
| GET  | `/api/auth/me` | Get current user |

### Destinations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/destinations/` | All 50 destinations |
| GET | `/api/destinations/{id}` | Destination detail |
| GET | `/api/destinations/{id}/overview?budget_tier=mid` | With attractions & hotels |

### Itinerary (AI Engine)
```
POST /api/itinerary/generate
{
  "destination_id": "cappadocia",
  "duration_days": 4,
  "budget_tier": "mid",
  "interests": ["adventure", "history", "nature"],
  "travelers": 2,
  "accessibility_needs": false
}
```

### Search
```
POST /api/search/
{ "query": "beach luxury diving", "continent": "Asia" }

GET /api/search/suggest?q=par
```

### Saved Trips (Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/trips/` | My saved trips |
| POST | `/api/trips/` | Save a trip |
| DELETE | `/api/trips/{id}` | Delete a trip |

---

## 🧠 AI Itinerary Algorithm

```python
def score_attraction(attr, interests, budget_tier):
    score = attr["rating"] * 10          # Base score

    for interest in interests:
        if interest matches attr tags:
            score += 12                  # Interest bonus

    if budget == "budget" and cost == 0:
        score += 10                      # Free attraction bonus

    if budget == "luxury" and rating >= 4.7:
        score += 8                       # Luxury quality bonus

    return score

# Greedy day-filling: max 8 hours/day
# Sort by score → fill each day with highest-scored unused attractions
```

---

## 🌍 Destinations Covered (50 total)

**Europe (10):** Paris · Rome · Barcelona · Amsterdam · London · Prague · Santorini · Lisbon · Florence · Reykjavik

**Asia (10):** Tokyo · Kyoto · Bali · Bangkok · Singapore · Maldives · Seoul · Hanoi · Mumbai · Angkor Wat

**Middle East (3):** Dubai · Istanbul · Petra

**Africa (4):** Cape Town · Marrakech · Cairo · Masai Mara

**Americas (6):** New York City · Rio de Janeiro · Mexico City · Buenos Aires · Machu Picchu · Galápagos

**Oceania (3):** Sydney · Queenstown · Hawaii

**+ More:** Cappadocia · Patagonia · Cinque Terre · Amalfi Coast · Taj Mahal · Cartagena · Budapest · Phuket

---

## 🗃️ Database Schema

### PostgreSQL (Relational)
```sql
users        — id, email, username, hashed_password, full_name, avatar_url
saved_trips  — id, user_id, destination_id, duration_days, budget_tier, itinerary_data (JSONB)
reviews      — id, user_id, destination_id, attraction_id, rating, title, body
```

### MongoDB (Flexible / Document)
```
destinations  — full destination documents (flexible schema)
attractions   — attraction documents with tags, coordinates, costs
itineraries   — cached generated itineraries
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3 (custom design system), Vanilla JS |
| Maps | Leaflet.js (OpenStreetMap tiles) |
| Backend | Python 3.11 + FastAPI |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Relational DB | PostgreSQL 15 + SQLAlchemy ORM |
| Document DB | MongoDB 7 + Motor (async) |
| Deployment | Docker + Docker Compose + Nginx |
| API Docs | Swagger UI at `/docs` |

---

*Built for Project 26 — Intelligent Travel Planning & Guide Agent*
