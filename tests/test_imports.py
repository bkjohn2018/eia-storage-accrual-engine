"""Test basic imports to prevent regressions."""

def test_pkg_import():
    """Test that the main package can be imported."""
    import eia_sa  # noqa: F401


def test_cli_import():
    """Test that CLI components can be imported."""
    from eia_sa.cli.app import build_parser
    p = build_parser()
    assert p.prog == "eia-sa"
