# Monthly Close Standard Operating Procedure
**EIA Storage Accrual Engine**

## 1) Purpose

Provide a repeatable, auditable process to estimate month-end natural gas storage balances and storage-related accruals (inventory, variable fees, fixed demand), using EIA weekly data + optional ops inputs. Output: an Excel close pack and narratives for CFO & Operations.

## 2) Scope

**Entities**: Company-owned/contracted gas storage exposures covered by our models.

**Periodicity**: Monthly close; weekly refresh allowed.

**Data horizon**: 2010 → present EIA history + current month activity.

## 3) Roles & Responsibilities

**Data/Analytics (you/owner)**: run pipeline, validate results, publish close pack & dashboard.

**Accounting**: review tables, post JEs, track variances/true-ups.

**Operations**: provide gap-window nominations/injection/withdrawal guidance (`data/ops/ops_volumes.csv`) and confirm outliers.

**Controller/CFO**: approve final accruals and narrative.

## 4) Inputs (required/optional)

### Required
- `data/bronze/eia_weekly_storage.parquet` (from EIA ingest)
- `data/bronze/eia_capacity.parquet` (optional but recommended)
- Assumptions for accruals: `wacog_per_mmbtu`, tariffs (fixed, inj, wd), scenario band

### Optional
- `data/ops/ops_volumes.csv` with columns: `date`, `region`, `stratum`, `inj_bcf`, `wd_bcf`

## 5) Definitions

**Method A** – Last-4-weeks average daily net change × gap days (Fri→month-end).

**Method B** – Seasonality model (month dummies) → daily rate × gap days.

**Method C** – Ops-anchored net injections/withdrawals over the gap window.

**Blended Estimate** – default weights C:A:B = 0.5 : 0.3 : 0.2 (configurable).

**Scenario band** – by default ±10% on the Base accrual.

## 6) Pre-Close Timeline (T-3 to T+5)

**T-3 to T-1**: Ingest/refresh EIA weekly; collect ops gap-window file; validate.

**T-1**: Dry run gold + accruals; sanity checks & narratives.

**T (close day)**: Final run; produce Excel; internal review; CFO/Controller sign-off.

**T+3**: Book true-ups as new statements post; update backtest file.

**T+5**: Backtest & bias review; update README notes if thresholds exceeded.

## 7) End-to-End Procedure (commands assume repo root)

### Step 1 — Build Silver (normalize EIA)
```bash
eia-sa build-silver \
  --weekly-bronze data/bronze/eia_weekly_storage.parquet \
  --capacity-bronze data/bronze/eia_capacity.parquet \
  --weekly-silver-out data/silver/eia_weekly_storage.parquet \
  --capacity-silver-out data/silver/eia_capacity.parquet
```

**Checks**
- No null `date_reported`.
- Non-negative `working_gas_bcf`.
- `delta_week_bcf` computed.

### Step 2 — Build Gold (rollforward + projection)
```bash
eia-sa build-gold \
  --asof YYYY-MM-DD \
  --weights 0.3,0.2,0.5 \
  --weekly-silver data/silver/eia_weekly_storage.parquet \
  --capacity-silver data/silver/eia_capacity.parquet \
  --monthly-roll-out data/gold/monthly_storage_rollforward.parquet \
  --kpis-out data/gold/monthly_kpis.parquet \
  --region US \
  --stratum none
```

**Outputs**
- `monthly_storage_rollforward.parquet` with: `beg_working_gas_bcf`, `est_injections_bcf`, `est_withdrawals_bcf`, `gap_delta_bcf`, `end_working_gas_bcf`.
- `monthly_kpis.parquet` with `%_of_working_capacity`, `zscore_vs_5yr` (placeholder), etc.

**Validation**
- Gap days ≥ 0 and ≤ 6 (typically).
- Sign of `est_injections_bcf`/`est_withdrawals_bcf` correct.
- If `ops_volumes.csv` present, `gap_delta_bcf` ≈ ops net within reason.

### Step 3 — Calculate Accruals + Excel Close Pack
```bash
eia-sa calc-accruals \
  --asof YYYY-MM-DD \
  --wacog 3.25 \
  --tariff-fixed 120000 \
  --tariff-inj 0.02 \
  --tariff-wd 0.03 \
  --scenario-band 0.10 \
  --monthly-roll data/gold/monthly_storage_rollforward.parquet \
  --kpis-path data/gold/monthly_kpis.parquet \
  --out-excel outputs/monthly_close_pack.xlsx
```

**Excel sheets (must exist)**
- **Rollforward** (beg, inj, wd, gap, end)
- **KPIs** (% capacity, z-score placeholder, etc.)
- **Accruals** (inventory value, variable fees, fixed demand, total low/base/high)
- **Assumptions** (WACOG, tariffs, scenario band)
- **Audit_Log** (UTC timestamp; add API params if you wire them in)

### Step 4 — Narrative Generation (see templates below)

Populate CFO + Ops narratives using the gold/accrual fields.

Paste narratives into the close memo / attach to Excel or export from dashboard.

### Step 5 — Review & Sign-off

**Accounting**: tie-out balances, review scenario band, select Base unless a clearly better estimate exists; document rationale.

**Operations**: confirm gap-window assumptions and any expected penalties.

**Controller/CFO**: sign-off; choose final JE amounts (usually Base) and book.

## 8) Journal Entry Templates

**Inventory (if company owns working gas)**
```
Dr Inventory – Gas in Storage ............. $[inventory_accrual_base]
    Cr Accrued Liabilities / Gas Clearing .. $[inventory_accrual_base]
```

