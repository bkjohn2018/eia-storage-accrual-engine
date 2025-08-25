#!/usr/bin/env python3
"""
Test script to explore EIA API endpoints
"""

import requests
import json

def test_endpoint(endpoint, api_key):
    """Test a specific API endpoint"""
    base_url = "https://api.eia.gov/v2"
    url = f"{base_url}/{endpoint}"
    
    params = {
        'api_key': api_key,
        'frequency': 'weekly',
        'data[0]': 'value',
        'start': '2020-01-01',
        'end': '2025-08-15',
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc',
        'offset': 0,
        'length': 10  # Just get 10 records for testing
    }
    
    try:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        print(f"   URL: {url}")
        
        response = requests.get(url, params=params)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            
            if 'response' in data:
                response_data = data['response']
                print(f"   Response data keys: {list(response_data.keys())}")
                
                if 'data' in response_data:
                    df_data = response_data['data']
                    print(f"   ✅ Success! Found {len(df_data)} data points")
                    if df_data:
                        print(f"   📋 Sample data structure:")
                        print(f"      Keys: {list(df_data[0].keys())}")
                        print(f"      First record: {df_data[0]}")
                    return True
                else:
                    print(f"   ❌ No 'data' key in response")
                    return False
            else:
                print(f"   ❌ No 'response' key in data")
                return False
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"      Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Test various EIA API endpoints"""
    api_key = "7Zh9UWfJ4WsW8vRXmO3NRVmwMPZuFudNeo44IcR2"
    
    print("🔋 EIA API Endpoint Testing")
    print("=" * 50)
    print(f"API Key: {api_key[:10]}...")
    
    # Test the exact endpoint from user's example
    print("\n🎯 Testing User's Exact Endpoint...")
    test_endpoint("natural-gas/stor/wkly", api_key)
    
    # Test some other endpoints to see what works
    print("\n🔍 Testing Other Endpoints...")
    
    endpoints_to_test = [
        "natural-gas/stor/wkly",
        "natural-gas/storage/weekly", 
        "natural-gas/storage",
        "natural-gas/production",
        "electricity/rto/demand-data",
        "electricity/retail-sales",
        "total-energy"
    ]
    
    working_endpoints = []
    for endpoint in endpoints_to_test:
        if test_endpoint(endpoint, api_key):
            working_endpoints.append(endpoint)
    
    print(f"\n📊 Summary:")
    print(f"   Working endpoints: {len(working_endpoints)}")
    print(f"   Failed endpoints: {len(endpoints_to_test) - len(working_endpoints)}")
    
    if working_endpoints:
        print(f"\n✅ Working endpoints:")
        for endpoint in working_endpoints:
            print(f"   • {endpoint}")
    
    print("\n🎯 Test complete!")

if __name__ == "__main__":
    main()
