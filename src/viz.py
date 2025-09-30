"""
Handles the visual representation of earthquake data.

This module provides functions for color and radius scaling based on
earthquake magnitude, and for creating the Pydeck visualization layer.
"""

import pydeck as pdk
import numpy as np

_DEF = {
    "min_mag": 0.0,
    "radius_scale": 10000,
    "radius_min": 3000,
}

def color_from_mag(m):
    """
    Determines the color of a point based on earthquake magnitude.

    Args:
        m: The earthquake magnitude.

    Returns:
        A list representing the RGBA color.
    """
    if m is None or np.isnan(m):
        return [128, 128, 128, 180]  # Gray for unknown magnitude
    if m < 3:
        return [50, 180, 70, 160]   # Green for minor earthquakes
    if m < 5:
        return [230, 200, 40, 170]  # Yellow for moderate earthquakes
    return [220, 60, 50, 190]       # Red for significant earthquakes

def radius_from_mag(m):
    """
    Calculates the radius of a point based on earthquake magnitude.

    Args:
        m: The earthquake magnitude.

    Returns:
        The radius for the point on the map.
    """
    if m is None or np.isnan(m):
        return _DEF["radius_min"]
    return int(_DEF["radius_min"] + m * _DEF["radius_scale"])

def globe_layer(df):
    """
    Creates a Pydeck ScatterplotLayer for visualizing earthquake data.

    Args:
        df: A Pandas DataFrame with earthquake data, including pre-calculated
            color and radius columns.

    Returns:
        A Pydeck Layer instance.
    """
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[longitude, latitude]",
        get_radius="radius",
        get_fill_color="[mag_r, mag_g, mag_b, mag_a]",
        pickable=True,
        radius_min_pixels=2,
    )
