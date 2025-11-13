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

# === Name helpers ===
def _norm(s: str) -> str:
    return (s or "").strip().casefold()


# common aliases / nicknames → canonical name in your JSON
_ALIASES = {
    "usa": "united states",
    "u.s.a.": "united states",
    "us": "united states",
    "america": "united states",
    "uk": "united kingdom",
    "u.k.": "united kingdom",
    "schengen": "germany",  # using Germany as a “Schengen example” in your dataset
    "eu": "germany",
}

# === Build fast lookup: normalized country -> (category, entry) ===
_LOOKUP = {}
for cat, items in _POLICY.items():
    for entry in items:
        name = entry.get("country", "")
        if not name:
            continue
        base_key = _norm(name)
        _LOOKUP[base_key] = (cat, entry)

        # also map aliases that point to this country
        for alias, target in _ALIASES.items():
            if _norm(target) == base_key:
                _LOOKUP[alias] = (cat, entry)


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

    # map aliases first
    if key in _ALIASES:
        key = _norm(_ALIASES[key])

    if key in _LOOKUP:
        return key

    # try fuzzy match as a fallback
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


def _normalize_trip_type(trip_type: str) -> str:
    t = (trip_type or "").strip().lower()
    mapping = {
        "tourist": "tourism",
        "holiday": "tourism",
        "vacation": "tourism",
        "study": "study",
        "student": "study",
        "work": "work",
        "business": "business",
        "transit": "transit",
        "long stay": "long_stay",
        "long_stay": "long_stay",
    }
    return mapping.get(t, "tourism")  # default to tourism


def _default_timing_window(category: str, tt_norm: str) -> tuple[int | None, int | None]:
    """
    Default “apply X–Y days before” window if JSON doesn't override.
    Returns (min_days, max_days).
    """
    if category == "visa_free":
        return (7, 14)  # just re-check rules and bookings
    if category == "visa_on_arrival":
        return (7, 14)
    if category == "e_visa":
        return (10, 20)

    # visa_required (embassy / consulate)
    if tt_norm in {"study", "work", "long_stay"}:
        return (42, 56)  # 6–8 weeks
    else:
        return (28, 42)  # 4–6 weeks


def _default_processing_days(category: str, tt_norm: str) -> int | None:
    if category == "visa_free":
        return None
    if category == "visa_on_arrival":
        return None
    if category == "e_visa":
        return 3
    if tt_norm in {"study", "work", "long_stay"}:
        return 30
    return 15


def _default_risk_level(category: str, tt_norm: str) -> str:
    # Very rough, just to give a feel
    if category == "visa_free":
        return "very low"
    if category == "visa_on_arrival":
        return "low"
    if category == "e_visa":
        return "low–medium"
    if tt_norm in {"study", "work", "long_stay"}:
        return "medium–high"
    return "medium"


def _timing_text(min_days: int | None, max_days: int | None) -> str:
    if min_days and max_days:
        return (
            f"Ideally apply between {min_days} and {max_days} days before departure "
            "so you have time for any delays."
        )
    if min_days:
        return f"Ideally apply at least {min_days} days before departure."
    if max_days:
        return f"Try to apply no later than {max_days} days before departure."
    return "Apply as early as practical, especially in busy seasons."


def _application_steps(category: str, country: str, trip_type: str) -> str:
    tt = _normalize_trip_type(trip_type)

    if category == "visa_free":
        return (
            "Since this trip is visa-free, you do not need to apply in advance. "
            "Just carry your valid passport, travel insurance if possible, "
            "and proof of accommodation / return ticket."
        )

    if category == "visa_on_arrival":
        return (
            "You do not apply in advance. On arrival, go to the visa counter, "
            "present your passport, completed form, hotel booking, and return ticket, "
            "pay the visa fee if required, and receive the visa stamp at the border."
        )

    if category == "e_visa":
        return (
            "Apply through the official e-visa website. Fill in the online form, "
            "upload a passport scan and photo, pay the fee, and download or print "
            "the e-visa approval to show at check-in and at the border."
        )

    # visa_required – classic embassy route
    if tt in {"study", "work", "long_stay"}:
        return (
            "You must apply at the embassy or visa center in your country. "
            "Choose the correct long-stay / study / work category, gather the required documents "
            "(passport, photos, acceptance or work letter, proof of funds, accommodation, etc.), "
            "book an appointment, attend in person, and then wait for the decision."
        )
    else:
        return (
            "You must apply at the embassy or visa center for a short-stay tourist or business visa. "
            "Fill out the application form, gather documents (passport, photos, travel insurance, "
            "flight and hotel bookings, proof of funds), book an appointment, submit everything, "
            "and wait for the visa to be issued."
        )


