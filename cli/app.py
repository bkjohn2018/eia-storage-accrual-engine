"""CLI application for EIA Storage Accrual Engine."""

import argparse
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from eia_sa.config import settings
from eia_sa.utils.logging import setup_logging, get_logger
from eia_sa.ingest.eia_client import EIAClient

# Initialize logging
setup_logging()
logger = get_logger(__name__)

def create_parser():
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="EIA Storage Accrual Engine - Production-grade natural gas storage analysis"
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest weekly command
    weekly_parser = subparsers.add_parser('ingest-weekly', help='Ingest weekly working gas storage data')
    weekly_parser.add_argument('--start', '-s', default=settings.default_start_date, help='Start date (YYYY-MM-DD)')
    weekly_parser.add_argument('--end', '-e', default=settings.default_end_date, help='End date (YYYY-MM-DD)')
    weekly_parser.add_argument('--regions', '-r', nargs='*', help='Specific regions to ingest')
    
    # Ingest capacity command
    capacity_parser = subparsers.add_parser('ingest-capacity', help='Ingest storage capacity data')
    capacity_parser.add_argument('--year', '-y', type=int, help='Year for capacity data')
    
    # Build silver command
    silver_parser = subparsers.add_parser('build-silver', help='Build silver layer tables')
    
    # Build gold command
    gold_parser = subparsers.add_parser('build-gold', help='Build gold layer tables')
    gold_parser.add_argument('--asof', help='As-of date (YYYY-MM-DD)')
    gold_parser.add_argument('--weights', nargs=3, type=float, help='Estimator weights (A B C)')
    
    # Calculate accruals command
    accruals_parser = subparsers.add_parser('calc-accruals', help='Calculate month-end accruals')
    accruals_parser.add_argument('--asof', help='As-of date (YYYY-MM-DD)')
    accruals_parser.add_argument('--wacog', type=float, default=settings.default_wacog_per_mmbtu, help='WACOG per MMBtu')
    accruals_parser.add_argument('--tariff-fixed', type=float, default=settings.default_tariff_fixed_monthly, help='Fixed monthly tariff')
    accruals_parser.add_argument('--tariff-inj', type=float, default=settings.default_tariff_injection, help='Injection tariff per MMBtu')
    accruals_parser.add_argument('--tariff-wd', type=float, default=settings.default_tariff_withdrawal, help='Withdrawal tariff per MMBtu')
    accruals_parser.add_argument('--scenario-band', type=float, default=settings.default_scenario_band, help='Scenario band (±X%)')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch Streamlit dashboard')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    return parser


def ingest_weekly(start_date: str, end_date: str, regions: Optional[List[str]] = None):
    """Ingest weekly working gas storage data from EIA API."""
    try:
        logger.info("Starting weekly storage data ingestion", 
                   start_date=start_date, end_date=end_date, regions=regions)
        
        # Initialize EIA client
        client = EIAClient()
        
        # Fetch weekly storage data
        df = client.fetch_weekly_storage(start_date, end_date, regions)
        
        if df.empty:
            logger.error("No weekly storage data retrieved")
            sys.exit(1)
        
        # Save raw data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client.save_raw_data(
            {"response": {"data": df.to_dict('records')}}, 
            f"weekly_storage_{start_date}_{end_date}_{timestamp}"
        )
        
        # Save parquet data
        client.save_parquet_data(
            df, 
            f"weekly_storage_{start_date}_{end_date}_{timestamp}"
        )
        
        # Generate summary
        summary = client.get_data_summary(df)
        logger.info("Weekly storage ingestion complete", summary=summary)
        
        print(f"✅ Successfully ingested {summary['record_count']} weekly storage records")
        print(f"📊 Date range: {summary['date_range']}")
        print(f"🌍 Regions: {summary['regions']}")
        
    except Exception as e:
        logger.error("Weekly storage ingestion failed", error=str(e))
        print(f"❌ Ingestion failed: {str(e)}")
        sys.exit(1)


def ingest_capacity(year: Optional[int] = None):
    """Ingest storage capacity data from EIA API."""
    try:
        logger.info("Starting capacity data ingestion", year=year)
        
        # Initialize EIA client
        client = EIAClient()
        
        # Fetch capacity data
        df = client.fetch_capacity_data(year)
        
        if df.empty:
            logger.error("No capacity data retrieved")
            sys.exit(1)
        
        # Save raw data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        year_str = str(year) if year else "current"
        client.save_raw_data(
            {"response": {"data": df.to_dict('records')}}, 
            f"capacity_{year_str}_{timestamp}"
        )
        
        # Save parquet data
        client.save_parquet_data(df, f"capacity_{year_str}_{timestamp}")
        
        # Generate summary
        summary = client.get_data_summary(df)
        logger.info("Capacity ingestion complete", summary=summary)
        
        print(f"✅ Successfully ingested {summary['record_count']} capacity records")
        print(f"📊 Year: {year_str}")
        
    except Exception as e:
        logger.error("Capacity ingestion failed", error=str(e))
        print(f"❌ Ingestion failed: {str(e)}")
        sys.exit(1)


