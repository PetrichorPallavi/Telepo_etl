# app.py

import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from queries import search_places, get_tokyo_stations
import subprocess
from datetime import datetime
import os



st.set_page_config(layout="wide")
st.title("Tokyo Business Search Demo")


# -----------------------------
# Cache station list
# -----------------------------
@st.cache_data
def load_stations():
    stations_data = get_tokyo_stations()
    return {
        row.name: (row.lat, row.lon)
        for row in stations_data
    }


stations = load_stations()


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Search Settings")

search_term = st.sidebar.text_input("Search keyword", "cafe")

radius = st.sidebar.slider(
    "Radius (meters)",
    100,
    5000,
    500
)

station_name = st.sidebar.text_input("Station name (e.g. 秋葉原)", "秋葉原")

if station_name in stations:
    lat, lon = stations[station_name]

# -----------------------------
# Session state
# -----------------------------
if "results" not in st.session_state:
    st.session_state.results = None

if "center" not in st.session_state:
    st.session_state.center = None


# -----------------------------
# Search button
# -----------------------------
if st.sidebar.button("Search"):

    lat, lon = stations[station_name]

    results = search_places(
        search_term=search_term,
        lat=lat,
        lon=lon,
        radius=radius
    )

    st.session_state.results = results
    st.session_state.center = (lat, lon)


results = st.session_state.results

# -----------------------------
# UPDATE DATA BUTTON
# -----------------------------
st.sidebar.markdown("## 🔄 Data Control")

# Show last update
if os.path.exists("last_update.txt"):
    with open("last_update.txt", "r") as f:
        last_update = f.read()
else:
    last_update = "Never"

st.sidebar.write(f"Last Updated: {last_update}")

# Update button
if st.sidebar.button("Update Data"):
    st.write("DEBUG:Updating data... this may take a few minutes.")
    with st.spinner("Updating data... please wait ⏳"):
        try:
            st.write("DEBUG:running process...")
            # Step 1: OSM update
            subprocess.run([
                "docker", "exec", "tokyo_osm_updater",
                "osm2pgsql-replication", "update",
                "-d", "tokyo_osm", "-H", "postgis", "-U", "postgres"
            ], check=True)

            # Step 2: Refresh table
            st.write("DEBUG:refreshing business table...")
            subprocess.run(
                "docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/refresh_business_table.sql",
                shell=True,
                check=True
            )

            # Save timestamp
            st.write("DEBUG:saving timestamp...")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("last_update.txt", "w") as f:
                f.write(now)

            st.success("✅ Data updated successfully!")

        except Exception as e:
            st.error(f"❌ Update failed: {e}")
# -----------------------------
# Display results
# -----------------------------
if results:

    df = pd.DataFrame(results)

    df = df.rename(columns={
        "name": "Name",
        "amenity": "Amenity",
        "shop": "Shop",
        "address": "Address",
        "phone": "Phone",
        "website": "Website",
        "lat": "Latitude",
        "lon": "Longitude"
    })


    # # Build address safely
    # df["Address"] = (
    #     df.get("House No.", "").fillna("").astype(str) + " " +
    #     df.get("Street", "").fillna("").astype(str) + " " +
    #     df.get("City", "").fillna("").astype(str)
    # ).str.strip()


    # Clean table view
    table_df = df[[
        "Name",
        # "Amenity",
        # "Shop",
        "Address",
        "Phone",
        "Website"
    ]]


    # -----------------------------
    # Map
    # -----------------------------
    center_lat, center_lon = st.session_state.center

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15
    )

    folium.Marker(
        [center_lat, center_lon],
        tooltip=station_name,
        icon=folium.Icon(color="red")
    ).add_to(m)


    for _, r in df.iterrows():

        folium.Marker(
            [r["Latitude"], r["Longitude"]],
            tooltip=f"{r['Name']} ({r['Amenity'] or r['Shop']})"
        ).add_to(m)


    st.subheader("Map")

    st_folium(
        m,
        width=1200,
        height=600
    )


    # -----------------------------
    # Table
    # -----------------------------
    st.subheader("Business Results")

    st.dataframe(
        table_df,
        column_config={
            "Website": st.column_config.LinkColumn("Website")
        },
        use_container_width=True
    )


elif results is not None:

    st.warning("No results found.")