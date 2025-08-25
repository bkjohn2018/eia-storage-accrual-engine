#!/usr/bin/env python3
"""Test script to verify import structure."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    print("Testing imports...")
    
    # Test basic package import
    import eia_sa
    print("✅ eia_sa package imported successfully")
    
    # Test config import
    from eia_sa.config import Settings
    print("✅ Settings class imported successfully")
    
    # Test logging import
    from eia_sa.utils.logging import setup_logging, get_logger
    print("✅ Logging module imported successfully")
    
    # Test EIA client import
    from eia_sa.ingest.eia_client import EIAClient
    print("✅ EIAClient imported successfully")
    
    # Test schemas import
    from eia_sa.transform.schemas import validate_bronze_weekly_storage
    print("✅ Schemas module imported successfully")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
