#!/usr/bin/env python3
"""
Test script for natural gas storage data from EIA API
"""

from eia_analysis import EIAEnergyAnalyzer
import os

def main():
    """Test natural gas storage data retrieval"""
    print("🔋 Natural Gas Storage Data Test")
    print("=" * 50)
    
    # Initialize analyzer with API key from environment
    api_key = os.getenv('EIA_API_KEY')
    if not api_key:
        print("❌ EIA_API_KEY environment variable not set")
        print("   Please set EIA_API_KEY in your .env file or environment")
        return
    
    analyzer = EIAEnergyAnalyzer(api_key=api_key)
    
    print(f"✅ API Key configured: {api_key[:10]}...")
    
    # Test natural gas storage data
    print("\n📊 Testing Natural Gas Storage Data...")
    print("-" * 40)
    
    # Get natural gas storage data from 2010 to present
    storage_df = analyzer.get_natural_gas_storage(start_date="2010-01-01", end_date="2025-08-15")
    
    if not storage_df.empty:
        print(f"✅ Successfully retrieved natural gas storage data!")
        print(f"   Data points: {len(storage_df)}")
        print(f"   Date range: {storage_df['period'].min()} to {storage_df['period'].max()}")
        print(f"   Columns: {list(storage_df.columns)}")
        
        # Show first few rows
        print("\n📋 First 5 rows of data:")
        print(storage_df.head())
        
        # Generate statistics
        stats = analyzer.generate_summary_stats(storage_df, "Natural Gas Storage")
        print("\n📈 Summary Statistics:")
        for key, value in stats.items():
            if key == 'date_range':
                print(f"   {key}: {value}")
            elif isinstance(value, float):
                print(f"   {key}: {value:,.2f}")
            else:
                print(f"   {key}: {value}")
        
        # Save data
        filename = "natural_gas_storage_2010_2025.csv"
        analyzer.save_data_to_csv(storage_df, filename)
        
        # Try to plot the data
        print("\n📊 Generating storage plot...")
        try:
            analyzer.plot_energy_consumption(storage_df, "Natural Gas Storage Over Time")
        except Exception as e:
            print(f"⚠️  Plotting error: {e}")
            print("   Data saved to CSV for manual analysis")
        
    else:
        print("❌ Failed to retrieve natural gas storage data")
    
    # Test other natural gas data types
    print("\n🌍 Testing Other Natural Gas Data...")
    print("-" * 40)
    
    data_types = ['production', 'consumption', 'prices']
    for data_type in data_types:
        print(f"\n📊 Testing {data_type} data...")
        try:
            df = analyzer.get_natural_gas_data(data_type, start_date="2020-01-01", end_date="2025-08-15")
            if not df.empty:
                print(f"   ✅ {data_type}: {len(df)} data points")
                filename = f"natural_gas_{data_type}_2020_2025.csv"
                analyzer.save_data_to_csv(df, filename)
            else:
                print(f"   ❌ {data_type}: No data")
        except Exception as e:
            print(f"   ❌ {data_type}: Error - {e}")
    
    print("\n🎯 Test complete!")
    print("💾 Check the generated CSV files for your data")

if __name__ == "__main__":
    main()
