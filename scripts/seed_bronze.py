#!/usr/bin/env python3
"""Seed realistic bronze test data for EIA Storage Accrual Engine testing."""

from pathlib import Path
import pandas as pd
import numpy as np

def seed_weekly_storage():
    Path("data/bronze").mkdir(parents=True, exist_ok=True)
    # 9 Fridays -> realistic weekly series across Jul–Aug 2025
    dates = pd.date_range("2025-07-04", "2025-08-29", freq="W-FRI")
    # Random walk around ~3,100 Bcf with small weekly injections
    levels = 3100 + np.cumsum(np.random.normal(12, 5, len(dates)))
    wk = pd.DataFrame(
        {
            "period": dates,     # bronze weekly uses 'period' + 'value' + 'area'
            "value": np.round(levels, 1),
            "area": "US",
        }
    )
    wk.to_parquet("data/bronze/eia_weekly_storage.parquet", index=False)
    return wk.shape

def seed_capacity():
    cap = pd.DataFrame(
        {
            "area": ["US"],
            "stratum": ["none"],
            "year": [2025],
            "working_capacity": [3800.0],
            "design_capacity": [4200.0],
        }
    )
    cap.to_parquet("data/bronze/eia_capacity.parquet", index=False)
    return cap.shape

def seed_ops_gap_window():
    Path("data/ops").mkdir(parents=True, exist_ok=True)
    ops = pd.DataFrame(
        {
            "date": pd.date_range("2025-08-30", "2025-08-31", freq="D"),
            "region": ["US", "US"],
            "stratum": ["none", "none"],
            "inj_bcf": [0.08, 0.05],
            "wd_bcf": [0.00, 0.00],
            "notes": ["gap inj", "gap inj"],
        }
    )
    ops.to_csv("data/ops/ops_volumes.csv", index=False)
    return ops.shape

if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    w_shape = seed_weekly_storage()
    c_shape = seed_capacity()
    o_shape = seed_ops_gap_window()
    print(f"✅ Seeded weekly {w_shape}, capacity {c_shape}, ops {o_shape}")
