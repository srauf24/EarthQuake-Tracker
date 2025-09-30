# Real‑time Global Earthquake Tracker — Design & Architecture

## 1) Executive Summary

Build a Streamlit app that visualizes live global earthquakes on an interactive 3D globe using Pydeck, powered by USGS’s free GeoJSON feeds (no API key). Users can filter by magnitude and time window (past day/week/month), inspect details in a table, and click map points for metadata. Caching ensures we’re a good API citizen.

---

## 2) Goals & Non‑Goals

**Goals**

* Fetch and display recent earthquakes on a 3D globe (Pydeck).
* Real‑time-ish updates with polite request frequency (caching TTL).
* Sidebar filters for magnitude threshold and time range.
* Tabular view with sorting/search.
* Shareable deployment (Streamlit Community Cloud).

**Non‑Goals**

* Historical archive beyond the USGS feed windows.
* Predictive modeling or seismic analysis.
* Auth, user accounts, or write operations.

---

## 3) User Stories

* *As a casual user*, I want to see where earthquakes are happening now so I can explore hotspots.
* *As a geo‑enthusiast*, I want to filter by magnitude and period to focus on significant events.
* *As a recruiter/reviewer*, I want to skim the UI and code to gauge the candidate’s data/visualization skill.

---

## 4) System Architecture Overview

### 4.1 High‑Level Options

* **Option A (Recommended, Portfolio‑friendly):** Single Streamlit app. Streamlit server fetches USGS JSON, caches results, renders Pydeck globe and a DataFrame table.
* **Option B (Extendable):** Streamlit UI + lightweight FastAPI microservice for data fetching/caching. Useful if you later add features like alerts, cron jobs, or custom rollups.

### 4.2 Components

* **USGS GeoJSON Feeds** (public): Past hour/day/week/month endpoints.
* **Data Fetch Layer**: `requests` with `User-Agent` header; basic retry/backoff.
* **Cache**: `@st.cache_data(ttl=600)` to limit outbound calls.
* **Data Processing**: Pandas transforms GeoJSON → tidy DataFrame with columns: `time`, `latitude`, `longitude`, `depth_km`, `mag`, `place`, `event_id`, `url`.
* **Visualization**: Pydeck `ScatterplotLayer` on a `GlobeView` or map-style view state; point radius & color scale based on magnitude.
* **UI/Controls**: Streamlit sidebar (period select, magnitude slider), main pane (map, data table, download CSV).
* **Deployment**: Streamlit Community Cloud.

### 4.3 Data Flow (Sequence)

1. User loads the app → Streamlit session starts.
2. App determines selected **time window** (day/week/month) and **min magnitude**.
3. Cached fetch function calls the appropriate USGS feed (if cache expired) with User-Agent.
4. Response (GeoJSON) → normalized into a Pandas DataFrame.
5. Data filtered by min magnitude → rendered in Pydeck and a DataFrame.
6. Optional: User clicks a point → tooltip shows metadata with a link to the USGS event page.

---

## 5) API Integration

### 5.1 Endpoints (GeoJSON Feeds)

* **Past hour/day/week/month** feeds in both “all” and magnitude‑filtered variants (e.g., `all_day`, `4.5_week`). For flexibility, default to `all_` feeds and filter in‑app.

### 5.2 Request Guidelines

* **User‑Agent**: USGS requests clients identify themselves.
* **Politeness**: Cache responses (600s TTL recommended). Avoid per‑interaction network calls.
* **Retries**: Small exponential backoff for transient failures.

**Python example**

```python
import requests

UA = {"User-Agent": "EarthquakeTracker/1.0 (me@mydomain.com)"}
resp = requests.get(usgs_url, headers=UA, timeout=15)
resp.raise_for_status()
geojson = resp.json()
```

---

## 6) Data Model

**Raw Source (GeoJSON)**

* `features[].geometry.coordinates = [lon, lat, depth]`
* `features[].properties = { mag, place, time, url, tsunami, type, ... }`

**App DataFrame (normalized)**

| column    | type     | notes                                  |
| --------- | -------- | -------------------------------------- |
| event_id  | string   | `features[].id`                        |
| time      | datetime | convert ms since epoch → UTC           |
| latitude  | float    | from `coordinates[1]`                  |
| longitude | float    | from `coordinates[0]`                  |
| depth_km  | float    | from `coordinates[2]`                  |
| mag       | float    | may be `None` → drop/label accordingly |
| place     | string   | human‑readable location                |
| url       | string   | link to USGS event page                |

---

## 7) UI/UX Design

