#!/usr/bin/env python3
"""
EIA Energy Data Analysis Tool
Analyzes energy consumption, production, and pricing data from the EIA API
Enhanced with comprehensive data sources from EIA API v2
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Union
import warnings
import numpy as np # Added for numeric column selection
warnings.filterwarnings('ignore')

class EIAEnergyAnalyzer:
    """Enhanced EIA energy data analyzer with multiple data sources"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the EIA analyzer
        
        Args:
            api_key: EIA API key (optional, can be set via environment variable)
        """
        self.api_key = api_key or os.getenv('EIA_API_KEY')
        self.base_url = "https://api.eia.gov/v2"
        self.session = requests.Session()
        
        if self.api_key:
            self.session.params.update({'api_key': self.api_key})
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Available data categories from EIA API v2
        self.data_categories = {
            'electricity': ['facility-fuel', 'electric-power-operational-data', 'operating-generator-capacity', 'retail-sales'],
            'natural_gas': ['production', 'consumption', 'storage', 'prices'],
            'coal': ['production', 'consumption', 'prices', 'shipments'],
            'nuclear': ['facility-nuclear-outages', 'generator-nuclear-outages'],
            'renewables': ['densified-biomass'],
            'emissions': ['co2-emissions-aggregates', 'co2-emissions-and-carbon-coefficients'],
            'forecasts': ['aeo', 'steo', 'ieo'],
            'international': ['international'],
            'total_energy': ['total-energy']
        }
    
    def _make_api_request(self, endpoint: str, params: Dict = None) -> pd.DataFrame:
        """Generic method to make API requests to EIA endpoints"""
        if params is None:
            params = {}
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'response' in data and 'data' in data['response']:
                df = pd.DataFrame(data['response']['data'])
                if not df.empty:
                    # Handle different column names for values
                    value_columns = ['value', 'Value', 'VALUE', 'amount', 'Amount', 'AMOUNT']
                    value_col = None
                    for col in value_columns:
                        if col in df.columns:
                            value_col = col
                            break
                    
                    if value_col is None:
                        # If no standard value column, use the first numeric column
                        numeric_cols = df.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            value_col = numeric_cols[0]
                            # Rename it to 'value' for consistency
                            df = df.rename(columns={value_col: 'value'})
                        else:
                            print(f"No numeric value column found in {endpoint}")
                            return pd.DataFrame()
                    
                    # Handle period column
                    period_columns = ['period', 'Period', 'PERIOD', 'date', 'Date', 'DATE', 'time', 'Time', 'TIME']
                    period_col = None
                    for col in period_columns:
                        if col in df.columns:
                            period_col = col
                            break
                    
                    if period_col and period_col != 'period':
                        df = df.rename(columns={period_col: 'period'})
                    
                    if 'period' in df.columns:
                        df['period'] = pd.to_datetime(df['period'])
                        df = df.sort_values('period')
                    
                    print(f"✅ Retrieved {len(df)} data points from {endpoint}")
                    print(f"   Columns: {list(df.columns)}")
                    if 'value' in df.columns:
                        # Convert value to numeric if it's a string
                        if df['value'].dtype == 'object':
                            df['value'] = pd.to_numeric(df['value'], errors='coerce')
                        
                        # Filter out any NaN values
                        df = df.dropna(subset=['value'])
                        
                        if len(df) > 0:
                            print(f"   Value range: {df['value'].min():.2f} to {df['value'].max():.2f}")
                        else:
                            print("   No valid numeric values found")
                    
                    return df
                else:
                    print(f"No data found in response for {endpoint}")
                    return pd.DataFrame()
            else:
                print(f"No data found in response for {endpoint}")
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {endpoint}: {e}")
            return pd.DataFrame()
    
    def get_available_datasets(self) -> Dict[str, List[str]]:
        """Get available datasets from EIA API"""
        print("🔍 Available EIA Data Categories:")
        for category, datasets in self.data_categories.items():
            print(f"   📊 {category.replace('_', ' ').title()}:")
            for dataset in datasets:
                print(f"      • {dataset}")
        return self.data_categories
    
    def get_electricity_generation(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get electricity generation data from EIA
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with electricity generation data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'frequency': 'daily',
            'data[0]': 'value',
            'facets[type][]': 'NG',  # Natural gas generation
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc',
            'offset': 0,
            'length': 5000
        }
        
        return self._make_api_request('electricity/electric-power-operational-data', params)
    
    def get_natural_gas_storage(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get natural gas storage data from EIA (weekly frequency)
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with natural gas storage data
        """
        if not start_date:
            start_date = "2010-01-01"  # Default to 2010 as per user's example
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'frequency': 'weekly',
            'data[0]': 'value',
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'offset': 0,
            'length': 5000
        }
        
        return self._make_api_request('natural-gas/stor/wkly/data', params)
    
    def get_natural_gas_data(self, data_type: str = 'production', start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get natural gas data from EIA
        
        Args:
            data_type: Type of data ('production', 'consumption', 'storage', 'prices')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with natural gas data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Map data types to EIA endpoints
        endpoint_map = {
            'production': 'natural-gas/production',
            'consumption': 'natural-gas/consumption',
            'storage': 'natural-gas/storage',
            'prices': 'natural-gas/prices'
        }
        
        if data_type not in endpoint_map:
            print(f"Invalid data_type: {data_type}. Available: {list(endpoint_map.keys())}")
            return pd.DataFrame()
        
        params = {
            'frequency': 'monthly',
            'data[0]': 'value',
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc',
            'offset': 0,
            'length': 5000
        }
        
        return self._make_api_request(endpoint_map[data_type], params)
    
    def get_coal_data(self, data_type: str = 'production', start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get coal data from EIA
        
        Args:
            data_type: Type of data ('production', 'consumption', 'prices', 'shipments')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with coal data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        endpoint_map = {
            'production': 'coal/mine-production',
            'consumption': 'coal/consumption-and-quality',
            'prices': 'coal/market-sales-price',
            'shipments': 'coal/shipments/mine-aggregates'
        }
        
        if data_type not in endpoint_map:
            print(f"Invalid data_type: {data_type}. Available: {list(endpoint_map.keys())}")
            return pd.DataFrame()
        
        params = {
            'frequency': 'monthly',
            'data[0]': 'value',
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc',
            'offset': 0,
            'length': 5000
        }
        
        return self._make_api_request(endpoint_map[data_type], params)
    
    def get_co2_emissions(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get CO2 emissions data from EIA
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with CO2 emissions data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'frequency': 'monthly',
            'data[0]': 'value',
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc',
            'offset': 0,
            'length': 5000
        }
        
        return self._make_api_request('co2-emissions/co2-emissions-aggregates', params)
    
    def get_energy_consumption(self, series_id: str = "TOTAL.TETCBUS.A", 
                              start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get energy consumption data from EIA (enhanced version)
        
        Args:
            series_id: EIA series ID for total energy consumption
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with energy consumption data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Try multiple endpoints for energy consumption data
        endpoints = [
            'electricity/rto/demand-data',
            'total-energy',
            'electricity/retail-sales'
        ]
        
        for endpoint in endpoints:
            params = {
                'frequency': 'hourly' if 'rto' in endpoint else 'monthly',
                'data[0]': 'value',
                'start': start_date,
                'end': end_date,
                'sort[0][column]': 'period',
                'sort[0][direction]': 'asc',
                'offset': 0,
                'length': 5000
            }
            
            df = self._make_api_request(endpoint, params)
            if not df.empty:
                return df
        
        print("No energy consumption data found from any endpoint")
        return pd.DataFrame()
    
    def get_electricity_prices(self, region: str = "US48", 
                             start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get electricity price data (enhanced version)
        
        Args:
            region: Geographic region (US48, CA, TX, etc.)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with electricity price data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Try RTO price data first
        params = {
            'frequency': 'hourly',
            'data[0]': 'value',
            'facets[type][]': 'RTP',
            'facets[respondent][]': region,
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc',
            'offset': 0,
            'length': 5000
        }
        
        df = self._make_api_request('electricity/rto/price-data', params)
        if not df.empty:
            return df
        
        # Fallback to retail sales data
        params = {
            'frequency': 'monthly',
            'data[0]': 'value',
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc',
            'offset': 0,
            'length': 5000
        }
        
        return self._make_api_request('electricity/retail-sales', params)
    
    def get_energy_mix(self, start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Get energy mix data from multiple sources
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with different energy source data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        energy_mix = {}
        
        # Get electricity generation by fuel type
        params = {
            'frequency': 'monthly',
            'data[0]': 'value',
            'start': start_date,
            'end': end_date,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'asc',
            'offset': 0,
            'length': 5000
        }
        
        # Try to get facility fuel data
        facility_fuel = self._make_api_request('electricity/facility-fuel', params)
        if not facility_fuel.empty:
            energy_mix['facility_fuel'] = facility_fuel
        
        # Get natural gas data
        ng_data = self.get_natural_gas_data('production', start_date, end_date)
        if not ng_data.empty:
            energy_mix['natural_gas'] = ng_data
        
        # Get coal data
        coal_data = self.get_coal_data('production', start_date, end_date)
        if not coal_data.empty:
            energy_mix['coal'] = coal_data
        
        return energy_mix
    
    def plot_energy_consumption(self, df: pd.DataFrame, title: str = "Energy Consumption Over Time"):
        """Plot energy consumption data"""
        if df.empty:
            print("No data to plot")
            return
            
        plt.figure(figsize=(12, 6))
        plt.plot(df['period'], df['value'], linewidth=2, alpha=0.8)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Energy Consumption (MWh)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def plot_electricity_prices(self, df: pd.DataFrame, title: str = "Electricity Prices Over Time"):
        """Plot electricity price data"""
        if df.empty:
            print("No data to plot")
            return
            
        plt.figure(figsize=(12, 6))
        plt.plot(df['period'], df['value'], linewidth=2, alpha=0.8, color='orange')
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price ($/MWh)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def plot_energy_mix(self, energy_mix: Dict[str, pd.DataFrame], title: str = "Energy Mix Over Time"):
        """Plot energy mix data from multiple sources"""
        if not energy_mix:
            print("No energy mix data to plot")
            return
        
        plt.figure(figsize=(14, 8))
        
        colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
        for i, (source, df) in enumerate(energy_mix.items()):
            if not df.empty and 'period' in df.columns and 'value' in df.columns:
                color = colors[i % len(colors)]
                plt.plot(df['period'], df['value'], 
                        linewidth=2, alpha=0.8, color=color, 
                        label=source.replace('_', ' ').title())
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Energy Production/Consumption', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def generate_summary_stats(self, df: pd.DataFrame, metric_name: str = "Data") -> Dict:
        """Generate summary statistics for a dataset"""
        if df.empty:
            return {}
            
        stats = {
            'metric': metric_name,
            'count': len(df),
            'mean': df['value'].mean(),
            'median': df['value'].median(),
            'std': df['value'].std(),
            'min': df['value'].min(),
            'max': df['value'].max(),
            'date_range': f"{df['period'].min()} to {df['period'].max()}"
        }
        
        return stats
    
    def save_data_to_csv(self, df: pd.DataFrame, filename: str):
        """Save data to CSV file"""
        if not df.empty:
            df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")
        else:
            print("No data to save")
    
    def export_all_data(self, start_date: str = None, end_date: str = None, output_dir: str = "eia_data_export"):
        """
        Export all available data to CSV files
        
        Args:
            start_date: Start date for data export
            end_date: End date for data export
            output_dir: Directory to save exported files
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"📁 Exporting data to {output_dir}/")
        
        # Export different data types
        data_sources = [
            ('energy_consumption', self.get_energy_consumption(start_date, end_date)),
            ('electricity_prices', self.get_electricity_prices(start_date=start_date, end_date=end_date)),
            ('electricity_generation', self.get_electricity_generation(start_date, end_date)),
            ('natural_gas_production', self.get_natural_gas_data('production', start_date, end_date)),
            ('coal_production', self.get_coal_data('production', start_date, end_date)),
            ('co2_emissions', self.get_co2_emissions(start_date, end_date))
        ]
        
        for name, df in data_sources:
            if not df.empty:
                filename = os.path.join(output_dir, f"{name}_{start_date}_{end_date}.csv")
                self.save_data_to_csv(df, filename)
        
        print(f"✅ Data export complete! Check {output_dir}/ directory")

def main():
    """Main function to demonstrate enhanced EIA analysis capabilities"""
    print("🔋 Enhanced EIA Energy Data Analysis Tool")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = EIAEnergyAnalyzer()
    
    if not analyzer.api_key:
        print("⚠️  No EIA API key found. Set EIA_API_KEY environment variable for full functionality.")
        print("   You can get a free API key from: https://www.eia.gov/opendata/")
        print("   Some basic analysis will still work with public data.\n")
    
    # Show available datasets
    analyzer.get_available_datasets()
    
    # Example analysis with multiple data sources
    print("\n📊 Fetching energy data from multiple sources...")
    
    # Get energy consumption data
    consumption_df = analyzer.get_energy_consumption()
    
    if not consumption_df.empty:
        print(f"✅ Retrieved {len(consumption_df)} consumption data points")
        
        # Generate summary statistics
        stats = analyzer.generate_summary_stats(consumption_df, "Energy Consumption")
        print("\n📈 Summary Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Plot the data
        print("\n📊 Generating consumption plot...")
        analyzer.plot_energy_consumption(consumption_df)
        
        # Save data
        analyzer.save_data_to_csv(consumption_df, "energy_consumption_data.csv")
    else:
        print("❌ No consumption data retrieved")
    
    # Try to get energy mix data
    print("\n🌍 Fetching energy mix data...")
    energy_mix = analyzer.get_energy_mix()
    
    if energy_mix:
        print(f"✅ Retrieved data for {len(energy_mix)} energy sources")
        analyzer.plot_energy_mix(energy_mix)
    else:
        print("❌ No energy mix data retrieved")
    
    print("\n🎯 Analysis complete!")
    print("💡 Tip: Set your EIA API key for access to more comprehensive data")
    print("🔍 Use get_available_datasets() to see all available data sources")

if __name__ == "__main__":
    main()
