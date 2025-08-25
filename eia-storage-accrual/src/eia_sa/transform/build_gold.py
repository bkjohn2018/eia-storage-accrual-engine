from __future__ import annotations
import datetime as dt
import pandas as pd

def build_monthly_rollforward(weekly_silver: pd.DataFrame, asof: dt.date, weights=(0.3,0.2,0.5), region='US', stratum=None) -> pd.DataFrame:
    return pd.DataFrame([{'month_end': asof, 'region': region, 'stratum': stratum or 'none', 'end_working_gas_bcf': 0.0}])
