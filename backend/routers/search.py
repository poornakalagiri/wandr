from fastapi import APIRouter, Query
from typing import Optional
from data.travel_data import DESTINATIONS, ATTRACTIONS, ACCOMMODATIONS
from models.schemas import SearchRequest

router = APIRouter()

@router.post("/")
def search(payload: SearchRequest):
    q = payload.query.lower()
    dests = [d for d in DESTINATIONS if
             q in d["name"].lower() or q in d["country"].lower() or
             q in d["description"].lower() or any(q in t.lower() for t in d["tags"])]
    attrs = [a for a in ATTRACTIONS if
             q in a["name"].lower() or q in a["description"].lower() or
             any(q in t.lower() for t in a.get("tags", []))]
    if payload.continent:
        dests = [d for d in dests if payload.continent.lower() in d["continent"].lower()]
    if payload.tags:
        dests = [d for d in dests if any(t in d["tags"] for t in payload.tags)]
    return {
        "destinations": dests[:8],
        "attractions": attrs[:8],
        "total": len(dests) + len(attrs)
    }

@router.get("/suggest")
def suggest(q: str = Query("", min_length=1)):
    ql = q.lower()
    suggestions = [
        {"type": "destination", "id": d["id"], "name": d["name"],
         "subtitle": d["country"], "continent": d["continent"]}
        for d in DESTINATIONS if ql in d["name"].lower() or ql in d["country"].lower()
    ][:6]
    return {"suggestions": suggestions}

@router.get("/attractions")
def search_attractions(
    q: Optional[str] = Query(None),
    destination_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
):
    results = ATTRACTIONS
    if destination_id:
        results = [a for a in results if a["destination_id"] == destination_id]
    if type:
        results = [a for a in results if a["type"].lower() == type.lower()]
    if q:
        ql = q.lower()
        results = [a for a in results if ql in a["name"].lower() or ql in a["description"].lower()]
    return {"attractions": results, "total": len(results)}
