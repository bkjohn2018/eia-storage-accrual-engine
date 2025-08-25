from __future__ import annotations
from dataclasses import dataclass
import datetime as dt
import pandas as pd
from typing import Optional, Protocol, Dict

class Estimator(Protocol):
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = "US", stratum: Optional[str] = None) -> float: ...

def _select_series(weekly: pd.DataFrame, region: str, stratum: Optional[str]) -> pd.DataFrame:
    w = weekly.copy()
    w = w[(w["region"] == region) & (w["stratum"].fillna("none") == (stratum or "none"))]
    return w.sort_values("date_reported")

def _gap_days(last_friday: dt.date, month_end: dt.date) -> int:
    return max((month_end - last_friday).days, 0)

@dataclass(frozen=True)
class MethodA:
    lookback_weeks: int = 4
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = "US", stratum: Optional[str] = None) -> float:
        sr = _select_series(weekly, region, stratum)
        sr = sr[sr["date_reported"] <= asof]
        if sr.empty: return 0.0
        last_friday = pd.to_datetime(sr["date_reported"].max()).date()
        month_end = (pd.Timestamp(asof).to_period("M").end_time.date())
        g = _gap_days(last_friday, month_end)
        tail = sr.tail(self.lookback_weeks)
        if tail.empty: return 0.0
        avg_daily = tail["delta_week_bcf"].sum() / (7 * len(tail))
        return float(avg_daily * g)

@dataclass(frozen=True)
class MethodB:
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = "US", stratum: Optional[str] = None) -> float:
        sr = _select_series(weekly, region, stratum)
        sr = sr[sr["date_reported"] <= asof].copy()
        if sr.empty: return 0.0
        sr["month"] = pd.to_datetime(sr["date_reported"]).dt.month
        sr["daily_rate"] = sr["delta_week_bcf"] / 7.0
        month_avg = sr.groupby("month", as_index=True)["daily_rate"].mean()
        last_friday = pd.to_datetime(sr["date_reported"].max()).date()
        month_end = (pd.Timestamp(asof).to_period("M").end_time.date())
        g = _gap_days(last_friday, month_end)
        return float(month_avg.loc[asof.month] * g) if asof.month in month_avg.index else 0.0

@dataclass(frozen=True)
class MethodC:
    ops_path: str = "data/ops/ops_volumes.csv"
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = "US", stratum: Optional[str] = None) -> float:
        sr = _select_series(weekly, region, stratum)
        if sr.empty: return 0.0
        last_friday = pd.to_datetime(sr[sr["date_reported"] <= asof]["date_reported"].max()).date()
        month_end = (pd.Timestamp(asof).to_period("M").end_time.date())
        if month_end <= last_friday: return 0.0
        try:
            ops = pd.read_csv(self.ops_path, parse_dates=["date"])
        except FileNotFoundError:
            return 0.0
        ops = ops[(ops["date"].dt.date > last_friday) & (ops["date"].dt.date <= month_end)]
        ops = ops[(ops["region"] == region) & (ops["stratum"].fillna("none") == (stratum or "none"))]
        if ops.empty: return 0.0
        net = float(ops["inj_bcf"].fillna(0).sum() - ops["wd_bcf"].fillna(0).sum())
        return net

@dataclass
class BlendedEstimator:
    weights: Dict[str, float]
    mA: MethodA; mB: MethodB; mC: MethodC
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = "US", stratum: Optional[str] = None) -> float:
        a = self.mA.estimate_gap(weekly, asof, region, stratum)
        b = self.mB.estimate_gap(weekly, asof, region, stratum)
        c = self.mC.estimate_gap(weekly, asof, region, stratum)
        wA = self.weights.get("A", 0.3); wB = self.weights.get("B", 0.2); wC = self.weights.get("C", 0.5)
        return float(wA*a + wB*b + wC*c)