@tool
def visa_requirements(destination: str, trip_type: str = "tourism") -> str:
    """
    Visa requirement for a Lebanese passport to the given destination and trip type.

    destination: country you want to visit (e.g. "Germany")
    trip_type:   tourism, study, work, business, transit, long_stay

    Example:
      visa_requirements("Germany", "tourism")
      visa_requirements("United States", "study")
    """
    if not destination:
        return "Please provide a destination country."

    k = _fuzzy_key(destination)
    if not k:
        return (
            f"No entry for '{destination}' for a {_PASSPORT} passport. "
            f"Last updated: {_LAST_UPDATED}"
        )

    category, entry = _LOOKUP[k]
    country = entry.get("country", destination)
    stay = entry.get("stay_duration", "N/A")
    notes = entry.get("notes", "—")
    until = _stay_until(stay)
    link = _link_for(country)

    tt_norm = _normalize_trip_type(trip_type)
    tt_label_map = {
        "tourism": "Tourism / holiday",
        "study": "Study",
        "work": "Work",
        "business": "Business",
        "transit": "Transit",
        "long_stay": "Long stay",
    }
    tt_label = tt_label_map.get(tt_norm, trip_type or "Tourism / holiday")

    # ----- trip-type specific overrides from JSON (if present) -----
    trip_types_cfg = entry.get("trip_types", {}) or {}
    trip_cfg = trip_types_cfg.get(tt_norm, {}) or {}

    cfg_min = trip_cfg.get("recommended_apply_days_min")
    cfg_max = trip_cfg.get("recommended_apply_days_max")
    cfg_proc = trip_cfg.get("processing_days_estimate")
    cfg_risk = trip_cfg.get("risk_level")
    cfg_extra = trip_cfg.get("extra_notes")

    # defaults if JSON did not provide them
    if cfg_min is None or cfg_max is None:
        def_min, def_max = _default_timing_window(category, tt_norm)
        min_days = cfg_min if cfg_min is not None else def_min
        max_days = cfg_max if cfg_max is not None else def_max
    else:
        min_days, max_days = cfg_min, cfg_max

    proc_days = cfg_proc if cfg_proc is not None else _default_processing_days(
        category, tt_norm
    )
    risk = cfg_risk if cfg_risk is not None else _default_risk_level(
        category, tt_norm
    )

    timing_text = _timing_text(min_days, max_days)
    steps = _application_steps(category, country, tt_norm)

    # --- structured output ---
    lines = [
        f"Passport:    {_PASSPORT}",
        f"Destination: {country}",
        f"Trip type:   {tt_label}",
        "",
        f"Visa category: {_fmt_category(category)}",
        f"Allowed stay: {stay}",
        f"If you arrive today, your stay limit would roughly end on: {until}",
        "",
        "Risk & processing:",
        f"- Risk level (chance of delays / complexity): {risk}.",
    ]

    if proc_days:
        lines.append(f"- Typical processing time: about {proc_days} day(s), "
                     "but this can vary by embassy.")
    else:
        lines.append(
            "- Typical processing time: N/A or not applicable (e.g. visa-free / visa on arrival)."
        )

    lines.extend(
        [
            "",
            "How to apply:",
            steps,
            "",
            "When to apply (to avoid last-minute stress):",
            timing_text,
        ]
    )

    if cfg_extra:
        lines.extend(["", "Extra notes for this trip type:", cfg_extra])

    lines.extend(
        [
            "",
            "Extra notes from dataset:",
            notes,
            f"Last updated in file: {_LAST_UPDATED}",
        ]
    )

    if link:
        lines.append(
            f"Official website / embassy link (check latest rules here): {link}"
        )

    lines.append(
        "Tip: Always double-check with the official embassy or consulate before you book anything."
    )

    return "\n".join(lines)


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
    lines = [
        f"Suggestions for {_PASSPORT} passport — {_fmt_category(vt)} (up to {limit}):"
    ]
    for x in items:
        c = x.get("country", "Unknown")
        stay = x.get("stay_duration", "N/A")
        link = _link_for(c)
        tail = f" | {stay}"
        if link:
            tail += f" | {link}"
        lines.append(f"- {c}{tail}")
    return "\n".join(lines)
