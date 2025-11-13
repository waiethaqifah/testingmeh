import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
import json, os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 Automatic GPS Tracker with Address")

COORDS_FILE = "coords.json"

def save_coords(lat, lon, address):
    with open(COORDS_FILE, "w", encoding="utf-8") as f:
        json.dump({"lat": lat, "lon": lon, "address": address}, f)

def load_coords():
    if os.path.exists(COORDS_FILE):
        with open(COORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# Get browser location through the component
location = streamlit_geolocation()

if location:
    lat, lon = location["latitude"], location["longitude"]
    st.write(f"**Detected:** {lat:.6f}, {lon:.6f}")

    geolocator = Nominatim(user_agent="streamlit_gps_app")
    loc = geolocator.reverse((lat, lon), language="en")
    address = loc.address if loc else "Address not found"
    st.success(address)

    save_coords(lat, lon, address)
    st.map([[lat, lon]])

else:
    st.info("⏳ Waiting for browser location permission...")

# Show last saved
last = load_coords()
if last:
    st.caption(f"Last saved: {last['address']}")
