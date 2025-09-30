"""
Defines the user interface components for the earthquake tracker app.

This module contains functions to create the sidebar controls and the main
map visualization using Streamlit and Pydeck.
"""

import streamlit as st
import pydeck as pdk
from src.enums import TimePeriod

def sidebar():
    """
    Renders the sidebar controls for filtering earthquake data.

    Returns:
        A tuple containing the selected TimePeriod enum and minimum magnitude.
    """
    st.sidebar.header("Filters")
    
    period = st.sidebar.radio(
        "Time window",
        options=[TimePeriod.DAY, TimePeriod.WEEK, TimePeriod.MONTH],
        index=1,  # Default to 'week'
        format_func=lambda x: x.value.capitalize(),  # Display 'Day', 'Week', 'Month'
        key="period"
    )
    
    min_mag = st.sidebar.slider("Min magnitude", 0.0, 8.0, 3.0, 0.1, key="min_mag")
    return period, min_mag

def render_map(df):
    """
    Renders the Pydeck map with earthquake data.

    Args:
        df: A Pandas DataFrame containing the earthquake data to display.
    """
    view = pdk.ViewState(latitude=0, longitude=0, zoom=1.7)
    tooltip = {
        "html": "<b>Mag</b>: {mag}<br/><b>Depth</b>: {depth_km} km<br/><b>When</b>: {time}<br/><b>Where</b>: {place}",
        "style": {"color": "white"}
    }
    deck = pdk.Deck(
        map_style=None,  # globe
        initial_view_state=view,
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[longitude, latitude]",
                get_radius="radius",
                get_fill_color="[mag_r, mag_g, mag_b, mag_a]",
                pickable=True,
            )
        ],
        tooltip=tooltip,
    )
    st.pydeck_chart(deck, use_container_width=True)
