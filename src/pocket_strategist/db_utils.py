"""
Database utilities for F1 data validation and querying
"""

import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class F1Database:
    def __init__(self, db_path="data/f1_data.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
    
    def get_connection(self):
        """Get DuckDB connection"""
        return duckdb.connect(str(self.db_path))
    
    def validate_data(self):
        """Run data validation checks"""
        with self.get_connection() as conn:
            print("🔍 F1 DATA VALIDATION REPORT")
            print("=" * 50)
            
            # Basic counts
            total_laps = conn.execute("SELECT COUNT(*) FROM laps").fetchone()[0]
            total_races = conn.execute("SELECT COUNT(DISTINCT event_name || season) FROM laps").fetchone()[0]
            total_drivers = conn.execute("SELECT COUNT(DISTINCT Driver) FROM laps").fetchone()[0]
            total_tracks = conn.execute("SELECT COUNT(DISTINCT track_id) FROM laps").fetchone()[0]
            
            print(f"📊 Total Records: {total_laps:,}")
            print(f"🏁 Races: {total_races}")
            print(f"👤 Drivers: {total_drivers}")
            print(f"🏎️  Tracks: {total_tracks}")
            
            # Data quality checks
            print("\n🔬 DATA QUALITY")
            print("-" * 20)
            
            # Null lap times
            null_laptimes = conn.execute("SELECT COUNT(*) FROM laps WHERE LapTime IS NULL").fetchone()[0]
            print(f"❌ Null lap times: {null_laptimes:,} ({null_laptimes/total_laps*100:.1f}%)")
            
            # Outlier laps
            outlier_laps = conn.execute("SELECT COUNT(*) FROM laps WHERE is_outlier = true").fetchone()[0]
            print(f"⚠️  Outlier laps: {outlier_laps:,} ({outlier_laps/total_laps*100:.1f}%)")
            
            # Safety car laps
            sc_laps = conn.execute("SELECT COUNT(*) FROM laps WHERE is_safety_car = true").fetchone()[0]
            print(f"🚨 Safety car laps: {sc_laps:,} ({sc_laps/total_laps*100:.1f}%)")
            
            # Lap time ranges
            lap_stats = conn.execute("""
                SELECT 
                    MIN(LapTime) as fastest,
                    AVG(LapTime) as average, 
                    MAX(LapTime) as slowest,
                    STDDEV(LapTime) as std_dev
                FROM laps 
                WHERE LapTime IS NOT NULL AND NOT is_outlier
            """).fetchone()
            
            print(f"⏱️  Lap times: {lap_stats[0]:.1f}s to {lap_stats[2]:.1f}s (avg: {lap_stats[1]:.1f}s ±{lap_stats[3]:.1f}s)")
            
            # Compound distribution
            print("\n🛞 TYRE COMPOUNDS")
            print("-" * 20)
            compounds = conn.execute("""
                SELECT compound_normalized, COUNT(*) as count
                FROM laps
                WHERE compound_normalized != 'unknown'
                GROUP BY compound_normalized
                ORDER BY count DESC
            """).fetchall()
            
            for compound, count in compounds:
                print(f"{compound.title():>12}: {count:,} laps")
            
            # Season breakdown
            print("\n📅 SEASON BREAKDOWN")
            print("-" * 20)
            seasons = conn.execute("""
                SELECT season, COUNT(*) as laps, COUNT(DISTINCT event_name) as races
                FROM laps
                GROUP BY season
                ORDER BY season DESC
            """).fetchall()
            for season, laps, races in seasons:
                print(f"{season}: {laps:,} laps, {races} races") 