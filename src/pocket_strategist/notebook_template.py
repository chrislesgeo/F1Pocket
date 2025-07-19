"""
Writes a ready‑to‑run Jupyter notebook that pulls from DuckDB
and makes a couple of sanity plots.
"""
import json
from pathlib import Path
from textwrap import dedent

from .config import DATA_DIR

_TEMPLATE = {
    "cells": [
        {
            "cell_type": "markdown",
            "source": ["# F1\u00a0Data exploration\nInitial lap‑time sanity checks"],
            "metadata": {},
        },
        {
            "cell_type": "code",
            "source": dedent(
                """
                import duckdb, pandas as pd, matplotlib.pyplot as plt, seaborn as sns, polars as pl
                plt.style.use('seaborn-v0_8'); sns.set_palette('husl')
                con = duckdb.connect('data/f1_data.db')
                laps = con.execute('SELECT * FROM laps WHERE NOT is_outlier').df()
                print(f'laps: {len(laps):,}', 'drivers:', laps.Driver.nunique())
                """
            ),
            "metadata": {},
        },
    ],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}


def create_notebook(path: Path = Path("notebooks/explore_laps.ipynb")) -> Path:
    path.parent.mkdir(exist_ok=True)
    with path.open("w") as f:
        json.dump(_TEMPLATE, f, indent=1)
    return path 