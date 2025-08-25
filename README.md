# 📦 EIA Storage Accrual Engine

End-to-end pipeline and dashboard for energy accountants to estimate storage accruals and generate CFO/Operations narratives.

---

## 🚀 Quickstart

```bash
# clone repo
git clone https://github.com/bkjohn2018/eia-storage-accrual-engine.git
cd eia-storage-accrual-engine

# install dependencies
pip install -r requirements.txt  # or conda env create -f environment.yml

# seed test data
python scripts/seed_bronze.py

# run dashboard
$env:PYTHONPATH="src"; streamlit run src/eia_sa/dashboard/app.py
```

---

## 🧩 Workflow

**Silver** → Normalize weekly + capacity data

**Gold** → Build monthly rollforward + KPIs

**Accruals** → Calculate accruals + Excel close pack

**Narratives** → Generate CFO + Ops markdown

---

## 📊 Outputs

**Excel pack** → `outputs/monthly_close_pack.xlsx`

**Narratives** → `outputs/narrative_cfo_YYYY-MM-DD.md` + `outputs/narrative_ops_YYYY-MM-DD.md`

---

## 🧪 Tests

Run smoke tests:

```bash
pytest -q
```

---

## 📌 Version

Current release: **v1.0.0**

See [CHANGELOG.md](CHANGELOG.md)
