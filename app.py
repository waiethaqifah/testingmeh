import json
import streamlit as st
from geopy.geocoders import Nominatim

st.title("📍 GPS Tracker with Address")

# Load coordinates from file
coords_file = "coords.json"

try:
    with open(coords_file, "r") as f:
        data = json.load(f)
        lat = float(data.get("lat", 0))
        lon = float(data.get("lon", 0))
except Exception:
    lat = lon = None

if lat is not None and lon is not None:
    st.write(f"**Detected Coordinates:** {lat:.6f}, {lon:.6f}")

    try:
        geolocator = Nominatim(user_agent="gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            st.success(f"📍 Detected Address: {location.address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Error: {e}")
else:
    st.info("⚠️ Location not detected yet. Click the button in the map first.")
