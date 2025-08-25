"""EIA API client for data ingestion with retry logic and structured logging."""

import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from eia_sa.config import settings
from eia_sa.utils.logging import get_logger, log_api_request

logger = get_logger(__name__)


class EIAClient:
    """EIA API client with retry logic, backoff, and structured logging."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize EIA client with API key and retry configuration."""
        self.api_key = api_key or settings.eia_api_key
        self.base_url = settings.eia_base_url
        self.session = self._create_session()
        
        # Ensure bronze directory exists
        Path(settings.data_bronze_path).mkdir(parents=True, exist_ok=True)

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic and backoff."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=settings.eia_max_retries,
            backoff_factor=settings.eia_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default timeout
        session.timeout = settings.eia_request_timeout
        
        return session

    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make API request with logging and error handling."""
        url = f"{self.base_url}/{endpoint}"
        
        # Add API key to params
        request_params = params or {}
        request_params["api_key"] = self.api_key
        
        start_time = time.time()
        
        try:
            logger.info("Making EIA API request", **log_api_request(
                endpoint=endpoint,
                status_code=0,
                response_time=0,
                url=url,
                params=request_params
            ))
            
            response = self.session.get(url, params=request_params)
            response_time = time.time() - start_time
            
            # Log the response
            logger.info("EIA API response received", **log_api_request(
                endpoint=endpoint,
                status_code=response.status_code,
                response_time=response_time,
                url=url,
                response_size=len(response.content)
            ))
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.error("EIA API request failed", **log_api_request(
                endpoint=endpoint,
                status_code=getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                response_time=response_time,
                url=url,
                error=str(e)
            ))
            raise

    def fetch_weekly_storage(
        self, 
        start_date: str, 
        end_date: str,
        regions: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Fetch weekly working gas storage data."""
        logger.info("Fetching weekly storage data", 
                   start_date=start_date, end_date=end_date, regions=regions)
        
        # Default regions if none specified
        if regions is None:
            regions = ["R10", "R20", "R30", "R40", "R50"]  # US regions
        
        all_data = []
        
        for region in regions:
            params = {
                'frequency': 'weekly',
                'data[0]': 'value',
                'facets[duoarea][]': region,
                'start': start_date,
                'end': end_date,
                'sort[0][column]': 'period',
                'sort[0][direction]': 'desc',
                'offset': 0,
                'length': 5000
            }
            
            try:
                data = self._make_request('natural-gas/stor/wkly/data', params)
                
                if 'response' in data and 'data' in data['response']:
                    region_data = data['response']['data']
                    if region_data:
                        all_data.extend(region_data)
                        logger.info(f"Retrieved {len(region_data)} records for region {region}")
                    else:
                        logger.warning(f"No data found for region {region}")
                else:
                    logger.warning(f"Invalid response structure for region {region}")
                    
            except Exception as e:
                logger.error(f"Failed to fetch data for region {region}", error=str(e))
                continue
        
        if not all_data:
            logger.warning("No weekly storage data retrieved")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        logger.info(f"Total weekly storage records: {len(df)}")
        
        return df

    def fetch_capacity_data(self, year: Optional[int] = None) -> pd.DataFrame:
        """Fetch storage capacity data (annual)."""
        if year is None:
            year = datetime.now().year
            
        logger.info("Fetching capacity data", year=year)
        
        params = {
            'frequency': 'annual',
            'data[0]': 'value',
            'facets[year][]': str(year),
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'offset': 0,
            'length': 1000
        }
        
        try:
            data = self._make_request('natural-gas/stor/cap', params)
            
            if 'response' in data and 'data' in data['response']:
                capacity_data = data['response']['data']
                if capacity_data:
                    df = pd.DataFrame(capacity_data)
                    logger.info(f"Retrieved {len(df)} capacity records for {year}")
                    return df
                else:
                    logger.warning(f"No capacity data found for {year}")
                    return pd.DataFrame()
            else:
                logger.warning("Invalid response structure for capacity data")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error("Failed to fetch capacity data", error=str(e))
            return pd.DataFrame()

    def save_raw_data(self, data: Dict[str, Any], filename: str) -> None:
        """Save raw API response to JSONL file."""
        filepath = Path(settings.data_bronze_path) / f"{filename}.jsonl"
        
        try:
            with open(filepath, 'w') as f:
                for item in data.get('response', {}).get('data', []):
                    f.write(f"{item}\n")
            
            logger.info(f"Raw data saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save raw data to {filepath}", error=str(e))
            raise

    def save_parquet_data(self, df: pd.DataFrame, filename: str) -> None:
        """Save normalized data to parquet file."""
        filepath = Path(settings.data_bronze_path) / f"{filename}.parquet"
        
        try:
            df.to_parquet(filepath, index=False)
            logger.info(f"Parquet data saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save parquet data to {filepath}", error=str(e))
            raise

    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for retrieved data."""
        if df.empty:
            return {"record_count": 0, "date_range": None, "regions": []}
        
        summary = {
            "record_count": len(df),
            "columns": list(df.columns),
            "regions": df.get('duoarea', pd.Series()).unique().tolist() if 'duoarea' in df.columns else [],
        }
        
        if 'period' in df.columns:
            try:
                df['period'] = pd.to_datetime(df['period'])
                summary["date_range"] = {
                    "start": df['period'].min().strftime('%Y-%m-%d'),
                    "end": df['period'].max().strftime('%Y-%m-%d')
                }
            except Exception as e:
                logger.warning(f"Could not parse date range: {e}")
                summary["date_range"] = None
        
        if 'value' in df.columns:
            try:
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                summary["value_stats"] = {
                    "min": float(df['value'].min()),
                    "max": float(df['value'].max()),
                    "mean": float(df['value'].mean()),
                    "median": float(df['value'].median())
                }
            except Exception as e:
                logger.warning(f"Could not calculate value statistics: {e}")
                summary["value_stats"] = None
        
        return summary
