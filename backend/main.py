from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.database import Base, engine
from routers import auth, destinations, itinerary, search, trips, reviews

# Create all PostgreSQL tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Wandr — Intelligent Travel Planning Agent API",
    description="""
## 🌍 Wandr Travel API

AI-powered travel planning system with:
- **50 destinations** across 6 continents
- **100+ attractions** with ratings, costs & GPS coordinates
- **Multi-constraint itinerary optimization** (budget × interests × duration × accessibility)
- **User authentication** with JWT
- **Saved trips** & reviews
- **Interactive map data** for Leaflet.js / Google Maps

### Budget Tiers
| Tier | Description |
|------|-------------|
| `budget` | Hostels, free attractions, street food |
| `mid` | 3–4★ hotels, mixed attractions, restaurants |
| `luxury` | 5★ resorts, premium experiences, fine dining |
    """,
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,         prefix="/api/auth",         tags=["Authentication"])
app.include_router(destinations.router, prefix="/api/destinations",  tags=["Destinations"])
app.include_router(itinerary.router,    prefix="/api/itinerary",     tags=["Itinerary"])
app.include_router(search.router,       prefix="/api/search",        tags=["Search"])
app.include_router(trips.router,        prefix="/api/trips",         tags=["Saved Trips"])
app.include_router(reviews.router,      prefix="/api/reviews",       tags=["Reviews"])

@app.get("/", tags=["Health"])
def root():
    return {
        "app": "Wandr Travel Planning Agent",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "operational",
        "coverage": {
            "destinations": 50,
            "attractions": "100+",
            "accommodations": "90+",
            "budget_tiers": ["budget", "mid", "luxury"]
        }
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
