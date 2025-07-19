import argparse
import logging

from .ingestion import download_seasons
from .storage import save_duckdb, save_parquet
from .notebook_template import create_notebook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)


def main() -> None:
    p = argparse.ArgumentParser(description="Pocket Strategist  F1 data ingestion")
    p.add_argument("--years", nargs="+", type=int, default=[2023, 2024])
    p.add_argument("--skip-download", action="store_true")
    args = p.parse_args()

    if not args.skip_download:
        df = download_seasons(args.years)
        if df is None:
            log.error("No data downloaded; abort.")
            return
        parquet_path = save_parquet(df)
        db_path = save_duckdb(df)
        log.info("✓ Pipeline done\n   Parquet: %s\n   DuckDB: %s", parquet_path, db_path)

    nb = create_notebook()
    log.info("Notebook scaffold  %s", nb)
    print(
        "\n🏁 NEXT:\n"
        f"  1.  jupyter notebook {nb}\n"
        "  2.  run cells & explore lap‑time sanity\n"
    )


if __name__ == "__main__":
    main() 