#!/usr/bin/env python3
"""Test narratives module."""

import sys
sys.path.insert(0, 'src')

try:
    from eia_sa.analysis.narratives import cfo_summary, ops_summary
    print("✅ Narratives module imported successfully")
    
    # Test the functions exist
    print(f"✅ cfo_summary function: {cfo_summary}")
    print(f"✅ ops_summary function: {ops_summary}")
    
except Exception as e:
    print(f"❌ Error importing narratives: {e}")
    sys.exit(1)
