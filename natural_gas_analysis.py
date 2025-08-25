#!/usr/bin/env python3
"""
Comprehensive Natural Gas Analysis using EIA API
"""

from eia_analysis import EIAEnergyAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

def analyze_natural_gas_storage():
    """Analyze natural gas storage data"""
    print("🔋 Natural Gas Storage Analysis")
    print("=" * 50)
    
    # Initialize analyzer with API key from environment
    api_key = os.getenv('EIA_API_KEY')
    if not api_key:
        print("❌ EIA_API_KEY environment variable not set")
        print("   Please set EIA_API_KEY in your .env file or environment")
        return None
    
    analyzer = EIAEnergyAnalyzer(api_key=api_key)
    
    print(f"✅ API Key configured: {api_key[:10]}...")
    
    # Get natural gas storage data
    print("\n📊 Fetching natural gas storage data...")
    storage_df = analyzer.get_natural_gas_storage(start_date="2010-01-01", end_date="2025-08-15")
    
    if storage_df.empty:
        print("❌ No storage data retrieved")
        return None
    
    print(f"✅ Retrieved {len(storage_df)} storage data points")
    
    # Data cleaning and preparation
    print("\n🧹 Cleaning and preparing data...")
    
    # Convert value to numeric
    if storage_df['value'].dtype == 'object':
        storage_df['value'] = pd.to_numeric(storage_df['value'], errors='coerce')
    
    # Remove any NaN values
    storage_df = storage_df.dropna(subset=['value'])
    
    # Convert period to datetime
    storage_df['period'] = pd.to_datetime(storage_df['period'])
    
    # Sort by period
    storage_df = storage_df.sort_values('period')
    
    print(f"   Clean data points: {len(storage_df)}")
    print(f"   Date range: {storage_df['period'].min().strftime('%Y-%m-%d')} to {storage_df['period'].max().strftime('%Y-%m-%d')}")
    print(f"   Value range: {storage_df['value'].min():.2f} to {storage_df['value'].max():.2f} BCF")
    
    return storage_df

