from pathlib import Path

# ---------- directories ----------
DATA_DIR  = Path("data")
CACHE_DIR = Path("cache")

DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# ---------- tyre compound map ----------
COMPOUND_MAP = {
    "SOFT": "soft",
    "MEDIUM": "medium",
    "HARD": "hard",
    "INTERMEDIATE": "intermediate",
    "WET": "wet",
    "UNKNOWN": "unknown",
}

# ---------- track metadata (pit‑lane loss, km) ----------
TRACK_META = {
    "bahrain":         {"pit_loss": 22, "len_km": 5.412},
    "saudi_arabia":    {"pit_loss": 24, "len_km": 6.174},
    "australia":       {"pit_loss": 23, "len_km": 5.278},
    "japan":           {"pit_loss": 19, "len_km": 5.807},
    "china":           {"pit_loss": 22, "len_km": 5.451},
    "miami":           {"pit_loss": 18, "len_km": 5.410},
    "monaco":          {"pit_loss": 16, "len_km": 3.337},
    "spain":           {"pit_loss": 21, "len_km": 4.655},
    "canada":          {"pit_loss": 15, "len_km": 4.361},
    "austria":         {"pit_loss": 18, "len_km": 4.318},
    "great_britain":   {"pit_loss": 20, "len_km": 5.891},
    "hungary":         {"pit_loss": 19, "len_km": 4.381},
    "belgium":         {"pit_loss": 17, "len_km": 7.004},
    "netherlands":     {"pit_loss": 20, "len_km": 4.259},
    "italy":           {"pit_loss": 19, "len_km": 5.793},
    "singapore":       {"pit_loss": 22, "len_km": 5.063},
    "united_states":   {"pit_loss": 20, "len_km": 5.513},
    "mexico":          {"pit_loss": 18, "len_km": 4.304},
    "brazil":          {"pit_loss": 19, "len_km": 4.309},
    "las_vegas":       {"pit_loss": 14, "len_km": 6.120},
    "qatar":           {"pit_loss": 18, "len_km": 5.419},
    "abu_dhabi":       {"pit_loss": 20, "len_km": 5.554},
} 