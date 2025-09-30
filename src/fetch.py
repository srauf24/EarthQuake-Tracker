"""
Fetches earthquake data from the USGS GeoJSON API.

This module provides a function to fetch earthquake data for different
time periods and caches the results to avoid excessive API calls.
"""

import streamlit as st
import requests
import time
from src.enums import TimePeriod

UA = {"User-Agent": "EarthquakeTracker/1.0 (sameerauf1@gmail.com)"}
BASE = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary"

@st.cache_data(ttl=600)
def fetch_geojson(period: TimePeriod) -> dict:
    """
    Fetches and validates GeoJSON data from the USGS earthquake feed.

    Args:
        period: The time period for the data (TimePeriod.DAY, .WEEK, or .MONTH).

    Returns:
        A dictionary containing the GeoJSON data.

    Raises:
        ValueError: If the fetched data is not valid GeoJSON or is missing the 'features' key.
    """
    url = f"{BASE}/all_{period.value}.geojson"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=15)
            r.raise_for_status()
            data = r.json()

            # Basic data validation
            if not isinstance(data, dict) or "features" not in data:
                raise ValueError("Invalid GeoJSON format: 'features' key is missing.")

            return data
        except requests.RequestException as e:
            st.error(f"Failed to fetch data: {e}. Retrying...")
            if attempt == 2:
                st.exception(e)
                raise
            time.sleep(2 ** attempt)
        except (ValueError, TypeError) as e:
            st.error(f"Data validation failed: {e}")
            raise
