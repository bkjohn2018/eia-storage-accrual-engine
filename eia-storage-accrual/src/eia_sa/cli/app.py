from __future__ import annotations
import argparse, sys, datetime as dt
import pandas as pd
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

from eia_sa.transform.normalize_weekly import normalize_weekly
from eia_sa.transform.normalize_capacity import normalize_capacity
from eia_sa.transform.build_gold import build_monthly_rollforward
from eia_sa.accrual.kpis import compute_kpis
from eia_sa.accrual.calculator import AccrualInputs, calc_accruals, DEFAULT_BCF_TO_MMBTU
from eia_sa.analysis.narratives import build_narrative_inputs, cfo_summary, ops_summary
from eia_sa.utils.excel_pack import write_close_pack


def main():
    print('Enhanced CLI working')
    return 0
