"""
Disk IO helpers: Parquet + DuckDB
"""
import logging
from pathlib import Path

import duckdb
import pandas as pd

from .config import DATA_DIR, TRACK_META

logger = logging.getLogger(__name__)


def save_parquet(df: pd.DataFrame, filename: str = "f1_laps.parquet") -> Path:
    dest = DATA_DIR / filename
    df.to_parquet(dest, index=False, compression="snappy")
    logger.info(f"Parquet  {dest}  ({dest.stat().st_size/1_048_576:.1f} MB)")
    return dest


def save_duckdb(df: pd.DataFrame, db_name: str = "f1_data.db") -> Path:
    db_path = DATA_DIR / db_name
    with duckdb.connect(str(db_path)) as con:
        con.execute("DROP TABLE IF EXISTS laps")
        con.execute("CREATE TABLE laps AS SELECT * FROM df")
        # -- circuits table
        circ_df = pd.DataFrame(
            [{"track_id": k, "pit_loss_time": v["pit_loss"], "track_length_km": v["len_km"]} for k, v in TRACK_META.items()]
        )
        con.execute("DROP TABLE IF EXISTS circuits")
        con.execute("CREATE TABLE circuits AS SELECT * FROM circ_df")

        # simple views
        con.execute(
            """
            CREATE OR REPLACE VIEW race_summary AS
            SELECT season, track_id, event_name,
                   COUNT(*) AS total_laps,
                   AVG(LapTime) AS avg_lap,
                   MIN(LapTime) AS fastest_lap,
                   SUM(is_safety_car::int) AS sc_laps
            FROM laps
            GROUP BY season, track_id, event_name
            ORDER BY season DESC, event_name
        """
        )

    logger.info("DuckDB  %s  (%d laps)" % (db_path, len(df)))
    return db_path 