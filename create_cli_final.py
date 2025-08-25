#!/usr/bin/env python3
"""Create the complete CLI file with proper encoding and Simon's conventions."""

from pathlib import Path

cli_content = '''from __future__ import annotations
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

def _pkg_version():
    try: return version("eia-sa")
    except PackageNotFoundError: return "0.0.0+local"

def cmd_build_silver(args: argparse.Namespace) -> int:
    if args.verbose > 0:
        print(f"Building silver from {args.weekly_bronze}")
    w = normalize_weekly(args.weekly_bronze)
    Path(args.weekly_silver_out).parent.mkdir(parents=True, exist_ok=True)
    w.to_parquet(args.weekly_silver_out, index=False)
    try:
        c = normalize_capacity(args.capacity_bronze)
        Path(args.capacity_silver_out).parent.mkdir(parents=True, exist_ok=True)
        c.to_parquet(args.capacity_silver_out, index=False)
    except Exception:
        pass
    print("silver built"); return 0

def cmd_build_gold(args: argparse.Namespace) -> int:
    if args.verbose > 0:
        print(f"Building gold for {args.asof} with weights {args.weights}")
    asof_date = dt.date.fromisoformat(args.asof)
    w = pd.read_parquet(args.weekly_silver)
    w["stratum"] = w["stratum"].fillna("none")
    a, b, c = [float(x) for x in args.weights.split(",")]
    mf = build_monthly_rollforward(
        w, asof=asof_date, weights=(a,b,c),
        region=args.region, stratum=None if args.stratum=="none" else args.stratum
    )
    Path(args.monthly_roll_out).parent.mkdir(parents=True, exist_ok=True)
    mf.to_parquet(args.monthly_roll_out, index=False)
    try:
        cap = pd.read_parquet(args.capacity_silver)
    except Exception:
        cap = None  # type: ignore
    k = compute_kpis(mf, cap)  # type: ignore
    Path(args.kpis_out).parent.mkdir(parents=True, exist_ok=True)
    k.to_parquet(args.kpis_out, index=False)
    print("gold built"); return 0

def cmd_calc_accruals(args: argparse.Namespace) -> int:
    if args.verbose > 0:
        print(f"Calculating accruals for {args.asof} with WACOG {args.wacog}")
    roll = pd.read_parquet(args.monthly_roll)
    kpis = pd.read_parquet(args.kpis_path)
    ai = AccrualInputs(
        wacog_per_mmbtu=args.wacog,
        bcf_to_mmbtu_factor=args.bcf_to_mmbtu or DEFAULT_BCF_TO_MMBTU,
        tariff_fixed_monthly=args.tariff_fixed,
        tariff_injection_per_mmbtu=args.tariff_inj,
        tariff_withdrawal_per_mmbtu=args.tariff_wd,
        scenario_band=args.scenario_band,
        penalty_probability=args.penalty_probability,
        penalty_amount=args.penalty_amount,
    )
    accruals = calc_accruals(roll, ai)
    Path("data/gold").mkdir(parents=True, exist_ok=True)
    accruals.to_parquet("data/gold/accruals.parquet", index=False)
    Path(args.out_excel).parent.mkdir(parents=True, exist_ok=True)
    write_close_pack(
        roll, kpis, accruals,
        assumptions={
            "wacog_per_mmbtu": args.wacog,
            "bcf_to_mmbtu_factor": ai.bcf_to_mmbtu_factor,
            "tariff_fixed": args.tariff_fixed,
            "tariff_injection": args.tariff_inj,
            "tariff_withdrawal": args.tariff_wd,
            "scenario_band": args.scenario_band,
            "penalty_probability": args.penalty_probability,
            "penalty_amount": args.penalty_amount,
        },
        out_path=args.out_excel
    )
    
    # JSON mode for machine consumers
    if args.json:
        import json
        print(json.dumps({
            "asof": args.asof,
            "rows": len(accruals),
            "out_excel": args.out_excel,
            "total_accrual_base": float(accruals["total_accrual_base"].sum())
        }))
    
    print(f"close pack written: {args.out_excel}"); return 0

def cmd_narratives(args: argparse.Namespace) -> int:
    if args.verbose > 0:
        print(f"Generating narratives with weights {args.weights}")
    roll = pd.read_parquet(args.monthly_roll)
    kpis = pd.read_parquet(args.kpis_path)
    accr = pd.read_parquet(args.accruals_path)
    a, b, c = [float(x) for x in args.weights.split(",")]
    ni = build_narrative_inputs(
        roll=roll, kpis=kpis, accruals=accr, weights=(a,b,c), band_pct=args.scenario_band,
        zscore_txt=args.zscore_txt, dominant_method=args.dominant_method, rationale=args.rationale,
        hotspot_region=args.hotspot_region, hotspot_stratum=args.hotspot_stratum, hotspot_driver=args.hotspot_driver,
        nom_adjust_bcf=args.nom_adjust_bcf, scenario_name=args.scenario_name,
        tariff_inj=args.tariff_inj, tariff_wd=args.tariff_wd
    )
    cfo = cfo_summary(ni); ops = ops_summary(ni)
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    me = pd.to_datetime(roll.iloc[0]["month_end"]).date()
    (out_dir / f"narrative_cfo_{me}.md").write_text(cfo, encoding="utf-8")
    (out_dir / f"narrative_ops_{me}.md").write_text(ops, encoding="utf-8")
    print(f"wrote narratives to {out_dir}"); return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="eia-sa",
        description="EIA storage accrual engine (silver→gold→accruals→narratives)",
        epilog="""Examples:
  eia-sa build-silver -w data/bronze/eia_weekly_storage.parquet -c data/bronze/eia_capacity.parquet
  eia-sa build-gold --asof 2025-08-31 --weights 0.3,0.2,0.5
  eia-sa calc-accruals --asof 2025-08-31 --wacog 3.25 --tariff-fixed 120000
  eia-sa narratives --out-dir outputs
        """
    )
    p.add_argument("-V","--version", action="version", version=f"%(prog)s {_pkg_version()}")
    p.add_argument("-v","--verbose", action="count", default=0, help="Increase verbosity (-v, -vv)")
    sub = p.add_subparsers(dest="cmd", required=True)
    
    s = sub.add_parser("build-silver", help="Normalize bronze parquet to silver")
    s.add_argument("-w","--weekly-bronze", default="data/bronze/eia_weekly_storage.parquet")
    s.add_argument("-c","--capacity-bronze", default="data/bronze/eia_capacity.parquet")
    s.add_argument("--weekly-silver-out", default="data/silver/eia_weekly_storage.parquet")
    s.add_argument("--capacity-silver-out", default="data/silver/eia_capacity.parquet")
    s.set_defaults(func=cmd_build_silver)

    g = sub.add_parser("build-gold", help="Build monthly rollforward using Methods A/B/C blend")
    g.add_argument("-A","--asof", required=True, help="Month-end date (YYYY-MM-DD)")
    g.add_argument("-W","--weights", default="0.3,0.2,0.5", help="Method weights: A,B,C")
    g.add_argument("-w","--weekly-silver", default="data/silver/eia_weekly_storage.parquet")
    g.add_argument("-c","--capacity-silver", default="data/silver/eia_capacity.parquet")
    g.add_argument("-o","--monthly-roll-out", default="data/gold/monthly_storage_rollforward.parquet")
    g.add_argument("-k","--kpis-out", default="data/gold/monthly_kpis.parquet")
    g.add_argument("-r","--region", default="US")
    g.add_argument("-s","--stratum", default="none")
    g.set_defaults(func=cmd_build_gold)

    a = sub.add_parser("calc-accruals", help="Calculate accruals and generate Excel close pack")
    a.add_argument("-A","--asof", required=True, help="Month-end date (YYYY-MM-DD)")
    a.add_argument("-W","--wacog", type=float, required=True, help="Weighted average cost of gas ($/MMBtu)")
    a.add_argument("-b","--bcf-to-mmbtu", type=float, default=None, help="BCF to MMBtu conversion factor")
    a.add_argument("-f","--tariff-fixed", type=float, default=0.0, help="Fixed monthly tariff ($)")
    a.add_argument("-i","--tariff-inj", type=float, default=0.0, help="Injection tariff ($/MMBtu)")
    a.add_argument("-d","--tariff-wd", type=float, default=0.0, help="Withdrawal tariff ($/MMBtu)")
    a.add_argument("-B","--scenario-band", type=float, default=0.10, help="Scenario band (0.10 = ±10%)")
    a.add_argument("-p","--penalty-probability", type=float, default=0.0, help="Penalty probability")
    a.add_argument("-a","--penalty-amount", type=float, default=0.0, help="Penalty amount ($)")
    a.add_argument("-m","--monthly-roll", default="data/gold/monthly_storage_rollforward.parquet")
    a.add_argument("-k","--kpis-path", default="data/gold/monthly_kpis.parquet")
    a.add_argument("-o","--out-excel", default="outputs/monthly_close_pack.xlsx")
    a.add_argument("-j","--json", action="store_true", help="Emit JSON summary to stdout")
    a.set_defaults(func=cmd_calc_accruals)

    n = sub.add_parser("narratives", help="Generate CFO and Ops narratives")
    n.add_argument("-W","--weights", default="0.3,0.2,0.5", help="Method weights: A,B,C")
    n.add_argument("-B","--scenario-band", type=float, default=0.10, help="Scenario band")
    n.add_argument("-z","--zscore-txt", default="near the 5-year average", help="Z-score description")
    n.add_argument("-d","--dominant-method", default="Method C (Ops)", help="Dominant estimation method")
    n.add_argument("-r","--rationale", default="recent nominations/injections during the gap window", help="Estimation rationale")
    n.add_argument("-R","--hotspot-region", default="US", help="Hotspot region")
    n.add_argument("-S","--hotspot-stratum", default="none", help="Hotspot stratum")
    n.add_argument("-D","--hotspot-driver", default="South-Central salt variability", help="Hotspot driver")
    n.add_argument("-n","--nom-adjust-bcf", type=float, default=0.10, help="Nomination adjustment (BCF)")
    n.add_argument("-s","--scenario-name", default="cold-snap", help="Scenario name")
    n.add_argument("-i","--tariff-inj", type=float, default=0.02, help="Injection tariff ($/MMBtu)")
    n.add_argument("-w","--tariff-wd", type=float, default=0.03, help="Withdrawal tariff ($/MMBtu)")
    n.add_argument("-m","--monthly-roll", default="data/gold/monthly_storage_rollforward.parquet")
    n.add_argument("-k","--kpis-path", default="data/gold/monthly_kpis.parquet")
    n.add_argument("-a","--accruals-path", default="data/gold/accruals.parquet")
    n.add_argument("-o","--out-dir", default="outputs")
    n.set_defaults(func=cmd_narratives)
    return p

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        rc = args.func(args)
        return int(rc) if isinstance(rc, int) else 0
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr); return 130
    except Exception as e:
        if getattr(args, "verbose", 0) > 0:
            raise
        print(f"ERROR: {e}", file=sys.stderr); return 1

if __name__ == "__main__":
    sys.exit(main())
'''

# Ensure the CLI directory exists
p = Path("src/eia_sa/cli")
p.mkdir(parents=True, exist_ok=True)

# Write the CLI file with explicit UTF-8 encoding
Path(p / "app.py").write_text(cli_content, encoding="utf-8")
print("✅ wrote src/eia_sa/cli/app.py")
print(f"File size: {Path(p / 'app.py').stat().st_size} bytes")
