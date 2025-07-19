"""
Pulls data from FastF1 and returns a **clean pandas DataFrame**.
"""
import logging
from typing import List, Optional

import fastf1
import pandas as pd
from tqdm import tqdm

from .config import CACHE_DIR, TRACK_META
from .helpers import (
    estimate_fuel_kg,
    identify_safety_car_laps,
    normalize_track_name,
    normalise_compound,
)

logger = logging.getLogger(__name__)
fastf1.set_log_level("WARNING")
fastf1.Cache.enable_cache(str(CACHE_DIR))


def _download_session(year: int, event_name: str, session_type: str = "R") -> Optional[pd.DataFrame]:
    """
    Returns a lap‑level DataFrame or None if download fails.
    """
    try:
        sess = fastf1.get_session(year, event_name, session_type)
        sess.load(laps=True, weather=True, messages=False)
        laps = sess.laps
        if laps.empty:
            logger.warning(f"No laps for {event_name} a0{year}")
            return None

        # basic clean‑up --------------------------------------------------
        laps["LapTime"] = laps["LapTime"].dt.total_seconds()
        for col in ("Sector1Time", "Sector2Time", "Sector3Time"):
            laps[col] = pd.to_numeric(laps[col].dt.total_seconds(), errors="coerce")

        # metadata --------------------------------------------------------
        laps["season"] = year
        laps["event_name"] = event_name
        laps["track_id"] = normalize_track_name(event_name)
        laps["session_type"] = session_type
        laps["compound_normalized"] = laps["Compound"].fillna("UNKNOWN").map(normalise_compound)

        # stint lap #
        laps = laps.sort_values(["Driver", "LapNumber"])
        laps["stint_lap"] = laps.groupby(["Driver", "Stint"]).cumcount() + 1

        # circuit meta
        meta = TRACK_META.get(laps["track_id"].iloc[0], {"pit_loss": 20, "len_km": 5.0})
        laps["pit_loss_time"] = meta["pit_loss"]
        laps["track_length_km"] = meta["len_km"]

        # fuel estimate
        laps["fuel_estimate"] = laps["stint_lap"].apply(estimate_fuel_kg)

        # SC flags + outliers
        laps = identify_safety_car_laps(laps)

        # weather merge (simple nearest‑past value per lap time)
        try:
            wx = sess.weather_data.copy()
            if not wx.empty:
                wx["Time"] = wx["Time"].dt.total_seconds()
                laps["Time"] = laps["Time"].dt.total_seconds()
                for col in ["AirTemp", "TrackTemp", "Humidity", "WindSpeed", "Rainfall"]:
                    if col in wx.columns:
                        laps[col] = laps["Time"].apply(
                            lambda t: wx.loc[wx["Time"] <= t, col].iloc[-1]
                            if (wx["Time"] <= t).any()
                            else wx[col].iloc[0]
                        )
        except Exception as e:
            logger.warning(f"Weather merge failed: {e}")

        # clip nonsense times
        laps = laps[(laps["LapTime"] > 30) & (laps["LapTime"] < 300)]
        logger.info(f"  {event_name} a0{year}: {len(laps)} laps")
        return laps

    except Exception as e:
        logger.error(f"  {event_name} a0{year}: {e}")
        return None


def download_seasons(years: List[int]) -> Optional[pd.DataFrame]:
    """
    Loops over all 'conventional' race weekends for the given years.
    """
    all_laps: List[pd.DataFrame] = []
    for yr in years:
        logger.info(f" Season {yr}")
        try:
            sched = fastf1.get_event_schedule(yr)
            races = sched[sched["EventFormat"] == "conventional"]
            for _, ev in tqdm(races.iterrows(), total=len(races), desc=f"{yr}"):
                df = _download_session(yr, ev["EventName"])
                if df is not None:
                    all_laps.append(df)
        except Exception as e:
            logger.error(f"Schedule for {yr} failed: {e}")
    if all_laps:
        return pd.concat(all_laps, ignore_index=True)
    return None 