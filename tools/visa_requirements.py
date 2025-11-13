# tools/visa_requirements.py
from langchain.tools import tool
from pathlib import Path
from difflib import get_close_matches
from datetime import datetime, timedelta
import json

# === Load main dataset ===
DATA_PATH = Path(__file__).resolve().parents[1] / "json" / "visa.json"
with open(DATA_PATH, "r", encoding="utf-8") as f:
    _DATA = json.load(f)

_PASSPORT = _DATA.get("passport_country", "Unknown")
_LAST_UPDATED = _DATA.get("last_updated", "Unknown")
_POLICY = _DATA.get("visa_policy", {})

# === Optional links (file if present, else small fallback) ===
LINKS_PATH = Path(__file__).resolve().parents[1] / "json" / "embassy_links.json"
if LINKS_PATH.exists():
    with open(LINKS_PATH, "r", encoding="utf-8") as f:
        _LINKS = json.load(f)
else:
    _LINKS = {
        "Turkey": "https://www.mfa.gov.tr/visa-information-for-foreigners.en.mfa",
        "Malaysia": "https://www.imi.gov.my/",
        "Maldives": "https://immigration.gov.mv/",
        "Armenia": "https://evisa.mfa.am/",
        "India": "https://indianvisaonline.gov.in/",
        "Kenya": "https://evisa.go.ke/",
        "United States": "https://www.ustraveldocs.com/",
        "Germany": "https://beirut.diplo.de/lb-en/service/visa",
    }

# === Build fast lookup: normalized country -> (category, entry) ===
def _norm(s: str) -> str:
    return (s or "").strip().casefold()

_LOOKUP = {}
for cat, items in _POLICY.items():
    for entry in items:
        name = entry.get("country", "")
        if name:
            _LOOKUP[_norm(name)] = (cat, entry)

def _fmt_category(cat: str) -> str:
    labels = {
        "visa_free": "🟢 Visa-free",
        "visa_on_arrival": "🟡 Visa on arrival",
        "e_visa": "🔵 e-Visa",
        "visa_required": "🔴 Visa required",
    }
    return labels.get(cat, cat)

def _fuzzy_key(q: str) -> str | None:
    key = _norm(q)
    if key in _LOOKUP:
        return key
    match = get_close_matches(key, list(_LOOKUP.keys()), n=1, cutoff=0.6)
    return match[0] if match else None

def _parse_days(stay: str) -> int | None:
    # expects strings like "90 days", returns 90
    if not stay:
        return None
    parts = stay.strip().split()
    for p in parts:
        if p.isdigit():
            return int(p)
    return None

def _stay_until(stay_duration: str) -> str:
    days = _parse_days(stay_duration)
    if not days:
        return "N/A"
    return (datetime.today() + timedelta(days=days)).strftime("%Y-%m-%d")

def _link_for(country: str) -> str | None:
    return _LINKS.get(country)

@tool
def visa_requirements(destination: str) -> str:
    """
    Visa requirement for a Lebanese passport to the given destination.
    Example: visa_requirements("Germany")
    """
    if not destination:
        return "Please provide a destination country."

    k = _fuzzy_key(destination)
    if not k:
        return f"No entry for '{destination}' (passport: {_PASSPORT}). Last updated: {_LAST_UPDATED}"

    category, entry = _LOOKUP[k]
    country = entry.get("country", destination)
    stay = entry.get("stay_duration", "N/A")
    notes = entry.get("notes", "—")
    until = _stay_until(stay)
    link = _link_for(country)

    out = [
        f"Passport: {_PASSPORT}",
        f"Destination: {country}",
        f"Category: {_fmt_category(category)}",
        f"Stay duration: {stay}",
        f"Stay until (if you arrive today): {until}",
        f"Notes: {notes}",
        f"Last updated: {_LAST_UPDATED}",
    ]
    if link:
        out.append(f"More info: {link}")
    out.append("Tip: Always verify with the official embassy before you book.")
    return "\n".join(out)

@tool
def visa_suggestions(visa_type: str = "visa_free", limit: int = 50) -> str:
    """
    Suggest destinations by visa type: visa_free, visa_on_arrival, e_visa, visa_required.
    Example: visa_suggestions("e_visa", 10)
    """
    vt = visa_type.strip()
    if vt not in _POLICY:
        return "Unknown visa type. Use: visa_free, visa_on_arrival, e_visa, visa_required."

    items = _POLICY[vt][:limit]
    lines = [f"Suggestions for {_PASSPORT} passport — {_fmt_category(vt)} (up to {limit}):"]
    for x in items:
        c = x.get("country", "Unknown")
        stay = x.get("stay_duration", "N/A")
        link = _link_for(c)
        tail = f" | {stay}"
        if link:
            tail += f" | {link}"
        lines.append(f"- {c}{tail}")
    return "\n".join(lines)
