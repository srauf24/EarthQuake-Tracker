"""
Transforms raw GeoJSON data into a clean Pandas DataFrame.

This module provides functions to normalize the nested GeoJSON structure
from the USGS API into a flat, tabular format suitable for analysis and
visualization.
"""

import pandas as pd

def validate_and_convert_geojson(geojson: dict) -> pd.DataFrame:
    """
    Converts and validates GeoJSON data to a Pandas DataFrame.

    This function iterates through the features in the GeoJSON data, validates
    their structure, and extracts the relevant fields into a structured DataFrame.
    Malformed features are skipped.

    Args:
        geojson: A dictionary containing GeoJSON data from the USGS feed.

    Returns:
        A Pandas DataFrame with cleaned and structured earthquake data.
    """
    feats = geojson.get("features", [])
    rows, skipped_count = [], 0

    for f in feats:
        try:
            # Structural validation
            props = f["properties"]
            coords = f["geometry"]["coordinates"]
            if len(coords) != 3:
                raise ValueError(f"Coordinates list has {len(coords)} items, expected 3.")

            # Append validated data
            rows.append({
                "event_id": f.get("id"),
                "time": pd.to_datetime(props["time"], unit="ms", utc=True),
                "longitude": coords[0],
                "latitude": coords[1],
                "depth_km": coords[2],
                "mag": props.get("mag"),
                "place": props.get("place"),
                "url": props.get("url"),
            })
        except (KeyError, TypeError, ValueError) as e:
            skipped_count += 1
            print(f"[Validation] Skipping malformed feature: {f.get('id', 'N/A')}. Reason: {e}")

    if skipped_count > 0:
        print(f"[Validation] Skipped a total of {skipped_count} malformed records.")

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).dropna(subset=["latitude", "longitude"])
    return df.sort_values("time", ascending=False)
