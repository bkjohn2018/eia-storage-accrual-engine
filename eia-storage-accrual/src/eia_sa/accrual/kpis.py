from __future__ import annotations
import pandas as pd

def compute_kpis(monthly_roll: pd.DataFrame, capacity=None) -> pd.DataFrame:
    return monthly_roll.copy()
