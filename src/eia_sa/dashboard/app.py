from __future__ import annotations
import datetime as dt
from pathlib import Path
import pandas as pd
import streamlit as st

# --- Resolve repo root from this file: .../src/eia_sa/dashboard/app.py  -> repo = parents[3] ---
PROJECT_ROOT = Path(__file__).resolve().parents[3]

def _p(p: str | Path) -> Path:
    """Return absolute path under repo root for any relative path."""
    p = Path(p)
    return p if p.is_absolute() else (PROJECT_ROOT / p)

# --- Lazy imports so the app starts even if optional deps are missing ---
def _lazy_imports():
    from eia_sa.transform.normalize_weekly import normalize_weekly
    from eia_sa.transform.normalize_capacity import normalize_capacity
    from eia_sa.transform.build_gold import build_monthly_rollforward
    from eia_sa.accrual.kpis import compute_kpis
    from eia_sa.accrual.calculator import AccrualInputs, calc_accruals, DEFAULT_BCF_TO_MMBTU
    from eia_sa.analysis.narratives import build_narrative_inputs, cfo_summary, ops_summary
    from eia_sa.utils.excel_pack import write_close_pack
    return (normalize_weekly, normalize_capacity, build_monthly_rollforward,
            compute_kpis, AccrualInputs, calc_accruals, DEFAULT_BCF_TO_MMBTU,
            build_narrative_inputs, cfo_summary, ops_summary, write_close_pack)

st.set_page_config(page_title="EIA Storage Accrual Engine", page_icon="📦", layout="wide")

DATA = {
    "bronze_weekly": "data/bronze/eia_weekly_storage.parquet",
    "bronze_capacity": "data/bronze/eia_capacity.parquet",
    "silver_weekly": "data/silver/eia_weekly_storage.parquet",
    "silver_capacity": "data/silver/eia_capacity.parquet",
    "gold_roll": "data/gold/monthly_storage_rollforward.parquet",
    "gold_kpis": "data/gold/monthly_kpis.parquet",
    "gold_accruals": "data/gold/accruals.parquet",
    "ops_csv": "data/ops/ops_volumes.csv",
    "out_excel": "outputs/monthly_close_pack.xlsx",
    "out_dir": "outputs",
}

def _ensure_dirs():
    for p in ["data/bronze","data/silver","data/gold","data/ops","outputs"]:
        _p(p).mkdir(parents=True, exist_ok=True)

@st.cache_data(show_spinner=False)
def _read_parquet(p: str) -> pd.DataFrame:
    pth = _p(p)
    return pd.read_parquet(pth) if pth.exists() else pd.DataFrame()

@st.cache_data(show_spinner=False)
def _read_csv(p: str) -> pd.DataFrame:
    pth = _p(p)
    return pd.read_csv(pth, parse_dates=["date"]) if pth.exists() else pd.DataFrame()

def _write_parquet(df: pd.DataFrame, p: str) -> None:
    _p(p).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(_p(p), index=False)

