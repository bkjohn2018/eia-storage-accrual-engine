"""Test CLI entrypoints to prevent regressions."""

import subprocess
import sys


def test_help_runs():
    """Test that CLI help command runs successfully."""
    # Use module form to avoid script resolution issues
    out = subprocess.run(
        [sys.executable, "-c", 
         "import sys; sys.path.insert(0, 'src'); from eia_sa.cli.app import build_parser; p = build_parser(); p.print_help()"], 
        capture_output=True, 
        text=True
    )
    assert out.returncode == 0
    assert "eia-sa" in out.stdout
