from langchain.tools import tool
from pathlib import Path
from difflib import get_close_matches
from typing import List, Dict, Any, Optional
import json

# ---- Load dataset once ----

DATA_PATH = Path(__file__).resolve().parents[1] / "json" / "restaurants.json"

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        _RESTAURANTS_RAW = json.load(f)
except FileNotFoundError:
    _RESTAURANTS_RAW = {}

def _norm(s: str) -> str:
    return (s or "").strip().casefold()

# city lookup with fuzzy matching
_CITY_KEYS = {_norm(city): city for city in _RESTAURANTS_RAW.keys()}

def _resolve_city(city: str) -> Optional[str]:
    if not city:
        return None
    key = _norm(city)
    if key in _CITY_KEYS:
        return _CITY_KEYS[key]
    # fuzzy fallback
    matches = get_close_matches(key, list(_CITY_KEYS.keys()), n=1, cutoff=0.6)
    if matches:
        return _CITY_KEYS[matches[0]]
    return None

def _score_restaurant(
    r: Dict[str, Any],
    budget: Optional[str],
    diet: Optional[str],
    cuisines: Optional[List[str]],
    near_attraction: Optional[str],
) -> float:
    score = 0.0

    # normalize inputs
    budget = _norm(budget) if budget else None
    diet = _norm(diet) if diet else None
    cuisines = [_norm(c) for c in cuisines] if cuisines else []

    r_budget = _norm(r.get("budget", ""))
    r_diets = [_norm(d) for d in r.get("diet_options", [])]
    r_cuisines = [_norm(c) for c in r.get("cuisines", [])]
    r_near = [_norm(a) for a in r.get("nearby_attractions", [])]

    # budget match
    if budget and r_budget:
        if r_budget == budget:
            score += 2.0
        elif (budget == "low" and r_budget == "medium") or (budget == "high" and r_budget == "medium"):
            score += 0.5  # close enough

    # diet match
    if diet:
        if diet in r_diets:
            score += 2.0
        # "vegan" satisfied by "vegan-friendly"
        if diet == "vegan" and "vegan-friendly" in r_diets:
            score += 1.0

    # cuisine overlap
    if cuisines:
        matches = len(set(cuisines) & set(r_cuisines))
        score += matches * 1.5

    # proximity to attraction
    if near_attraction:
        na = _norm(near_attraction)
        if na in r_near:
            score += 3.0

    # small base score so unfiltered results don't all look equal
    return score + 1.0


@tool
def restaurant_matcher(
    city: str,
    budget: str = "medium",
    diet: str = "",
    cuisines: Optional[List[str]] = None,
    near_attraction: str = "",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Match restaurants / local food spots in a given city.

    Args:
        city: City name (e.g. "Rome", "Tokyo").
        budget: One of: "low", "medium", "high". (Heuristic, not exact prices.)
        diet: Optional dietary preference, e.g. "vegetarian", "vegan", "halal", "".
        cuisines: Optional list of desired cuisines, e.g. ["italian", "seafood"].
        near_attraction: Optional attraction name; prioritize places close to it.
        limit: Maximum number of results to return.

    Returns:
        List of restaurant dicts sorted by match score, each containing:
            - name
            - city
            - cuisines
            - budget
            - diet_options
            - area
            - nearby_attractions
            - notes
            - match_score (float)
    """
    resolved_city = _resolve_city(city)
    if not resolved_city:
        return []

    city_list = _RESTAURANTS_RAW.get(resolved_city, [])
    if not city_list:
        return []

    # compute scores and sort
    scored: List[Dict[str, Any]] = []
    for r in city_list:
        s = _score_restaurant(r, budget, diet, cuisines, near_attraction)
        item = {
            "name": r.get("name"),
            "city": resolved_city,
            "cuisines": r.get("cuisines", []),
            "budget": r.get("budget", ""),
            "diet_options": r.get("diet_options", []),
            "area": r.get("area", ""),
            "nearby_attractions": r.get("nearby_attractions", []),
            "notes": r.get("notes", ""),
            "match_score": round(s, 2),
        }
        scored.append(item)

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[: max(1, limit)]
