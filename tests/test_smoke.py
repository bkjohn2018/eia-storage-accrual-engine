def test_imports():
    import eia_sa
    import eia_sa.dashboard.app
    from eia_sa.transform import normalize_weekly, build_gold
    from eia_sa.accrual import calculator, kpis
    assert True

def test_cli_help():
    from eia_sa.cli import app
    parser = app.build_parser()
    helptext = parser.format_help()
    assert "build-silver" in helptext
    assert "build-gold" in helptext
    assert "calc-accruals" in helptext
    assert "narratives" in helptext