def generate_storage_insights(storage_df):
    """Generate insights from storage data"""
    print("\n🔍 Generating Storage Insights...")
    print("-" * 40)
    
    # Basic statistics
    stats = {
        'Total Records': len(storage_df),
        'Average Storage': f"{storage_df['value'].mean():.2f} BCF",
        'Median Storage': f"{storage_df['value'].median():.2f} BCF",
        'Min Storage': f"{storage_df['value'].min():.2f} BCF",
        'Max Storage': f"{storage_df['value'].max():.2f} BCF",
        'Standard Deviation': f"{storage_df['value'].std():.2f} BCF",
        'Date Range': f"{storage_df['period'].min().strftime('%Y-%m-%d')} to {storage_df['period'].max().strftime('%Y-%m-%d')}"
    }
    
    print("📊 Basic Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Seasonal analysis
    print("\n🌍 Seasonal Analysis:")
    storage_df['year'] = storage_df['period'].dt.year
    storage_df['month'] = storage_df['period'].dt.month
    storage_df['week'] = storage_df['period'].dt.isocalendar().week
    
    # Monthly averages
    monthly_avg = storage_df.groupby('month')['value'].mean()
    print("   📅 Monthly Averages (BCF):")
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for month, avg in monthly_avg.items():
        print(f"      {month_names[month-1]}: {avg:.2f}")
    
    # Find peak and low storage periods
    peak_storage = storage_df.loc[storage_df['value'].idxmax()]
    low_storage = storage_df.loc[storage_df['value'].idxmin()]
    
    print(f"\n📈 Peak Storage: {peak_storage['value']:.2f} BCF on {peak_storage['period'].strftime('%Y-%m-%d')}")
    print(f"📉 Low Storage: {low_storage['value']:.2f} BCF on {low_storage['period'].strftime('%Y-%m-%d')}")
    
    return storage_df

def create_storage_visualizations(storage_df):
    """Create visualizations for storage data"""
    print("\n🎨 Creating Visualizations...")
    print("-" * 40)
    
    # Set up plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create a comprehensive visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Time series plot
    ax1.plot(storage_df['period'], storage_df['value'], linewidth=1, alpha=0.8)
    ax1.set_title('Natural Gas Storage Over Time', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Storage (BCF)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Distribution histogram
    ax2.hist(storage_df['value'], bins=50, alpha=0.7, edgecolor='black')
    ax2.axvline(storage_df['value'].mean(), color='red', linestyle='--', 
                label=f'Mean: {storage_df["value"].mean():.0f} BCF')
    ax2.axvline(storage_df['value'].median(), color='green', linestyle='--', 
                label=f'Median: {storage_df["value"].median():.0f} BCF')
    ax2.set_title('Distribution of Storage Values', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Storage (BCF)', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Monthly box plot
    monthly_data = [storage_df[storage_df['month'] == month]['value'].values 
                    for month in range(1, 13)]
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax3.boxplot(monthly_data, labels=month_labels)
    ax3.set_title('Storage by Month (Box Plot)', fontsize=16, fontweight='bold')
    ax3.set_ylabel('Storage (BCF)', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Recent trend (last 2 years)
    recent_data = storage_df[storage_df['period'] >= (datetime.now() - timedelta(days=730))]
    ax4.plot(recent_data['period'], recent_data['value'], linewidth=2, alpha=0.8, color='orange')
    ax4.set_title('Recent Storage Trend (Last 2 Years)', fontsize=16, fontweight='bold')
    ax4.set_ylabel('Storage (BCF)', fontsize=12)
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    print("✅ Visualizations created successfully!")

def export_storage_data(storage_df):
    """Export storage data in various formats"""
    print("\n💾 Exporting Data...")
    print("-" * 40)
    
    # Create export directory
    export_dir = "natural_gas_analysis_export"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Export full dataset
    full_filename = os.path.join(export_dir, "natural_gas_storage_full.csv")
    storage_df.to_csv(full_filename, index=False)
    print(f"✅ Full dataset exported to: {full_filename}")
    
    # Export summary statistics
    summary_stats = storage_df.groupby(storage_df['period'].dt.year)['value'].agg(['mean', 'min', 'max', 'std']).round(2)
    summary_filename = os.path.join(export_dir, "natural_gas_storage_summary.csv")
    summary_stats.to_csv(summary_filename)
    print(f"✅ Annual summary exported to: {summary_filename}")
    
    # Export monthly averages
    monthly_avg = storage_df.groupby(storage_df['period'].dt.month)['value'].mean().round(2)
    monthly_filename = os.path.join(export_dir, "natural_gas_storage_monthly.csv")
    monthly_avg.to_csv(monthly_filename)
    print(f"✅ Monthly averages exported to: {monthly_filename}")
    
    print(f"\n📁 All exports saved to: {export_dir}/")

def main():
    """Main analysis function"""
    print("🔋 Natural Gas Storage Comprehensive Analysis")
    print("=" * 60)
    print("This script analyzes natural gas storage data from the EIA API")
    print("and provides insights, visualizations, and data exports.\n")
    
    try:
        # Step 1: Retrieve and clean data
        storage_df = analyze_natural_gas_storage()
        if storage_df is None:
            print("❌ Analysis failed - no data retrieved")
            return
        
        # Step 2: Generate insights
        storage_df = generate_storage_insights(storage_df)
        
        # Step 3: Create visualizations
        create_storage_visualizations(storage_df)
        
        # Step 4: Export data
        export_storage_data(storage_df)
        
        print("\n🎯 Analysis complete!")
        print("📊 Natural gas storage data has been analyzed, visualized, and exported")
        print("💡 Check the export directory for CSV files with your data")
        
    except Exception as e:
        print(f"\n❌ Analysis error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
