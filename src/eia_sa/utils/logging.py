"""Logging configuration for EIA Storage Accrual Engine."""

from __future__ import annotations
import logging
import os

# Try to read log level from env or (optionally) config, but don't fail if missing.
_LEVEL = os.getenv("EIA_SA_LOG_LEVEL", "INFO").upper()
try:
    from eia_sa.config import get_settings
    _cfg = get_settings()
    lvl = getattr(_cfg, "log_level", None)
    if isinstance(lvl, str):
        _LEVEL = lvl.upper()
except Exception:
    pass

def _configure_root() -> logging.Logger:
    logger = logging.getLogger("eia_sa")
    if not logger.handlers:
        h = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)
    logger.setLevel(_LEVEL)
    return logger

_root = _configure_root()

def get_logger(name: str | None = None) -> logging.Logger:
    return _root if not name else logging.getLogger(f"eia_sa.{name}")


def log_function_call(func_name: str, **kwargs: Any) -> Dict[str, Any]:
    """Create a standardized log context for function calls."""
    from datetime import datetime
    return {
        "function": func_name,
        "parameters": kwargs,
        "timestamp": datetime.now().isoformat(),
    }


def log_api_request(endpoint: str, status_code: int, response_time: float, **kwargs: Any) -> Dict[str, Any]:
    """Create a standardized log context for API requests."""
    from datetime import datetime
    return {
        "api_endpoint": endpoint,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "timestamp": datetime.now().isoformat(),
        **kwargs,
    }


def log_data_processing(
    layer: str, 
    record_count: int, 
    processing_time: float, 
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a standardized log context for data processing."""
    from datetime import datetime
    return {
        "data_layer": layer,
        "record_count": record_count,
        "processing_time_ms": round(processing_time * 1000, 2),
        "timestamp": datetime.now().isoformat(),
        **kwargs,
    }


def log_accrual_calculation(
    month_end: str,
    region: str,
    total_accrual: float,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a standardized log context for accrual calculations."""
    return {
        "month_end": month_end,
        "region": region,
        "total_accrual": round(total_accrual, 2),
        "timestamp": datetime.now().isoformat(),
        **kwargs,
    }
