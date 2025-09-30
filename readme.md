# 🌎 Real‑time Global Earthquake Tracker

## Overview

The **Real‑time Global Earthquake Tracker** is a Streamlit web app that fetches live earthquake data from the U.S. Geological Survey (USGS) and visualizes it on an interactive 3D globe. Users can filter events by magnitude and time range, explore details through tooltips, and inspect raw data in an interactive table.

This project demonstrates skills in **API integration, data processing, interactive visualization, and deployment**.

---

## Features (Detailed for Junior Engineers)

### 1. Data Fetching

* **What it does**: Connects to the free [USGS GeoJSON feeds](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) to pull recent earthquake data (past day, week, or month).
* **Key skills learned**: Making HTTP requests with headers, handling JSON, adding polite usage (User-Agent).
* **Implementation details**:

  * Use `requests.get()` with a `User-Agent` header.
  * Cache responses with `@st.cache_data(ttl=600)` so the app doesn’t overwhelm the API.
  * Handle network errors with `try/except` and retries.

### 2. Data Transformation

* **What it does**: Converts GeoJSON into a structured Pandas DataFrame.
* **Key skills learned**: Parsing JSON, working with DataFrames, handling missing values.
* **Implementation details**:

  * Extract `latitude`, `longitude`, `depth_km`, `magnitude`, `place`, and `time`.
  * Convert `time` from milliseconds since epoch into human‑readable UTC datetimes.
  * Drop invalid or missing coordinates.

### 3. Interactive 3D Globe

* **What it does**: Displays earthquakes on a globe using Pydeck’s `ScatterplotLayer`.
* **Key skills learned**: Data visualization, mapping numerical values to colors/sizes.
* **Implementation details**:

  * Earthquakes are shown as circles on the globe.
  * **Magnitude → Radius**: Larger quakes produce bigger circles.
  * **Magnitude → Color**: Low magnitude = green, medium = yellow, high = red.
  * Tooltips show magnitude, depth, time, and place.

### 4. Sidebar Filters

* **What it does**: Lets users control the displayed data.
* **Key skills learned**: Streamlit UI widgets, filtering DataFrames.
* **Implementation details**:

  * **Time Range**: Select from *Past Day*, *Past Week*, *Past Month*.
  * **Minimum Magnitude**: Slider (0.0–8.0). Example: set to 5.0 to see only major quakes.

### 5. Data Table

* **What it does**: Displays the filtered earthquakes in a searchable, scrollable table.
* **Key skills learned**: Presenting data in Streamlit, sorting/filtering.
* **Implementation details**:

  * Uses `st.dataframe()` for interactive display.
  * Sorted by most recent earthquakes.
  * Add “Download CSV” button for user export (future enhancement).

### 6. Caching & Politeness

* **What it does**: Ensures API requests happen only once every 10 minutes per session.
* **Key skills learned**: Using decorators (`@st.cache_data`) and TTL values.
* **Implementation details**:

  * Users see fresh data at most every 10 minutes.
  * Reduces load on USGS servers.

### 7. Error Handling

* **What it does**: Prevents crashes if the API is unavailable or data is malformed.
* **Key skills learned**: Writing defensive code.
* **Implementation details**:

  * Show a friendly error message in the app.
  * Retry logic with exponential backoff.
  * Skip or mark earthquakes with missing magnitude values.

---

## Tech Stack

* **Streamlit**: Web app framework.
* **Pandas**: Data processing.
* **Requests**: HTTP requests.
* **Pydeck**: 3D globe visualization.

---

## Installation & Running

1. Clone the repo:

   ```bash
   git clone https://github.com/your-username/earthquake-tracker.git
   cd earthquake-tracker
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

4. Open the app in your browser (usually `http://localhost:8501`).

---

## Deployment

* Deploy free on **[Streamlit Community Cloud](https://streamlit.io/cloud)**.
* Connect your GitHub repo, configure Python version, and deploy.

---

## Demo

Include a **GIF or screenshot** showing:

* Globe rotation.
* Filtering by magnitude.
* Earthquake details in tooltips.
* <img width="2564" height="1326" alt="image" src="https://github.com/user-attachments/assets/c4980db0-03d3-40fa-9bb9-bfb520d8873a" />


---

## Roadmap / Future Enhancements

* Region filters (e.g., filter by country or bounding box).
* Notification system for >5.5 magnitude events.
* Historical trend storage and visualization.
* Plate tectonic overlays.

---

## Credits

* Data: [U.S. Geological Survey Earthquake Hazards Program](https://earthquake.usgs.gov/).
* Libraries: Streamlit, Pandas, Requests, Pydeck.
