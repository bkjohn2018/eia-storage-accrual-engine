import pandas as pd
from eia_sa.analysis.narratives import build_narrative_inputs, cfo_summary, ops_summary

def test_narratives_minimal():
    roll = pd.DataFrame([{
        "month_end": "2025-08-31",
        "end_working_gas_bcf": 3298.0,
        "est_injections_bcf": 0.25,
        "est_withdrawals_bcf": 0.05,
        "gap_delta_bcf": 0.10,
        "gap_days": 2
    }])
    kpis = pd.DataFrame([{"pct_of_capacity": 85.2}])
    accr = pd.DataFrame([{
        "inventory_accrual": 1_000_000.0,
        "variable_fees": 50_000.0,
        "fixed_demand": 120_000.0,
        "penalties_est": 0.0,
        "total_accrual_low": 1_035_000.0,
        "total_accrual_base": 1_170_000.0,
        "total_accrual_high": 1_287_000.0,
    }])

    ni = build_narrative_inputs(roll, kpis, accr, weights=(0.3,0.2,0.5), band_pct=0.10)
    assert "As of 2025-08-31" in cfo_summary(ni)
    assert "For 2025-08-31" in ops_summary(ni)
