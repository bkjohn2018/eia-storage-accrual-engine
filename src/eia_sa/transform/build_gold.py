from __future__ import annotations
import datetime as dt
import pandas as pd
from eia_sa.accrual.methods import MethodA, MethodB, MethodC, BlendedEstimator

def _month_end(d: dt.date) -> dt.date:
    return (pd.Timestamp(d).to_period("M").end_time.date())  # type: ignore

def _last_reported_friday(sr: pd.DataFrame, asof: dt.date) -> dt.date:
    return pd.to_datetime(sr[sr["date_reported"] <= asof]["date_reported"].max()).date()

def build_monthly_rollforward(
    weekly_silver: pd.DataFrame,
    asof: dt.date,
    weights=(0.3, 0.2, 0.5),
    region="US",
    stratum=None,
) -> pd.DataFrame:
    sr = weekly_silver[
        (weekly_silver["region"] == region)
        & (weekly_silver["stratum"].fillna("none") == (stratum or "none"))
    ].copy()
    sr = sr.sort_values("date_reported")
    me = _month_end(asof)
    prev_me = _month_end((pd.Timestamp(me) - pd.offsets.MonthBegin(1)).date())  # type: ignore

    # beginning = last month-end working_gas
    beg = float(sr[sr["date_reported"] <= prev_me]["working_gas_bcf"].tail(1).squeeze()) if not sr.empty else 0.0

    # in-month deltas (reported Fridays that fall in target month)
    in_month = sr[pd.to_datetime(sr["date_reported"]).dt.to_period("M") == pd.Period(me, freq="M")].copy()
    inj = float(in_month[in_month["delta_week_bcf"] > 0]["delta_week_bcf"].sum())
    wd = float(-in_month[in_month["delta_week_bcf"] < 0]["delta_week_bcf"].sum())

    # gap from last reported Friday → month end
    last_fri = _last_reported_friday(sr, asof)
    gap_days = max((me - last_fri).days, 0)

    est = BlendedEstimator(
        weights={"A": weights[0], "B": weights[1], "C": weights[2]},
        mA=MethodA(),
        mB=MethodB(),
        mC=MethodC(),
    )
    gap_delta = est.estimate_gap(weekly_silver, asof=asof, region=region, stratum=stratum)
    end_est = beg + inj - wd + gap_delta

    return pd.DataFrame(
        [{
            "month_end": me,
            "region": region,
            "stratum": (stratum or "none"),
            "beg_working_gas_bcf": beg,
            "est_injections_bcf": inj,
            "est_withdrawals_bcf": wd,
            "gap_delta_bcf": gap_delta,
            "gap_days": gap_days,
            "end_working_gas_bcf": end_est,
        }]
    )
