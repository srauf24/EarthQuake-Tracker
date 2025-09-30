"""
Main application file for the Real-time Global Earthquake Tracker.

This Streamlit app visualizes recent earthquake data on a 3D globe.
It fetches data from the USGS, processes it, and displays it using Pydeck.
Users can filter the data by time period and magnitude.
"""

import streamlit as st
from src.fetch import fetch_geojson
from src.transform import validate_and_convert_geojson
from src.ui import sidebar, render_map
from src.viz import color_from_mag, radius_from_mag

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Earthquake Tracker", layout="wide")
    st.title("🌎 Real-time Global Earthquake Tracker")

    period, min_mag = sidebar()
    print(f"[Flow] User selected: Period='{period.value}', Min Magnitude={min_mag}")

    try:
        print("[Flow] Fetching data from USGS...")
        raw_data = fetch_geojson(period)
        print("[Flow] Data fetched successfully.")

        print("[Flow] Transforming data into DataFrame...")
        df = validate_and_convert_geojson(raw_data)
        print(f"[Flow] DataFrame created with {len(df)} records.")

        if "mag" in df.columns:
            # Apply visual mappings for color and radius
            color_cols = list(zip(*df["mag"].map(color_from_mag)))
            df["mag_r"], df["mag_g"], df["mag_b"], df["mag_a"] = color_cols
            df["radius"] = df["mag"].apply(radius_from_mag)

            # Filter data based on user selection
            print(f"[Flow] Filtering DataFrame for magnitude >= {min_mag}...")
            filtered_df = df[df["mag"].fillna(-1) >= min_mag]
            print(f"[Flow] Filtered DataFrame has {len(filtered_df)} records.")

            if not filtered_df.empty:
                print("[Flow] Rendering map and data table...")
                render_map(filtered_df)
                st.subheader("Raw Data")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("No earthquakes found for the selected magnitude.")
                print("[Flow] No data to render after filtering.")
        else:
            st.warning("No magnitude data available to display.")
            print("[Flow] No 'mag' column in DataFrame.")

    except Exception as e:
        st.error("An error occurred while fetching or processing data.")
        st.exception(e)
        print(f"[Flow] An error occurred: {e}")

if __name__ == "__main__":
    main()

