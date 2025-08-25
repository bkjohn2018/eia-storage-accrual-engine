from __future__ import annotations
from dataclasses import dataclass
import datetime as dt
import pandas as pd

@dataclass
class MethodA:
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = 'US', stratum=None) -> float:
        return 0.0

@dataclass
class MethodB:
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = 'US', stratum=None) -> float:
        return 0.0

@dataclass
class MethodC:
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = 'US', stratum=None) -> float:
        return 0.0

@dataclass
class BlendedEstimator:
    weights: dict
    mA: MethodA
    mB: MethodB
    mC: MethodC
    def estimate_gap(self, weekly: pd.DataFrame, asof: dt.date, region: str = 'US', stratum=None) -> float:
        return 0.0
