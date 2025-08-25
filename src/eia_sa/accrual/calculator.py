from __future__ import annotations
import pandas as pd
from dataclasses import dataclass

DEFAULT_BCF_TO_MMBTU = 1_037_000.0

@dataclass
class AccrualInputs:
    wacog_per_mmbtu: float
    bcf_to_mmbtu_factor: float = DEFAULT_BCF_TO_MMBTU
    tariff_fixed_monthly: float = 0.0
    tariff_injection_per_mmbtu: float = 0.0
    tariff_withdrawal_per_mmbtu: float = 0.0
    scenario_band: float = 0.10
    penalty_probability: float = 0.0
    penalty_amount: float = 0.0

def _inventory_value(bcf: float, ai: AccrualInputs) -> float:
    return bcf * ai.bcf_to_mmbtu_factor * ai.wacog_per_mmbtu

def calc_accruals(monthly_roll: pd.DataFrame, ai: AccrualInputs) -> pd.DataFrame:
    df = monthly_roll.copy()
    df["inventory_accrual"] = df["end_working_gas_bcf"].apply(lambda x: _inventory_value(x, ai))
    inj_mmbtu = df["est_injections_bcf"] * ai.bcf_to_mmbtu_factor
    wd_mmbtu  = df["est_withdrawals_bcf"] * ai.bcf_to_mmbtu_factor
    df["variable_fees"] = inj_mmbtu * ai.tariff_injection_per_mmbtu + wd_mmbtu * ai.tariff_withdrawal_per_mmbtu
    df["fixed_demand"] = ai.tariff_fixed_monthly
    df["penalties_est"] = ai.penalty_probability * ai.penalty_amount
    df["total_accrual_base"] = df["inventory_accrual"] + df["variable_fees"] + df["fixed_demand"] + df["penalties_est"]
    band = ai.scenario_band
    df["total_accrual_low"]  = df["total_accrual_base"] * (1 - band)
    df["total_accrual_high"] = df["total_accrual_base"] * (1 + band)
    cols = [
        "month_end","region","stratum","end_working_gas_bcf",
        "inventory_accrual","variable_fees","fixed_demand","penalties_est",
        "total_accrual_low","total_accrual_base","total_accrual_high"
    ]
    return df[cols]