* **Layout**: Sidebar controls; main area with globe on top, table below.
* **Filters**:

  * Time period: radio/select → *Past Day*, *Past Week*, *Past Month*.
  * Min magnitude: slider (e.g., 0.0–8.0, step 0.1; default 3.0).
* **Map**:

  * Pydeck `ScatterplotLayer` with `get_position=["longitude", "latitude"]`.
  * `get_radius` = `mag` → radius scale (e.g., `mag * 10000 + 5000`).
  * `get_fill_color` from a function mapping magnitudes (e.g., low=green, high=red). Use a capped scale and graceful handling of missing mags.
  * Tooltips: mag, depth, time, place.
* **Table**: `st.dataframe` with default sorting on `time desc` and a download button.
* **Empty States**: Show info if no quakes match filters, or API is down.
* **Accessibility**: High‑contrast tooltip text; keyboard‑navigable controls; color encoding paired with size.

---

## 8) Caching, Performance & Rate Limiting

* `@st.cache_data(ttl=600)` on the fetch function keyed by endpoint.
* Memoize color/radius transforms to avoid recompute on widget changes.
* Use Pandas vectorized ops; avoid per‑row Python loops.
* Limit DataFrame size shown (e.g., show top N by magnitude/time if extremely large).

---

## 9) Reliability & Error Handling

* Network timeouts (e.g., 15s) and `raise_for_status()`.
* `try/except` around request; render a friendly error with a retry button.
* Validate JSON shape; fail gracefully if fields missing.
* Guard against `mag == None` or malformed coordinates.

---

## 10) Security & Privacy

* No secrets or API keys required.
* Don’t log PII; keep User‑Agent generic plus a contact email if you want.
* Pin library versions to known‑good ranges.

---

## 11) Observability

* Lightweight app logs: request duration, cache hits/misses, exceptions.
* Optional: add a tiny status panel in the sidebar with “Last fetched at … (UTC)” and feed URL.

---

## 12) Testing Strategy

* **Unit**: parsers (GeoJSON → DataFrame), color/size mapping, filter logic.
* **Integration**: mocked HTTP responses; cache layer behavior.
* **UI Smoke**: app boots, widgets render, no exceptions on basic flows.

---

## 13) Deployment

* **Local**: `pip install -r requirements.txt`, `streamlit run app.py`.
* **Streamlit Community Cloud**: connect GitHub repo; set Python version and requirements; enable “wide mode”.
* Add a `Procfile` only if deploying to other PaaS (optional).

---

## 14) Project Structure

```
earthquake-tracker/
├─ app.py
├─ src/
│  ├─ fetch.py          # USGS URL builder + requests + caching
│  ├─ transform.py      # GeoJSON → DataFrame normalization
│  ├─ viz.py            # pydeck layer builders, color/radius mapping
│  └─ ui.py             # sidebar widgets, table helpers
├─ tests/
│  ├─ test_transform.py
│  ├─ test_fetch.py
│  └─ test_filters.py
├─ assets/
│  └─ demo.gif          # Readme preview
├─ requirements.txt
└─ README.md
```

---

## 15) Detailed Module Design

### 15.1 `src/fetch.py`

**Responsibilities**

* Map period → USGS feed URL (day/week/month; choose `all_*`).
* GET with `User-Agent`, timeout, retry/backoff.
* Return `dict` GeoJSON.

**Key Functions**

```python
import streamlit as st, requests, time

UA = {"User-Agent": "EarthquakeTracker/1.0 (youremail@example.com)"}
BASE = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary"

@st.cache_data(ttl=600)
def fetch_geojson(period: str) -> dict:
    # period ∈ {"day", "week", "month"}
    url = f"{BASE}/all_{period}.geojson"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
```

### 15.2 `src/transform.py`

**Responsibilities**

* Normalize GeoJSON → DataFrame with validated fields.
* Convert epoch ms to pandas `datetime64[ns, UTC]`.

**Key Functions**

```python
import pandas as pd

def to_dataframe(geojson: dict) -> pd.DataFrame:
    feats = geojson.get("features", [])
    rows = []
    for f in feats:
        props = f.get("properties", {})
        coords = (f.get("geometry") or {}).get("coordinates") or [None, None, None]
        rows.append({
            "event_id": f.get("id"),
            "time": pd.to_datetime(props.get("time"), unit="ms", utc=True),
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2],
            "mag": props.get("mag"),
            "place": props.get("place"),
            "url": props.get("url"),
        })
    df = pd.DataFrame(rows).dropna(subset=["latitude", "longitude"])
    return df.sort_values("time", ascending=False)
```