def build_silver():
    """Build silver layer tables from bronze data."""
    try:
        logger.info("Starting silver layer build")
        print("🔧 Building silver layer tables...")
        
        # TODO: Implement silver layer transformation
        print("⚠️  Silver layer build not yet implemented")
        print("💡 This will normalize weekly storage and capacity data")
        
    except Exception as e:
        logger.error("Silver layer build failed", error=str(e))
        print(f"❌ Build failed: {str(e)}")
        sys.exit(1)


def build_gold(asof: Optional[str] = None, weights: Optional[List[float]] = None):
    """Build gold layer tables from silver data."""
    try:
        logger.info("Starting gold layer build", asof=asof, weights=weights)
        print(f"🔧 Building gold layer tables as of {asof}...")
        
        # TODO: Implement gold layer transformation
        print("⚠️  Gold layer build not yet implemented")
        print("💡 This will create monthly rollforward and KPIs")
        
    except Exception as e:
        logger.error("Gold layer build failed", error=str(e))
        print(f"❌ Build failed: {str(e)}")
        sys.exit(1)


def calc_accruals(asof: str, wacog: float = None, tariff_fixed: float = None, tariff_inj: float = None, tariff_wd: float = None, scenario_band: float = None):
    """Calculate month-end accruals."""
    try:
        logger.info("Starting accrual calculation", 
                   asof=asof, wacog=wacog, tariff_fixed=tariff_fixed,
                   tariff_inj=tariff_inj, tariff_wd=tariff_wd,
                   scenario_band=scenario_band)
        
        print(f"💰 Calculating accruals as of {asof}...")
        print(f"📊 WACOG: ${wacog:.2f}/MMBtu")
        print(f"💵 Fixed tariff: ${tariff_fixed:,.0f}/month")
        print(f"📥 Injection tariff: ${tariff_inj:.3f}/MMBtu")
        print(f"📤 Withdrawal tariff: ${tariff_wd:.3f}/MMBtu")
        print(f"📈 Scenario band: ±{scenario_band:.1%}")
        
        # TODO: Implement accrual calculation
        print("⚠️  Accrual calculation not yet implemented")
        print("💡 This will calculate inventory + storage fees")
        
    except Exception as e:
        logger.error("Accrual calculation failed", error=str(e))
        print(f"❌ Calculation failed: {str(e)}")
        sys.exit(1)


def dashboard():
    """Launch the Streamlit dashboard."""
    try:
        logger.info("Launching Streamlit dashboard")
        print("🚀 Launching Streamlit dashboard...")
        
        # TODO: Implement dashboard launch
        print("⚠️  Dashboard launch not yet implemented")
        print("💡 This will start the Streamlit app")
        
    except Exception as e:
        logger.error("Dashboard launch failed", error=str(e))
        print(f"❌ Launch failed: {str(e)}")
        sys.exit(1)


def status():
    """Show system status and configuration."""
    try:
        logger.info("Showing system status")
        
        print("🔋 EIA Storage Accrual Engine - Status")
        print("=" * 50)
        
        # Configuration
        print("📋 Configuration:")
        print(f"   EIA API Key: {'✅ Configured' if settings.eia_api_key else '❌ Not configured'}")
        print(f"   Base URL: {settings.eia_base_url}")
        print(f"   Data paths:")
        print(f"     Bronze: {settings.data_bronze_path}")
        print(f"     Gold: {settings.data_gold_path}")
        print(f"     Outputs: {settings.outputs_path}")
        
        # Estimator weights
        print(f"   Estimator weights: {settings.estimator_weights_dict}")
        
        # Check data files
        print("\n📊 Data Status:")
        bronze_path = Path(settings.data_bronze_path)
        if bronze_path.exists():
            bronze_files = list(bronze_path.glob("*.parquet"))
            print(f"   Bronze files: {len(bronze_files)}")
            for f in bronze_files[:5]:  # Show first 5
                print(f"     • {f.name}")
            if len(bronze_files) > 5:
                print(f"     ... and {len(bronze_files) - 5} more")
        else:
            print("   Bronze files: No data directory found")
        
        print("\n🎯 Ready for operations!")
        
    except Exception as e:
        logger.error("Status check failed", error=str(e))
        print(f"❌ Status check failed: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'ingest-weekly':
            ingest_weekly(args.start, args.end, args.regions)
        elif args.command == 'ingest-capacity':
            ingest_capacity(args.year)
        elif args.command == 'build-silver':
            build_silver()
        elif args.command == 'build-gold':
            build_gold(args.asof, args.weights)
        elif args.command == 'calc-accruals':
            calc_accruals(args.asof, args.wacog, args.tariff_fixed, args.tariff_inj, args.tariff_wd, args.scenario_band)
        elif args.command == 'dashboard':
            dashboard()
        elif args.command == 'status':
            status()
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
