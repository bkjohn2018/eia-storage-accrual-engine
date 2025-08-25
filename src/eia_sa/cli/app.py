from __future__ import annotations
import argparse, sys, datetime as dt
import pandas as pd
from pathlib import Path

def cmd_build_silver(args: argparse.Namespace) -> int:
    print("silver built")
    return 0

def cmd_build_gold(args: argparse.Namespace) -> int:
    print("gold built")
    return 0

def cmd_calc_accruals(args: argparse.Namespace) -> int:
    print("accruals calculated")
    return 0

def cmd_narratives(args: argparse.Namespace) -> int:
    print("narratives generated")
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="eia-sa")
    sub = p.add_subparsers(dest="cmd", required=True)
    
    s = sub.add_parser("build-silver")
    s.add_argument("--weekly-bronze", default="data/bronze/eia_weekly_storage.parquet")
    s.add_argument("--capacity-bronze", default="data/bronze/eia_capacity.parquet")
    s.add_argument("--weekly-silver-out", default="data/silver/eia_weekly_storage.parquet")
    s.add_argument("--capacity-silver-out", default="data/silver/eia_capacity.parquet")
    s.set_defaults(func=cmd_build_silver)

    g = sub.add_parser("build-gold")
    g.add_argument("--asof", required=True)
    g.add_argument("--weights", default="0.3,0.2,0.5")
    g.add_argument("--weekly-silver", default="data/silver/eia_weekly_storage.parquet")
    g.add_argument("--capacity-silver", default="data/silver/eia_capacity.parquet")
    g.add_argument("--monthly-roll-out", default="data/gold/monthly_storage_rollforward.parquet")
    g.add_argument("--kpis-out", default="data/gold/monthly_kpis.parquet")
    g.add_argument("--region", default="US")
    g.add_argument("--stratum", default="none")
    g.set_defaults(func=cmd_build_gold)

    a = sub.add_parser("calc-accruals")
    a.add_argument("--asof", required=True)
    a.add_argument("--wacog", type=float, required=True)
    a.add_argument("--bcf-to-mmbtu", type=float, default=None)
    a.add_argument("--tariff-fixed", type=float, default=0.0)
    a.add_argument("--tariff-inj", type=float, default=0.0)
    a.add_argument("--tariff-wd", type=float, default=0.0)
    a.add_argument("--scenario-band", type=float, default=0.10)
    a.add_argument("--penalty-probability", type=float, default=0.0)
    a.add_argument("--penalty-amount", type=float, default=0.0)
    a.add_argument("--monthly-roll", default="data/gold/monthly_storage_rollforward.parquet")
    a.add_argument("--kpis-path", default="data/gold/monthly_kpis.parquet")
    a.add_argument("--out-excel", default="outputs/monthly_close_pack.xlsx")
    a.set_defaults(func=cmd_calc_accruals)

    n = sub.add_parser("narratives")
    n.add_argument("--weights", default="0.3,0.2,0.5")
    n.add_argument("--scenario-band", type=float, default=0.10)
    n.add_argument("--zscore-txt", default="near the 5-year average")
    n.add_argument("--dominant-method", default="Method C (Ops)")
    n.add_argument("--rationale", default="recent nominations/injections during the gap window")
    n.add_argument("--hotspot-region", default="US")
    n.add_argument("--hotspot-stratum", default="none")
    n.add_argument("--hotspot-driver", default="South-Central salt variability")
    n.add_argument("--nom-adjust-bcf", type=float, default=0.10)
    n.add_argument("--scenario-name", default="cold-snap")
    n.add_argument("--tariff-inj", type=float, default=0.02)
    n.add_argument("--tariff-wd", type=float, default=0.03)
    n.add_argument("--monthly-roll", default="data/gold/monthly_storage_rollforward.parquet")
    n.add_argument("--kpis-path", default="data/gold/monthly_kpis.parquet")
    n.add_argument("--accruals-path", default="data/gold/accruals.parquet")
    n.add_argument("--out-dir", default="outputs")
    n.set_defaults(func=cmd_narratives)
    
    return p

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main()) 