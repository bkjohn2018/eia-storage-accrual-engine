from __future__ import annotations
import pandas as pd
import numpy as np

def compute_kpis(monthly_roll: pd.DataFrame, capacity: pd.DataFrame | None) -> pd.DataFrame:
    df = monthly_roll.copy()
    if capacity is not None and not capacity.empty:
        latest_cap = capacity.sort_values("year").groupby(["region","stratum"]).tail(1)
        df = df.merge(latest_cap[["region","stratum","working_capacity_bcf"]], on=["region","stratum"], how="left")
        df["pct_of_capacity"] = (df["end_working_gas_bcf"] / df["working_capacity_bcf"]) * 100.0
    else:
        df["pct_of_capacity"] = np.nan
    # placeholder for future: z-score vs 5yr avg at month-end
    df["zscore_vs_5yr"] = np.nan
    return df