**Storage Fees**
```
Dr Storage Expense – Fixed Demand ......... $[fixed_demand]
Dr Storage Expense – Variable ............. $[variable_fees]
    Cr Accrued Liabilities ................. $[fixed_demand + variable_fees]
```

If penalties are probable and estimable, include:
```
Dr Storage Expense – Penalties ............ $[penalties_est]
    Cr Accrued Liabilities ................. $[penalties_est]
```

**Posting policy**
- Book Base scenario by default.
- Disclose ±band ($) in the close memo; if material, Management may adjust to Low/High.

## 9) Controls & Documentation (SOX-friendly)

**Reproducibility**: keep command line used + commit SHA in the close memo.

**Segregation**: analytics prepares; accounting reviews; controller approves.

**Evidence**: Excel close pack, ops file (if used), and method weights.

**Change control**: update weights or scenario bands only via PR with approval.

**Backups**: archive `data/gold/*.parquet` and Excel in period folder.

## 10) Variance & True-Up

When actual statements arrive (T+3/T+5), compute variance vs booked accrual:

**Driver categories**: (a) EIA projection error (A/B), (b) ops gap delta (C), (c) tariff mis-rate, (d) FX/conv.

Book true-up in current period unless material & policy requires prior-period adjustment.

Append to `docs/ANALYTICAL_NOTES.md` variance log.

## 11) Backtesting & Method Governance

Maintain `data/actuals/monthly_actuals.csv` when available.

Compute MAPE and signed bias by method & region; if bias > 15% over last 6 months, propose new weights via PR.

Record decision in `docs/ANALYTICAL_NOTES.md`.

## 12) Troubleshooting

**Empty gap delta**: missing ops file (C) and insufficient recent weeks—fallback to A only.

**Percent of capacity blank**: capacity parquet missing—re-ingest capacity.

**Excel missing sheets**: re-run `calc-accruals` and confirm write permissions to `outputs/`.

## 13) Definition of Done (Close Checklist)

- [ ] Gold rollforward built for asof month.
- [ ] Accruals computed with Low/Base/High.
- [ ] Excel close pack contains all five sheets.
- [ ] CFO/Ops narratives generated and attached.
- [ ] JE templates prepared; numbers tie to Excel.
- [ ] Controller/CFO sign-off captured.
- [ ] Prior month variance & true-up documented.

## Appendix A — CFO Narrative Template (Jinja-style)

```
As of {{ month_end }}, estimated working gas is **{{ end_bcf | round(0) }} Bcf**,
which is **{{ pct_capacity | round(1) }}% of working capacity**{{ " (capacity unavailable)" if pct_capacity is none else "" }}.
We used the **Base** scenario with blended estimator weights **C:A:B = {{ wC }}:{{ wA }}:{{ wB }}**,
projecting **{{ gap_days }}** gap day(s) from the last EIA Friday report.

**Accrual summary (USD):** Inventory **${{ inv_accrual | comma }}**, Variable fees **${{ var_fees | comma }}**,
Fixed demand **${{ fixed_demand | comma }}**, Penalties (expected) **${{ penalties | comma }}**.
Total Base accrual **${{ total_base | comma }}**, with sensitivity band ±{{ band_pct }}%
(**${{ total_low | comma }} – ${{ total_high | comma }}**).

Context: storage stands **{{ zscore_txt }}** relative to the 5-year average; risk this month is
primarily driven by **{{ risk_driver }}**. We expect any true-up to fall within the sensitivity band.
```

**Example variable bindings:**
`end_bcf`, `pct_capacity`, `wA`, `wB`, `wC`, `gap_days`, `inv_accrual`, `var_fees`, `fixed_demand`, `penalties`, `total_base`, `total_low`, `total_high`, `band_pct`, `zscore_txt`, `risk_driver`.

## Appendix B — Ops Narrative Template (Jinja-style)

```
For {{ month_end }}, projected **injections = {{ inj_bcf | round(2) }} Bcf** and
**withdrawals = {{ wd_bcf | round(2) }} Bcf** (net gap delta {{ gap_delta_bcf | round(2) }} Bcf).
The blended estimator emphasized **{{ dominant_method }}** due to {{ rationale }}.

Hotspots:
- Region: **{{ hotspot_region }}** ({{ hotspot_stratum }}).
  Driver: {{ hotspot_driver }}; Recommend adjusting nominations by **{{ nom_adjust_bcf | round(2) }} Bcf**
  under {{ scenario_name }} scenario.

Operational asks:
- Confirm ops file coverage for {{ gap_days }} gap day(s).
- Validate tariff assumptions (inj {{ tariff_inj }}, wd {{ tariff_wd }}).
- Flag any expected imbalance penalties beyond the base estimate.
```

## Appendix C — JE Working Block (copy/paste table)

| Account | Dr / (Cr) | Amount (USD) | Note |
|---------|-----------|--------------|------|
| Inventory – Gas in Storage | Dr | {{ inv_accrual }} | {{ month_end }} Base |
| Storage Expense – Fixed Demand | Dr | {{ fixed_demand }} | Tariff fixed |
| Storage Expense – Variable | Dr | {{ var_fees }} | Inj/Wd variable fees |
| Storage Expense – Penalties (expected) | Dr | {{ penalties }} | If probable & estimable |
| Accrued Liabilities / Gas Clearing | Cr | {{ total_base }} | Plug to match total |
