"""Data validation schemas for EIA Storage Accrual Engine."""

from typing import Optional, Dict, Any
import pandas as pd

from eia_sa.config import settings


# TODO: Re-implement with pandera when available
def validate_bronze_weekly_storage(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate bronze layer weekly storage data."""
    # Placeholder validation
    return {"valid": True, "record_count": len(df)}


def validate_bronze_capacity(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate bronze layer capacity data."""
    # Placeholder validation
    return {"valid": True, "record_count": len(df)}


def validate_silver_weekly_storage(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate silver layer weekly storage data."""
    # Placeholder validation
    return {"valid": True, "record_count": len(df)}


def validate_silver_capacity(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate silver layer capacity data."""
    # Placeholder validation
    return {"valid": True, "record_count": len(df)}


def validate_gold_monthly_storage_rollforward(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate gold layer monthly storage rollforward."""
    # Placeholder validation
    return {"valid": True, "record_count": len(df)}


def validate_gold_monthly_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate gold layer monthly KPIs."""
    # Placeholder validation
    return {"valid": True, "record_count": len(df)}


def validate_gold_accruals(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate gold layer accruals."""
    # Placeholder validation
    return {"valid": True, "record_count": len(df)}


# Schema definitions for reference (not used for validation yet)
BRONZE_WEEKLY_STORAGE_COLUMNS = [
    "period", "duoarea", "area_name", "product", "product_name",
    "process", "process_name", "series", "series_description", "value", "units"
]

BRONZE_CAPACITY_COLUMNS = [
    "period", "duoarea", "area_name", "product", "product_name",
    "process", "process_name", "series", "series_description", "value", "units"
]

SILVER_WEEKLY_STORAGE_COLUMNS = [
    "date_reported", "region", "stratum", "working_gas_bcf", 
    "delta_week_bcf", "five_year_avg_bcf"
]

SILVER_CAPACITY_COLUMNS = [
    "region", "stratum", "year", "working_capacity_bcf", "design_capacity_bcf"
]

GOLD_MONTHLY_STORAGE_ROLLFORWARD_COLUMNS = [
    "month_end", "region", "stratum", "beg_working_gas_bcf",
    "est_injections_bcf", "est_withdrawals_bcf", "end_working_gas_bcf",
    "gap_days", "estimation_method"
]

GOLD_MONTHLY_KPIS_COLUMNS = [
    "month_end", "region", "stratum", "working_gas_bcf", "working_capacity_bcf",
    "percent_of_working_capacity", "zscore_vs_5yr", "days_of_cover"
]

GOLD_ACCRUALS_COLUMNS = [
    "month_end", "region", "stratum", "scenario", "inventory_accrual",
    "variable_fees", "fixed_demand", "total_accrual", "wacog_per_mmbtu", "tariff_rates"
]