### 15.3 `src/viz.py`

**Responsibilities**

* Build Pydeck `ScatterplotLayer` and `Deck` config.
* Map magnitude → radius and color.

**Key Functions**

```python
import pydeck as pdk

_DEF = {
    "min_mag": 0.0,
    "radius_scale": 10000,
    "radius_min": 3000,
}

# Simple color scale (G→Y→R). Color‑blind friendliness via size + tooltip text.

def color_from_mag(m):
    if m is None: return [128, 128, 128, 180]
    if m < 3: return [50, 180, 70, 160]
    if m < 5: return [230, 200, 40, 170]
    return [220, 60, 50, 190]

def radius_from_mag(m):
    if m is None: return _DEF["radius_min"]
    return int(_DEF["radius_min"] + m * _DEF["radius_scale"])

def globe_layer(df):
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[longitude, latitude]",
        get_radius="mag.apply(m)" if False else None,  # computed client‑side via get_radius below
        get_fill_color=[255, 255, 255],  # overridden by get_color
        pickable=True,
        radius_min_pixels=2,
        get_color="[mag_color_0, mag_color_1, mag_color_2, mag_color_3]",
    )
```

*(Implementation detail: precompute `mag_color_*` and `radius` columns in the DataFrame for performance and simple binding.)*

### 15.4 `src/ui.py`

**Responsibilities**

* Render sidebar, return selected filters.
* Render map/table and empty states.

**Key Snippet**

```python
import streamlit as st, pydeck as pdk

def sidebar():
    st.sidebar.header("Filters")
    period = st.sidebar.radio("Time window", ["day", "week", "month"], index=1)
    min_mag = st.sidebar.slider("Min magnitude", 0.0, 8.0, 3.0, 0.1)
    return period, min_mag

def render_map(df):
    view = pdk.ViewState(latitude=0, longitude=0, zoom=0.5)
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
```

---

## 16) App Flow (Pseudocode)

```python
import streamlit as st
from src.fetch import fetch_geojson
from src.transform import validate_and_convert_geojson
from src.ui import sidebar, render_map

st.set_page_config(page_title="Earthquake Tracker", layout="wide")
st.title("🌎 Real‑time Global Earthquake Tracker")

period, min_mag = sidebar()
raw = fetch_geojson(period)
df = validate_and_convert_geojson(raw)

# derive visuals
import numpy as np


def map_color(m):
  if np.isnan(m): return (128, 128, 128, 180)
  return (50, 180, 70, 160) if m < 3 else (230, 200, 40, 170) if m < 5 else (220, 60, 50, 190)


if "mag" in df:
  cols = list(zip(*df["mag"].fillna(np.nan).map(map_color)))
  df["mag_r"], df["mag_g"], df["mag_b"], df["mag_a"] = cols
  df["radius"] = df["mag"].fillna(0).apply(lambda m: 3000 + int(m * 10000))

filtered = df[df["mag"].fillna(-1) >= min_mag]
render_map(filtered)

st.subheader("Raw Data")
st.dataframe(filtered, use_container_width=True)
st.caption("Last fetched (UTC): " + str(st.session_state.get("_cache_info", "via cache")))
```

---

## 17) Accessibility & Internationalization

* Provide text legend for magnitude bins.
* Large hit‑targets for sliders; keyboard focus indicators.
* Time displayed in both UTC and user locale (optional) with ISO format.

---

## 18) Risks & Mitigations

* **Feed downtime** → show cached data + banner; retry after TTL.
* **Large payloads** → cap rows shown; pre‑aggregate counts by region for overview (future).
* **Pydeck rendering performance** → throttle point size, cluster in future if needed.

---

## 19) Future Enhancements

* Sound/desktop notifications for >5.5 magnitude events (with opt‑in).
* Region filters (bounding box, country).
* Clustering/heatmap layers; tectonic plate overlay.
* Shareable permalinks (encode filters in query params).
* Background job to store snapshots to a database for historical trends.

---

## 20) README Outline (for GitHub)

1. Hero GIF demo
2. What it does / screenshots
3. Tech stack (Streamlit, Pandas, Pydeck, Requests)
4. Run locally (`pip install -r requirements.txt`; `streamlit run app.py`)
5. Deployment (Streamlit Community Cloud)
6. Architecture & caching notes
7. Credits (USGS Earthquake Hazards Program)

---

## 21) Definition of Done

* App runs locally and on Streamlit Cloud
* Filters work; map + table render without errors
* Lint passes; basic tests green
* README includes GIF + deployment link
