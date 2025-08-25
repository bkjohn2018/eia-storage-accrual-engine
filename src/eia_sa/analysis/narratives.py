from __future__ import annotations
from dataclasses import dataclass
import datetime as dt
import pandas as pd
from typing import Optional

def _comma(n: float | int | None) -> str:
    if n is None:
        return "—"
    return f"{n:,.0f}"

def _comma2(n: float | int | None) -> str:
    if n is None:
        return "—"
    return f"{n:,.2f}"

def _pct(n: float | None) -> str:
    if n is None:
        return "—"
    return f"{n:.1f}%"

@dataclass
class NarrativeInputs:
    month_end: dt.date
    end_bcf: float
    pct_capacity: Optional[float]
    zscore_txt: str
    gap_days: int
    weights: tuple[float, float, float]  # (A, B, C)
    inv_accrual: float
    var_fees: float
    fixed_demand: float
    penalties: float
    total_low: float
    total_base: float
    total_high: float
    band_pct: float
    inj_bcf: float
    wd_bcf: float
    gap_delta_bcf: float
    dominant_method: str
    rationale: str
    hotspot_region: str
    hotspot_stratum: str
    hotspot_driver: str
    nom_adjust_bcf: float
    scenario_name: str
    tariff_inj: float
    tariff_wd: float

def cfo_summary(n: NarrativeInputs) -> str:
    wA, wB, wC = n.weights
    pct_cap = _pct(n.pct_capacity)
    lines = [
        f"As of {n.month_end.isoformat()}, estimated working gas is **{_comma(n.end_bcf)} Bcf**, "
        f"which is **{pct_cap} of working capacity**.",
        f"We used the **Base** scenario with blended estimator weights **C:A:B = {wC}:{wA}:{wB}**, "
        f"projecting **{n.gap_days}** gap day(s) from the last EIA Friday report.",
        "",
        f"**Accrual summary (USD):** Inventory **${_comma(n.inv_accrual)}**, "
        f"Variable fees **${_comma(n.var_fees)}**, Fixed demand **${_comma(n.fixed_demand)}**, "
        f"Penalties (expected) **${_comma(n.penalties)}**.",
        f"Total Base accrual **${_comma(n.total_base)}**, with sensitivity band ±{_pct(n.band_pct*100)} "
        f"(**${_comma(n.total_low)} – ${_comma(n.total_high)}**).",
        "",
        f"Context: storage stands **{n.zscore_txt}** relative to the 5-year average; "
        f"risk this month is primarily driven by **{n.hotspot_driver}**. "
        f"We expect any true-up to fall within the sensitivity band."
    ]
    return "\n".join(lines)

def ops_summary(n: NarrativeInputs) -> str:
    lines = [
        f"For {n.month_end.isoformat()}, projected **injections = {_comma2(n.inj_bcf)} Bcf** and "
        f"**withdrawals = {_comma2(n.wd_bcf)} Bcf** (net gap delta {_comma2(n.gap_delta_bcf)} Bcf).",
        f"The blended estimator emphasized **{n.dominant_method}** due to {n.rationale}.",
        "",
        "Hotspots:",
        f"- Region: **{n.hotspot_region}** ({n.hotspot_stratum}).",
        f"  Driver: {n.hotspot_driver}; recommend adjusting nominations by **{_comma2(n.nom_adjust_bcf)} Bcf** "
        f"under **{n.scenario_name}** scenario.",
        "",
        "Operational asks:",
        f"- Confirm ops file coverage for {n.gap_days} gap day(s).",
        f"- Validate tariff assumptions (inj {n.tariff_inj}, wd {n.tariff_wd}).",
        "- Flag any expected imbalance penalties beyond the base estimate."
    ]
    return "\n".join(lines)

def build_narrative_inputs(
    roll: pd.DataFrame,
    kpis: pd.DataFrame,
    accruals: pd.DataFrame,
    weights: tuple[float, float, float],
    band_pct: float,
    zscore_txt: str = "near the 5-year average",
    dominant_method: str = "Method C (Ops)",
    rationale: str = "recent nominations/injections during the gap window",
    hotspot_region: str = "US",
    hotspot_stratum: str = "none",
    hotspot_driver: str = "South-Central salt variability",
    nom_adjust_bcf: float = 0.10,
    scenario_name: str = "cold-snap",
    tariff_inj: float = 0.02,
    tariff_wd: float = 0.03,
) -> NarrativeInputs:
    # assume single-row dataframes for the selected region/stratum/month_end
    r = roll.iloc[0].to_dict()
    k = kpis.iloc[0].to_dict()
    a = accruals.iloc[0].to_dict()

    me = pd.to_datetime(r["month_end"]).date()
    end_bcf = float(r["end_working_gas_bcf"])
    inj_bcf = float(r.get("est_injections_bcf", 0.0))
    wd_bcf = float(r.get("est_withdrawals_bcf", 0.0))
    gap_delta_bcf = float(r.get("gap_delta_bcf", 0.0))
    pct_capacity = float(k.get("pct_of_capacity")) if "pct_of_capacity" in k and pd.notna(k["pct_of_capacity"]) else None

    return NarrativeInputs(
        month_end=me,
        end_bcf=end_bcf,
        pct_capacity=pct_capacity,
        zscore_txt=zscore_txt,
        gap_days=int(r.get("gap_days", 0)) if "gap_days" in r else 0,
        weights=weights,
        inv_accrual=float(a["inventory_accrual"]),
        var_fees=float(a["variable_fees"]),
        fixed_demand=float(a["fixed_demand"]),
        penalties=float(a.get("penalties_est", 0.0)),
        total_low=float(a["total_accrual_low"]),
        total_base=float(a["total_accrual_base"]),
        total_high=float(a["total_accrual_high"]),
        band_pct=band_pct,
        inj_bcf=inj_bcf,
        wd_bcf=wd_bcf,
        gap_delta_bcf=gap_delta_bcf,
        dominant_method=dominant_method,
        rationale=rationale,
        hotspot_region=hotspot_region,
        hotspot_stratum=hotspot_stratum,
        hotspot_driver=hotspot_driver,
        nom_adjust_bcf=nom_adjust_bcf,
        scenario_name=scenario_name,
        tariff_inj=tariff_inj,
        tariff_wd=tariff_wd,
    )