def main():
    _ensure_dirs()
    st.title("📦 EIA Storage Accrual Engine")
    st.caption("Silver → Gold → Accruals → Narratives")
    st.caption(f"Working dir: `{Path.cwd()}` · Project root: `{PROJECT_ROOT}`")

    # Sidebar: global parameters
    st.sidebar.header("Parameters")
    asof = st.sidebar.date_input("Month End (ASOF)", value=dt.date(2025, 8, 31))
    weights_str = st.sidebar.text_input("Blend Weights A,B,C", value="0.3,0.2,0.5")
    wA, wB, wC = (float(x) for x in weights_str.split(","))
    wacog = st.sidebar.number_input("WACOG ($/MMBtu)", value=3.25, step=0.01)
    tariff_fixed = st.sidebar.number_input("Tariff Fixed ($/mo)", value=120000.0, step=1000.0)
    tariff_inj = st.sidebar.number_input("Tariff Injection ($/MMBtu)", value=0.02, step=0.01, format="%.2f")
    tariff_wd = st.sidebar.number_input("Tariff Withdrawal ($/MMBtu)", value=0.03, step=0.01, format="%.2f")
    band = st.sidebar.slider("Scenario band (±%)", min_value=0.0, max_value=0.5, value=0.10, step=0.01)

    st.sidebar.divider()
    show_previews = st.sidebar.checkbox("Show data previews", value=True)

    # Optional "Run All" chain
    run_all = st.sidebar.button("🚀 Run All (Silver → Gold → Accruals → Narratives)")

    (normalize_weekly, normalize_capacity, build_monthly_rollforward,
     compute_kpis, AccrualInputs, calc_accruals, DEFAULT_BCF_TO_MMBTU,
     build_narrative_inputs, cfo_summary, ops_summary, write_close_pack) = _lazy_imports()

    tab1, tab2, tab3, tab4 = st.tabs(["1) Silver", "2) Gold", "3) Accruals", "4) Narratives"])

    # -------- 1) Silver --------
    with tab1:
        st.subheader("Build Silver")
        col1, col2 = st.columns([1,1])
        with col1:
            st.write("Bronze → Silver transforms.")
            if st.button("Run Silver") or run_all:
                try:
                    w = normalize_weekly(_p(DATA["bronze_weekly"]))
                    _write_parquet(w, DATA["silver_weekly"])
                    try:
                        c = normalize_capacity(_p(DATA["bronze_capacity"]))
                        _write_parquet(c, DATA["silver_capacity"])
                    except Exception:
                        pass  # capacity optional
                    st.success("Silver built ✅")
                except Exception as e:
                    st.error(f"Silver build failed: {e}")
        with col2:
            st.caption("Bronze inputs (detected)")
            st.code(f"Weekly:   {DATA['bronze_weekly']}\nCapacity: {DATA['bronze_capacity']}")

        if show_previews:
            st.caption("Silver Weekly Preview")
            # Add manual refresh button to bypass cache
            if st.button("🔄 Refresh Preview", key="refresh_silver"):
                st.cache_data.clear()
            silver_data = _read_parquet(DATA["silver_weekly"])
            st.write(f"Silver data shape: {silver_data.shape}")
            st.write(f"Silver data path: {_p(DATA['silver_weekly'])}")
            if not silver_data.empty:
                st.dataframe(silver_data.head(20), use_container_width=True)
            else:
                st.warning("No silver data found for preview. File may not exist or be empty.")
                st.info("Try clicking '🔄 Refresh Preview' to clear cache and reload data.")

    # -------- 2) Gold --------
    with tab2:
        st.subheader("Build Gold (Monthly Roll + KPIs)")
        if st.button("Run Gold") or run_all:
            try:
                w = _read_parquet(DATA["silver_weekly"])
                st.write(f"Gold step - Silver data shape: {w.shape}")
                st.write(f"Gold step - Silver data path: {_p(DATA['silver_weekly'])}")
                st.write(f"Gold step - Silver data columns: {list(w.columns)}")
                st.write(f"Gold step - Silver data head: {w.head(3).to_dict()}")
                if w.empty:
                    raise ValueError("Silver weekly not found or empty.")
                w["stratum"] = w.get("stratum", "none")
                mf = build_monthly_rollforward(
                    w, asof=asof, weights=(wA, wB, wC), region="US", stratum=None
                )
                st.write(f"Gold step - Monthly rollforward shape: {mf.shape}")
                st.write(f"Gold step - Monthly rollforward columns: {list(mf.columns)}")
                st.write(f"Gold step - Monthly rollforward head: {mf.head(3).to_dict()}")
                _write_parquet(mf, DATA["gold_roll"])
                # capacity optional
                try:
                    cap = _read_parquet(DATA["silver_capacity"])
                    k = compute_kpis(mf, cap)
                except Exception:
                    k = compute_kpis(mf, None)  # type: ignore
                _write_parquet(k, DATA["gold_kpis"])
                st.success("Gold built ✅")
            except Exception as e:
                st.error(f"Gold build failed: {e}")

        if show_previews:
            st.caption("Monthly Rollforward Preview")
            # Add manual refresh button to bypass cache
            if st.button("🔄 Refresh Preview", key="refresh_gold"):
                st.cache_data.clear()
            preview_data = _read_parquet(DATA["gold_roll"])
            st.write(f"Preview - Gold data shape: {preview_data.shape}")
            st.write(f"Preview - Gold data path: {_p(DATA['gold_roll'])}")
            st.write(f"Preview - Gold data columns: {list(preview_data.columns)}")
            if not preview_data.empty:
                st.dataframe(preview_data.head(50), use_container_width=True)
            else:
                st.warning("No gold data found for preview. File may not exist or be empty.")
                st.info("Try clicking '🔄 Refresh Preview' to clear cache and reload data.")

    # -------- 3) Accruals + Excel --------
    with tab3:
        st.subheader("Calculate Accruals & Generate Excel Pack")
        out_excel = st.text_input("Excel output path", value=DATA["out_excel"])
        if st.button("Run Accruals + Excel") or run_all:
            try:
                roll = _read_parquet(DATA["gold_roll"])
                kpis = _read_parquet(DATA["gold_kpis"])
                st.write(f"Accruals step - Roll data shape: {roll.shape}")
                st.write(f"Accruals step - Roll data path: {_p(DATA['gold_roll'])}")
                st.write(f"Accruals step - Roll data columns: {list(roll.columns)}")
                if roll.empty:
                    raise ValueError("Monthly rollforward not found or empty.")
                ai = AccrualInputs(
                    wacog_per_mmbtu=float(wacog),
                    bcf_to_mmbtu_factor=DEFAULT_BCF_TO_MMBTU,
                    tariff_fixed_monthly=float(tariff_fixed),
                    tariff_injection_per_mmbtu=float(tariff_inj),
                    tariff_withdrawal_per_mmbtu=float(tariff_wd),
                    scenario_band=float(band),
                    penalty_probability=0.0,
                    penalty_amount=0.0,
                )
                accr = calc_accruals(roll, ai)
                _write_parquet(accr, DATA["gold_accruals"])
                _p(out_excel).parent.mkdir(parents=True, exist_ok=True)
                write_close_pack(
                    roll, kpis, accr,
                    assumptions={
                        "wacog_per_mmbtu": wacog,
                        "tariff_fixed": tariff_fixed,
                        "tariff_injection": tariff_inj,
                        "tariff_withdrawal": tariff_wd,
                        "scenario_band": band
                    },
                    out_path=_p(out_excel)
                )
                st.success("Accruals calculated & Excel pack written ✅")
                with open(_p(out_excel), "rb") as f:
                    st.download_button(
                        "Download Excel Pack",
                        data=f, file_name=Path(out_excel).name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Accruals/Excel failed: {e}")

        if show_previews:
            st.caption("Accruals Preview")
            # Add manual refresh button to bypass cache
            if st.button("🔄 Refresh Preview", key="refresh_accruals"):
                st.cache_data.clear()
            accruals_data = _read_parquet(DATA["gold_accruals"])
            st.write(f"Preview - Accruals data shape: {accruals_data.shape}")
            st.write(f"Preview - Accruals data path: {_p(DATA['gold_accruals'])}")
            st.write(f"Preview - Accruals data columns: {list(accruals_data.columns)}")
            if not accruals_data.empty:
                st.dataframe(accruals_data.head(50), use_container_width=True)
            else:
                st.warning("No accruals data found for preview. File may not exist or be empty.")
                st.info("Try clicking '🔄 Refresh Preview' to clear cache and reload data.")

    # -------- 4) Narratives --------
    with tab4:
        st.subheader("Generate CFO & Ops Narratives")
        ztxt = st.text_input("Z-score phrasing", value="near the 5-year average")
        dom = st.text_input("Dominant method", value="Method C (Ops)")
        why = st.text_input("Rationale", value="recent nominations/injections during the gap window")
        hotspot_region = st.text_input("Hotspot region", value="US")
        hotspot_stratum = st.text_input("Hotspot stratum", value="none")
        hotspot_driver = st.text_input("Hotspot driver", value="South-Central salt variability")
        nom_adjust_bcf = st.number_input("Nomination adj (bcf)", value=0.10, step=0.01)
        scen = st.text_input("Scenario name", value="cold-snap")
        out_dir = st.text_input("Output directory", value=DATA["out_dir"])

        do_narr = st.button("Build Narratives") or run_all
        if do_narr:
            try:
                roll = _read_parquet(DATA["gold_roll"])
                kpis = _read_parquet(DATA["gold_kpis"])
                accr = _read_parquet(DATA["gold_accruals"])
                
                # Debug info for narratives
                st.write(f"Narratives step - Roll data shape: {roll.shape}")
                st.write(f"Narratives step - Roll data path: {_p(DATA['gold_roll'])}")
                st.write(f"Narratives step - Roll data columns: {list(roll.columns)}")
                st.write(f"Narratives step - Roll data head: {roll.head(3).to_dict()}")
                
                if roll.empty:
                    raise ValueError("Monthly rollforward not found or empty.")
                
                # Safe month_end extraction with better error handling
                if len(roll) == 0:
                    raise ValueError("Roll DataFrame is empty")
                
                month_end_col = roll.get("month_end")
                if month_end_col is None:
                    raise ValueError("Column 'month_end' not found in roll data")
                
                if len(month_end_col) == 0:
                    raise ValueError("month_end column is empty")
                
                me = pd.to_datetime(month_end_col.iloc[0]).date()
                st.write(f"Narratives step - Extracted month_end: {me}")
                
                ni = build_narrative_inputs(
                    roll=roll, kpis=kpis, accruals=accr,
                    weights=(wA, wB, wC), band_pct=float(band),
                    zscore_txt=ztxt, dominant_method=dom, rationale=why,
                    hotspot_region=hotspot_region, hotspot_stratum=hotspot_stratum, hotspot_driver=hotspot_driver,
                    nom_adjust_bcf=float(nom_adjust_bcf), scenario_name=scen,
                    tariff_inj=float(tariff_inj), tariff_wd=float(tariff_wd)
                )
                cfo = cfo_summary(ni)
                ops = ops_summary(ni)
                _p(out_dir).mkdir(parents=True, exist_ok=True)
                p1 = _p(out_dir) / f"narrative_cfo_{me}.md"
                p2 = _p(out_dir) / f"narrative_ops_{me}.md"
                p1.write_text(cfo, encoding="utf-8")
                p2.write_text(ops, encoding="utf-8")
                st.success("Narratives written ✅")
                st.download_button("Download CFO Narrative", data=cfo, file_name=p1.name, mime="text/markdown")
                st.download_button("Download Ops Narrative", data=ops, file_name=p2.name, mime="text/markdown")
                with st.expander("Preview CFO Narrative"):
                    st.markdown(cfo)
                with st.expander("Preview Ops Narrative"):
                    st.markdown(ops)
            except Exception as e:
                st.error(f"Narratives failed: {e}")
                st.error(f"Error type: {type(e).__name__}")
                import traceback
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
