from __future__ import annotations
import pandas as pd

def _rename_cols(df: pd.DataFrame, mapping: dict[str,str]) -> pd.DataFrame:
    present = {k:v for k,v in mapping.items() if k in df.columns}
    return df.rename(columns=present)

def normalize_weekly(raw_parquet: str) -> pd.DataFrame:
    df = pd.read_parquet(raw_parquet)
    # try common EIA shapes
    df = _rename_cols(df, {"period":"date","value":"working_gas_bcf","area":"region"})
    if "working_gas_bcf" not in df.columns and "value" in df.columns:
        df["working_gas_bcf"] = df["value"]
    if "date_reported" not in df.columns:
        base_date_col = "date" if "date" in df.columns else "period"
        df["date_reported"] = pd.to_datetime(df[base_date_col]).dt.date
    if "region" not in df.columns:
        raise ValueError(f"normalize_weekly: missing 'region' column. got {df.columns.tolist()}")
    if "stratum" not in df.columns:
        df["stratum"] = "none"
    df = df.sort_values(["region","stratum","date_reported"])
    df["delta_week_bcf"] = df.groupby(["region","stratum"])["working_gas_bcf"].diff().fillna(0.0)
    keep = ["date_reported","region","stratum","working_gas_bcf","delta_week_bcf"]
    keep = [c for c in keep if c in df.columns]
    return df[keep]
