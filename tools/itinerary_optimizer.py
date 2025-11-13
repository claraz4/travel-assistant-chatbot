from langchain.tools import tool
from typing import List, Dict, Any
import json

def load_distances(path="db_files/transit_time.json", city=None):
    """Return all distances or only those for one city."""
    with open(path, "r") as f:
        data = json.load(f)
    return data[city] if city else data

@tool
def itinerary_optimizer(city: str, attractions: List[Dict[str, Any]], daily_limit: int = 8):
    """
    Plans an optimized daily itinerary for a given city.

    Args:
        city (str): Target city for the itinerary.
        attractions (list): List of attractions, each with:
            - name (str): Attraction name.
            - duration_hr (float): Estimated time spent there.
        daily_limit (int): Specify the length of a single plan.

    Returns:
        dict: {
            "city": str,
            "ordered_itinerary": [
                {
                    "day": int,
                    "plan": [
                        {
                            "name": str,           # Attraction name
                            "duration_hr": float,  # Time spent at the attraction
                            "travel_hr": float     # Travel time from the previous attraction (0 for first stop)
                        }
                    ]
                }
            ],
            "total_travel_time_hr": float  # Total travel time across all days (in hours)
        }
    """
    if not city or not attractions:
        return {"ordered_itinerary": [], "total_travel_time_hr": 0}

    distances = load_distances(city=city)
    remaining = attractions.copy()
    current = remaining.pop(0)
    plan = [[current["name"]]]
    plan_idx = 0
    daily_time = current["duration_hr"]
    total_travel_time = 0.0

    while remaining:
        current_name = current["name"]
        # pick next closest unvisited attraction
        next_place = None
        shortest_time = float("inf")

        for candidate in remaining:
            cand_name = candidate["name"]
            travel_time = distances.get(current_name, {}).get(cand_name, float("inf"))
            if travel_time < shortest_time:
                shortest_time = travel_time
                next_place = candidate

        if next_place is None:
            break

        travel_hr = shortest_time / 60.0
        if daily_time + travel_hr + next_place["duration_hr"] > daily_limit:
            plan_idx += 1
            plan.append([])
            daily_time = 0

        # Add next attraction with travel time
        plan[plan_idx].append({
            "name": next_place["name"],
            "duration_hr": next_place["duration_hr"],
            "travel_hr": round(travel_hr, 2)
        })

        daily_time += travel_hr + next_place["duration_hr"]
        total_travel_time += travel_hr
        current = next_place
        remaining.remove(next_place)

    return {
        "city": city,
        "ordered_itinerary": [{"day": i+1, "plan": day} for i, day in enumerate(plan)],
        "total_travel_time_hr": round(total_travel_time, 2)
    }