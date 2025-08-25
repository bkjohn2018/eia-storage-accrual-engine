from __future__ import annotations
import pandas as pd
from pathlib import Path
from datetime import datetime

def write_close_pack(
    rollforward: pd.DataFrame,
    kpis: pd.DataFrame,
    accruals: pd.DataFrame,
    assumptions: dict,
    out_path: str = "outputs/monthly_close_pack.xlsx",
) -> str:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as xl:
        rollforward.to_excel(xl, sheet_name="Rollforward", index=False)
        kpis.to_excel(xl, sheet_name="KPIs", index=False)
        accruals.to_excel(xl, sheet_name="Accruals", index=False)
        pd.DataFrame([assumptions]).to_excel(xl, sheet_name="Assumptions", index=False)
        pd.DataFrame([{"generated_at": datetime.utcnow().isoformat() + "Z"}]).to_excel(
            xl, sheet_name="Audit_Log", index=False
        )
    return out_path
