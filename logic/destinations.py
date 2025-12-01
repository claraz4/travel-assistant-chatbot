DESTINATIONS = [
    {"code": "FR", "country": "France", "city": "Paris"},
    {"code": "DE", "country": "Germany", "city": "Berlin"},
    {"code": "IT", "country": "Italy", "city": "Rome"},
    {"code": "GB", "country": "United Kingdom", "city": "London"},
    {"code": "ES", "country": "Spain", "city": "Barcelona"},
    {"code": "TR", "country": "Turkey", "city": "Istanbul"},
    {"code": "JP", "country": "Japan", "city": "Tokyo"},
    {"code": "US", "country": "United States", "city": "New York"},
]

# map country code -> flag file base name in /pictures/flags
FLAG_NAME = {
    "FR": "france",
    "DE": "germany",
    "IT": "italy",
    "GB": "england",   # your file name
    "ES": "spain",
    "TR": "turkey",
    "JP": "japan",
    "US": "usa",
}

def country_flag(code: str) -> str:
    """Return emoji flag from country code like 'DE'."""
    code = code.upper()
    return "".join(
        chr(ord(c) - 65 + 0x1F1E6) for c in code
        if "A" <= c <= "Z"
    )

