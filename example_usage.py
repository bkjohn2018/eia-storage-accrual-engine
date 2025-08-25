#!/usr/bin/env python3
"""
Simple example of using the EIA Energy Analyzer
"""

from eia_analysis import EIAEnergyAnalyzer
import os

def main():
    """Demonstrate basic EIA analysis functionality"""
    print("🔋 EIA Energy Analysis - Simple Example")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('EIA_API_KEY')
    if api_key:
        print("✅ EIA API key found")
    else:
        print("⚠️  No EIA API key found. Using limited functionality.")
        print("   Set EIA_API_KEY environment variable for full access.")
    
    # Initialize analyzer
    analyzer = EIAEnergyAnalyzer(api_key=api_key)
    
    # Example 1: Basic data retrieval
    print("\n📊 Example 1: Basic Data Retrieval")
    print("-" * 30)
    
    try:
        # Get recent energy consumption data
        consumption_data = analyzer.get_energy_consumption()
        
        if not consumption_data.empty:
            print(f"✅ Retrieved {len(consumption_data)} consumption data points")
            print(f"📅 Date range: {consumption_data['period'].min()} to {consumption_data['period'].max()}")
            print(f"📊 Sample values: {consumption_data['value'].head(3).tolist()}")
        else:
            print("❌ No consumption data retrieved")
            
    except Exception as e:
        print(f"❌ Error retrieving consumption data: {e}")
    
    # Example 2: Generate statistics
    print("\n📈 Example 2: Statistical Analysis")
    print("-" * 30)
    
    try:
        if 'consumption_data' in locals() and not consumption_data.empty:
            stats = analyzer.generate_summary_stats(consumption_data, "Energy Consumption")
            
            print("📊 Summary Statistics:")
            for key, value in stats.items():
                if key == 'date_range':
                    print(f"   {key}: {value}")
                elif isinstance(value, float):
                    print(f"   {key}: {value:,.2f}")
                else:
                    print(f"   {key}: {value}")
        else:
            print("⚠️  No data available for statistics")
            
    except Exception as e:
        print(f"❌ Error generating statistics: {e}")
    
    # Example 3: Data export
    print("\n💾 Example 3: Data Export")
    print("-" * 30)
    
    try:
        if 'consumption_data' in locals() and not consumption_data.empty:
            filename = "example_energy_data.csv"
            analyzer.save_data_to_csv(consumption_data, filename)
            
            # Verify file was created
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"✅ Data exported to {filename} ({file_size} bytes)")
            else:
                print("❌ File export failed")
        else:
            print("⚠️  No data available for export")
            
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
    
    # Example 4: Custom analysis
    print("\n🔍 Example 4: Custom Analysis")
    print("-" * 30)
    
    try:
        if 'consumption_data' in locals() and not consumption_data.empty:
            # Calculate some custom metrics
            total_consumption = consumption_data['value'].sum()
            avg_consumption = consumption_data['value'].mean()
            peak_consumption = consumption_data['value'].max()
            low_consumption = consumption_data['value'].min()
            
            print("🔬 Custom Metrics:")
            print(f"   Total Consumption: {total_consumption:,.2f} MWh")
            print(f"   Average Consumption: {avg_consumption:,.2f} MWh")
            print(f"   Peak Consumption: {peak_consumption:,.2f} MWh")
            print(f"   Low Consumption: {low_consumption:,.2f} MWh")
            
            # Calculate efficiency ratio (if we had price data)
            efficiency_ratio = avg_consumption / peak_consumption if peak_consumption > 0 else 0
            print(f"   Efficiency Ratio: {efficiency_ratio:.2%}")
        else:
            print("⚠️  No data available for custom analysis")
            
    except Exception as e:
        print(f"❌ Error in custom analysis: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Example complete!")
    print("\n💡 Next steps:")
    print("   1. Get an EIA API key for full functionality")
    print("   2. Explore the Jupyter notebook for interactive analysis")
    print("   3. Customize the analysis for your specific needs")
    print("   4. Add more data sources and analysis methods")

if __name__ == "__main__":
    main()
