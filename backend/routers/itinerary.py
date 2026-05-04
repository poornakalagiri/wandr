from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from models.orm import User
from models.schemas import ItineraryRequest
from services.auth import get_optional_user
from data.travel_data import DESTINATIONS, ATTRACTIONS, ACCOMMODATIONS

router = APIRouter()

INTEREST_TAG_MAP = {
    "culture": ["culture","cultural","art","music","theatre"],
    "food": ["food","cuisine","street food","gastronomy"],
    "history": ["history","historic","ancient","UNESCO","ruins"],
    "nature": ["nature","outdoor","hiking","scenic","wildlife"],
    "adventure": ["adventure","trekking","diving","bungee","safari"],
    "beach": ["beach","island","coastal","surf","snorkelling"],
    "art": ["art","museum","gallery","impressionism","renaissance"],
    "spiritual": ["temple","shrine","religious","spiritual","sacred"],
    "nightlife": ["nightlife","bar","club","party"],
    "shopping": ["shopping","market","bazaar","souk"],
    "luxury": ["luxury","spa","overwater","fine dining"],
    "affordable": ["free","affordable","budget","local"],
}

def score_attraction(attr, interests, budget_tier):
    score = attr["rating"] * 10
    for interest in interests:
        mapped_tags = INTEREST_TAG_MAP.get(interest, [interest])
        for tag in attr.get("tags", []):
            if any(t.lower() in tag.lower() or tag.lower() in t.lower() for t in mapped_tags):
                score += 12
    cost = attr.get("cost", {}).get(budget_tier, 0)
    if budget_tier == "budget" and cost <= 15:
        score += 8
    elif budget_tier == "luxury" and attr["rating"] >= 4.7:
        score += 8
    if "free" in attr.get("tags", []) or "free" in attr.get("description", "").lower():
        if budget_tier == "budget":
            score += 10
    return score

def generate_checklist(dest, request: ItineraryRequest):
    return {
        "📄 Documents": [
            "Valid passport (6+ months validity)",
            f"Visa / entry: {dest['visa_info']}",
            "Travel insurance",
            "Flight & hotel confirmations",
            "Emergency contact list",
            "Photocopies of all documents"
        ],
        "💊 Health & Safety": [
            "Prescription medications (extra supply)",
            "First aid kit",
            "Sunscreen & insect repellent",
            "Travel vaccinations (check requirements)",
            "Health insurance card / EHIC",
            "Hand sanitiser & masks"
        ],
        "💰 Money": [
            f"{dest['currency']} local currency or notify bank",
            "Credit/debit cards (notify your bank)",
            "Emergency cash reserve (USD/EUR)",
            "Budget tracking app",
            "Know ATM locations at destination"
        ],
        "🧳 Packing": [
            "Weather-appropriate clothing",
            "Comfortable walking shoes",
            "Universal power adapter",
            "Portable charger / power bank",
            "Reusable water bottle",
            "Day backpack",
            "Laundry bag"
        ],
        "📱 Digital": [
            "Offline maps downloaded (Google Maps)",
            "Translation app (Google Translate)",
            f"Local emergency numbers saved ({dest['country']})",
            "Hotel address in local language",
            "Photos backup (Google Photos / iCloud)",
            "VPN app (if needed)"
        ],
        "✈️ Pre-Departure": [
            "Check-in for flight (24h before)",
            "Confirm accommodation booking",
            "Arrange airport transfer",
            f"Check weather: {dest['best_season']}",
            "Notify someone of your itinerary"
        ]
    } | ({"♿ Accessibility": [
        "Confirm wheelchair accessibility at all attractions",
        "Book accessible accommodation (ground floor / lift)",
        "Research accessible transport options",
        "Contact airlines for assistance (min. 48h notice)",
        "Download accessibility maps / apps"
    ]} if request.accessibility_needs else {})

@router.post("/generate")
def generate_itinerary(request: ItineraryRequest, current_user: Optional[User] = Depends(get_optional_user)):
    dest = next((d for d in DESTINATIONS if d["id"] == request.destination_id), None)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    dest_attrs = [a for a in ATTRACTIONS if a["destination_id"] == request.destination_id]
    if not dest_attrs:
        raise HTTPException(status_code=404, detail="No attractions found for this destination")

    scored = sorted(dest_attrs, key=lambda a: score_attraction(a, request.interests, request.budget_tier), reverse=True)

    DAILY_HOURS = 8
    days = []
    used = set()

    for day_num in range(1, request.duration_days + 1):
        day_attrs, hours_used, day_cost = [], 0, 0
        for attr in scored:
            if attr["id"] in used:
                continue
            dur = attr.get("duration_hours", 2)
            if hours_used + dur <= DAILY_HOURS:
                day_attrs.append(attr)
                hours_used += dur
                day_cost += attr.get("cost", {}).get(request.budget_tier, 0)
                used.add(attr["id"])
        # If we run out of unique attractions, recycle top ones
        if not day_attrs:
            day_attrs = [scored[day_num % len(scored)]]
            day_cost = day_attrs[0].get("cost", {}).get(request.budget_tier, 0)

        days.append({
            "day": day_num,
            "title": f"Day {day_num} — {dest['name']}",
            "attractions": day_attrs,
            "estimated_cost_per_person": round(day_cost, 2),
            "hours_planned": round(hours_used, 1)
        })

    # Accommodation
    accs = [a for a in ACCOMMODATIONS if a["destination_id"] == request.destination_id and a["tier"] == request.budget_tier]
    accommodation = accs[0] if accs else None

    # Budget breakdown
    daily_budget   = dest["budget_per_day"].get(request.budget_tier, 150)
    attr_cost      = sum(d["estimated_cost_per_person"] for d in days) * request.travelers
    acc_cost       = (accommodation["price_per_night"] if accommodation else daily_budget * 0.5) * request.duration_days * request.travelers
    food_misc      = daily_budget * 0.35 * request.duration_days * request.travelers
    grand_total    = round(attr_cost + acc_cost + food_misc, 2)

    return {
        "destination": dest,
        "duration_days": request.duration_days,
        "budget_tier": request.budget_tier,
        "travelers": request.travelers,
        "interests": request.interests,
        "itinerary": days,
        "accommodation": accommodation,
        "budget_summary": {
            "accommodation_total": round(acc_cost, 2),
            "attractions_total":   round(attr_cost, 2),
            "food_misc_total":     round(food_misc, 2),
            "grand_total":         grand_total,
            "per_person":          round(grand_total / request.travelers, 2),
            "daily_average":       round(grand_total / request.duration_days / request.travelers, 2),
            "currency":            "USD"
        },
        "checklist": generate_checklist(dest, request),
        "map_data": {
            "center": {"lat": dest["lat"], "lng": dest["lng"]},
            "zoom": 12,
            "markers": [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "lat": a["lat"],
                    "lng": a["lng"],
                    "day": d["day"],
                    "type": a["type"]
                }
                for d in days for a in d["attractions"]
            ]
        }
    }

@router.get("/destinations/{destination_id}/sample")
def sample_itinerary(destination_id: str, budget_tier: str = "mid", duration_days: int = 3):
    req = ItineraryRequest(
        destination_id=destination_id,
        duration_days=duration_days,
        budget_tier=budget_tier,
        travelers=2
    )
    return generate_itinerary(req, None)
