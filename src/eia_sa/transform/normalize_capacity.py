from __future__ import annotations
import pandas as pd

def normalize_capacity(raw_parquet: str) -> pd.DataFrame:
    df = pd.read_parquet(raw_parquet)
    df = df.rename(columns={
        "area":"region",
        "working_capacity":"working_capacity_bcf",
        "design_capacity":"design_capacity_bcf"
    })
    if "stratum" not in df.columns:
        df["stratum"] = "none"
    wanted = ["region","stratum","year","working_capacity_bcf","design_capacity_bcf"]
    missing = [c for c in wanted if c not in df.columns]
    if missing:
        raise ValueError(f"normalize_capacity: missing {missing}. columns: {df.columns.tolist()}")
    return df[wanted]
