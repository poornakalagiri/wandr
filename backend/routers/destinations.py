from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from db.database import get_mongo
from data.travel_data import DESTINATIONS, ATTRACTIONS, ACCOMMODATIONS

router = APIRouter()

@router.get("/")
async def get_destinations(
    continent: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    results = DESTINATIONS
    if continent:
        results = [d for d in results if continent.lower() in d["continent"].lower()]
    if tag:
        results = [d for d in results if tag.lower() in [t.lower() for t in d["tags"]]]
    if q:
        ql = q.lower()
        results = [d for d in results if ql in d["name"].lower() or ql in d["country"].lower()
                   or ql in d["description"].lower() or any(ql in t.lower() for t in d["tags"])]
    return {"destinations": results[:limit], "total": len(results)}

@router.get("/continents")
async def get_continents():
    continents = sorted(set(d["continent"] for d in DESTINATIONS))
    return {"continents": continents}

@router.get("/{destination_id}")
async def get_destination(destination_id: str):
    dest = next((d for d in DESTINATIONS if d["id"] == destination_id), None)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest

@router.get("/{destination_id}/overview")
async def get_overview(destination_id: str, budget_tier: str = "mid"):
    dest = next((d for d in DESTINATIONS if d["id"] == destination_id), None)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    attrs = [a for a in ATTRACTIONS if a["destination_id"] == destination_id]
    accs  = [a for a in ACCOMMODATIONS if a["destination_id"] == destination_id and a["tier"] == budget_tier]
    return {
        "destination": dest,
        "attractions": attrs,
        "accommodations": accs,
        "budget_per_day": dest["budget_per_day"].get(budget_tier, 150)
    }

@router.get("/{destination_id}/attractions")
async def get_dest_attractions(destination_id: str, type: Optional[str] = None):
    attrs = [a for a in ATTRACTIONS if a["destination_id"] == destination_id]
    if type:
        attrs = [a for a in attrs if a["type"].lower() == type.lower()]
    return {"attractions": attrs, "total": len(attrs)}

@router.get("/{destination_id}/accommodations")
async def get_dest_accommodations(destination_id: str, tier: Optional[str] = None):
    accs = [a for a in ACCOMMODATIONS if a["destination_id"] == destination_id]
    if tier:
        accs = [a for a in accs if a["tier"].lower() == tier.lower()]
    return {"accommodations": accs, "total": len(accs)}
