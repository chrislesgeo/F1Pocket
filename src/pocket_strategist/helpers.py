"""
Utility functions that don t talk to disk or the network.
"""
import pandas as pd
from typing import Dict, List
from .config import COMPOUND_MAP

# --------- name normalisation ---------
_NAME_MAP = {
    "Bahrain Grand Prix": "bahrain",
    "Saudi Arabian Grand Prix": "saudi_arabia",
    "Australian Grand Prix": "australia",
    "Japanese Grand Prix": "japan",
    "Chinese Grand Prix": "china",
    "Miami Grand Prix": "miami",
    "Monaco Grand Prix": "monaco",
    "Spanish Grand Prix": "spain",
    "Canadian Grand Prix": "canada",
    "Austrian Grand Prix": "austria",
    "British Grand Prix": "great_britain",
    "Hungarian Grand Prix": "hungary",
    "Belgian Grand Prix": "belgium",
    "Dutch Grand Prix": "netherlands",
    "Italian Grand Prix": "italy",
    "Singapore Grand Prix": "singapore",
    "United States Grand Prix": "united_states",
    "Mexican Grand Prix": "mexico",
    "Brazilian Grand Prix": "brazil",
    "Las Vegas Grand Prix": "las_vegas",
    "Qatar Grand Prix": "qatar",
    "Abu Dhabi Grand Prix": "abu_dhabi",
}

def normalize_track_name(event_name: str) -> str:
    return _NAME_MAP.get(
        event_name,
        event_name.lower()
        .replace(" grand prix", "")
        .replace(" ", "_")
        .strip("_"),
    )

# ---------- fuel & tyre helpers ----------
def estimate_fuel_kg(stint_lap: int, start_fuel: float = 100, burn_per_lap: float = 2) -> float:
    """
    Very crude fuel burn curve.
    """
    return max(10.0, start_fuel - stint_lap * burn_per_lap)

def identify_safety_car_laps(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Flags laps that are >20 % slower than rolling 5 lap median for the same driver+stint.
    Adds boolean columns: is_safety_car, is_outlier.
    """
    if laps_df.empty:
        return laps_df

    laps_df["is_safety_car"] = False
    laps_df["is_outlier"] = False
    for drv, drv_laps in laps_df.groupby("Driver"):
        drv_laps = drv_laps.sort_values("LapNumber")
        if len(drv_laps) < 5:
            continue
        roll = drv_laps["LapTime"].rolling(5, center=True).median()
        slow_mask = drv_laps["LapTime"] > roll * 1.20
        outlier_mask = drv_laps["LapTime"] > drv_laps["LapTime"].median() * 2
        laps_df.loc[slow_mask.index, "is_safety_car"] = slow_mask
        laps_df.loc[outlier_mask.index, "is_outlier"] = outlier_mask
    return laps_df

def normalise_compound(raw: str) -> str:
    return COMPOUND_MAP.get(raw or "UNKNOWN", "unknown") 