from langchain.tools import tool
from pathlib import Path
from difflib import get_close_matches
from typing import List, Dict, Any, Optional
import json

# ---- Load dataset once ----

DATA_PATH = Path(__file__).resolve().parents[1] / "json" / "hotels.json"

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        _HOTELS_RAW = json.load(f)
except FileNotFoundError:
    _HOTELS_RAW = {}

def _norm(s: str) -> str:
    return (s or "").strip().casefold()

# Build normalized city lookup (supports fuzzy)
_CITY_KEYS = {_norm(city): city for city in _HOTELS_RAW.keys()}

def _resolve_city(city: str) -> Optional[str]:
    if not city:
        return None
    key = _norm(city)
    if key in _CITY_KEYS:
        return _CITY_KEYS[key]
    matches = get_close_matches(key, list(_CITY_KEYS.keys()), n=1, cutoff=0.6)
    if matches:
        return _CITY_KEYS[matches[0]]
    return None

def _normalize_trip_type(trip_type: str) -> str:
    t = (trip_type or "").strip().lower()
    mapping = {
        "solo": "solo",
        "single": "solo",
        "couple": "couple",
        "romantic": "couple",
        "honeymoon": "couple",
        "family": "family",
        "kids": "family",
        "business": "business",
        "work": "business"
    }
    return mapping.get(t, "any")

def _score_hotel(
    h: Dict[str, Any],
    budget: Optional[str],
    min_stars: int,
    trip_type: str,
    amenities: Optional[List[str]],
    near_attraction: Optional[str],
) -> float:
    score = 0.0

    # normalize inputs
    budget = _norm(budget) if budget else None
    tt = _normalize_trip_type(trip_type)
    amenities = [_norm(a) for a in amenities] if amenities else []
    near_attraction = _norm(near_attraction) if near_attraction else None

    h_budget = _norm(h.get("budget", ""))
    h_stars = int(h.get("stars", 0) or 0)
    h_amenities = [_norm(a) for a in h.get("amenities", [])]
    h_near = [_norm(a) for a in h.get("nearby_attractions", [])]
    family_friendly = bool(h.get("family_friendly", False))
    style = _norm(h.get("style", ""))

    # --- stars ---
    if h_stars >= min_stars:
        score += (h_stars - min_stars + 1) * 1.2
    else:
        # heavily de-prioritize if under requested min
        score -= 3.0

    # --- budget match ---
    if budget and h_budget:
        if h_budget == budget:
            score += 2.0
        elif (budget == "low" and h_budget == "medium") or (budget == "high" and h_budget == "medium"):
            score += 0.5  # close enough

    # --- trip type logic ---
    if tt == "family":
        if family_friendly:
            score += 2.0
        if "family_rooms" in h_amenities or "kitchenette" in h_amenities:
            score += 1.0
    elif tt == "couple":
        if style in {"boutique", "luxury"}:
            score += 2.0
        if "rooftop_terrace" in h_amenities or "spa" in h_amenities:
            score += 1.0
    elif tt == "business":
        if style in {"business"} or "meeting_rooms" in h_amenities:
            score += 2.0
        if "wifi" in h_amenities and "desk" in h_amenities:
            score += 0.5
    elif tt == "solo":
        if style in {"hostel", "capsule", "pod_hotel"}:
            score += 1.5

    # --- amenity overlap ---
    if amenities:
        matches = len(set(amenities) & set(h_amenities))
        score += matches * 1.5

    # --- proximity to attraction ---
    if near_attraction:
        if near_attraction in h_near:
            score += 3.0

    # small base score so "okay" options don't get stuck at 0
    return score + 1.0


@tool
def hotel_matcher(
    city: str,
    budget: str = "medium",
    min_stars: int = 0,
    trip_type: str = "any",
    amenities: Optional[List[str]] = None,
    near_attraction: str = "",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Match hotels in a given city.

    Args:
        city: City name (e.g. "Rome", "Tokyo").
        budget: "low", "medium", or "high". This is approximate, not real prices.
        min_stars: Minimum acceptable hotel star rating (0–5).
        trip_type: "solo", "couple", "family", "business", or "any".
        amenities: Optional list of desired amenities (e.g. ["wifi", "pool", "breakfast"]).
        near_attraction: Optional attraction name; prioritize hotels close to it.
        limit: Max number of hotels to return.

    Returns:
        A list of hotel dicts sorted by match_score, each including:
          - name
          - city
          - stars
          - budget
          - area
          - nearby_attractions
          - amenities
          - style
          - family_friendly
          - notes
          - match_score (float)
    """
    resolved_city = _resolve_city(city)
    if not resolved_city:
        return []

    city_hotels = _HOTELS_RAW.get(resolved_city, [])
    if not city_hotels:
        return []

    scored: List[Dict[str, Any]] = []
    for h in city_hotels:
        s = _score_hotel(h, budget, min_stars, trip_type, amenities, near_attraction)
        item = {
            "name": h.get("name"),
            "city": resolved_city,
            "stars": h.get("stars", 0),
            "budget": h.get("budget", ""),
            "area": h.get("area", ""),
            "nearby_attractions": h.get("nearby_attractions", []),
            "amenities": h.get("amenities", []),
            "style": h.get("style", ""),
            "family_friendly": h.get("family_friendly", False),
            "notes": h.get("notes", ""),
            "match_score": round(s, 2),
        }
        scored.append(item)

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[: max(1, limit)]
