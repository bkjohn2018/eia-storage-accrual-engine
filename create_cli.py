from pathlib import Path

code = r'''from __future__ import annotations
import argparse, sys, datetime as dt
import pandas as pd
from pathlib import Path

from eia_sa.transform.normalize_weekly import normalize_weekly
from eia_sa.transform.normalize_capacity import normalize_capacity
from eia_sa.transform.build_gold import build_monthly_rollforward
from eia_sa.accrual.kpis import compute_kpis
from eia_sa.accrual.calculator import AccrualInputs, calc_accruals, DEFAULT_BCF_TO_MMBTU
from eia_sa.analysis.narratives import build_narrative_inputs, cfo_summary, ops_summary
from eia_sa.utils.excel_pack import write_close_pack

def cmd_build_silver(args: argparse.Namespace) -> int:
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
    print(f"close pack written: {args.out_excel}"); return 0

def cmd_narratives(args: argparse.Namespace) -> int:
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
    p = argparse.ArgumentParser(prog="eia-sa"); sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("build-silver")
    s.add_argument("--weekly-bronze", default="data/bronze/eia_weekly_storage.parquet")
    s.add_argument("--capacity-bronze", default="data/bronze/eia_capacity.parquet")
    s.add_argument("--weekly-silver-out", default="data/silver/eia_weekly_storage.parquet")
    s.add_argument("--capacity-silver-out", default="data/silver/eia_capacity.parquet")
    s.set_defaults(func=cmd_build_silver)

    g = sub.add_parser("build-gold")
    g.add_argument("--asof", required=True); g.add_argument("--weights", default="0.3,0.2,0.5")
    g.add_argument("--weekly-silver", default="data/silver/eia_weekly_storage.parquet")
    g.add_argument("--capacity-silver", default="data/silver/eia_capacity.parquet")
    g.add_argument("--monthly-roll-out", default="data/gold/monthly_storage_rollforward.parquet")
    g.add_argument("--kpis-out", default="data/gold/monthly_kpis.parquet")
    g.add_argument("--region", default="US"); g.add_argument("--stratum", default="none")
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
    parser = build_parser(); args = parser.parse_args(argv); return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
'''

# Ensure the CLI directory exists
Path("src/eia_sa/cli").mkdir(parents=True, exist_ok=True)

# Write the CLI file with explicit UTF-8 encoding
Path("src/eia_sa/cli/app.py").write_text(code, encoding="utf-8")
print("✅ wrote src/eia_sa/cli/app.py")
