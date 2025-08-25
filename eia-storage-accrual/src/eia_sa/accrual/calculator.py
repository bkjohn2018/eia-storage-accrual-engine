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

def calc_accruals(monthly_roll: pd.DataFrame, ai: AccrualInputs) -> pd.DataFrame:
    return monthly_roll.copy()
