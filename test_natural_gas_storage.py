#!/usr/bin/env python3
"""
Test natural gas storage data using the exact API call from the user
"""

import requests
import json
import pandas as pd
from datetime import datetime

def test_natural_gas_storage():
    """Test the exact natural gas storage API call"""
    api_key = "7Zh9UWfJ4WsW8vRXmO3NRVmwMPZuFudNeo44IcR2"
    
    print("🔋 Natural Gas Storage API Test")
    print("=" * 50)
    print(f"API Key: {api_key[:10]}...")
    
    # Use the exact parameters from user's working API call
    url = "https://api.eia.gov/v2/natural-gas/stor/wkly/data/"
    
    params = {
        'api_key': api_key,
        'frequency': 'weekly',
        'data[0]': 'value',
        'start': '2010-01-01',
        'end': '2025-08-15',
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc',
        'offset': 0,
        'length': 5000
    }
    
    print(f"\n🔍 Testing URL: {url}")
    print(f"📋 Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(url, params=params)
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response received")
            print(f"📋 Response keys: {list(data.keys())}")
            
            if 'response' in data:
                response_data = data['response']
                print(f"📋 Response data keys: {list(response_data.keys())}")
                
                if 'data' in response_data:
                    df_data = response_data['data']
                    print(f"📊 Data points found: {len(df_data)}")
                    
                    if df_data:
                        print(f"\n📋 First data record:")
                        first_record = df_data[0]
                        for key, value in first_record.items():
                            print(f"   {key}: {value}")
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(df_data)
                        print(f"\n📊 DataFrame created:")
                        print(f"   Shape: {df.shape}")
                        print(f"   Columns: {list(df.columns)}")
                        
                        # Check for period and value columns
                        if 'period' in df.columns:
                            df['period'] = pd.to_datetime(df['period'])
                            print(f"   Date range: {df['period'].min()} to {df['period'].max()}")
                        
                        if 'value' in df.columns:
                            # Convert value to numeric if it's a string
                            if df['value'].dtype == 'object':
                                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                            
                            # Filter out any NaN values
                            df = df.dropna(subset=['value'])
                            
                            if len(df) > 0:
                                print(f"   Value range: {df['value'].min():.2f} to {df['value'].max():.2f}")
                                print(f"   Units: {df['units'].iloc[0] if 'units' in df.columns else 'Unknown'}")
                            else:
                                print("   No valid numeric values found")
                        
                        # Save to CSV
                        filename = "natural_gas_storage_test.csv"
                        df.to_csv(filename, index=False)
                        print(f"\n💾 Data saved to {filename}")
                        
                        return df
                    else:
                        print("❌ No data records found")
                        return None
                else:
                    print("❌ No 'data' key in response")
                    return None
            else:
                print("❌ No 'response' key in data")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    df = test_natural_gas_storage()
    
    if df is not None:
        print(f"\n🎯 Test successful!")
        print(f"📊 Retrieved {len(df)} natural gas storage records")
        print(f"💾 Data saved to CSV for analysis")
    else:
        print(f"\n❌ Test failed")
    
    print("\n🎯 Test complete!")

if __name__ == "__main__":
    main()
