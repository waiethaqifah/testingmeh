import streamlit as st
from streamlit_geolocation import geolocation
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

# Get the current location
location = geolocation(timeout=20)  # waits up to 20 seconds

if location is None:
    st.warning("⚠️ Location not detected yet. Make sure you allow location access.")
else:
    lat = location["latitude"]
    lon = location["longitude"]
    st.success(f"📍 Coordinates detected: {lat:.6f}, {lon:.6f}")

    # Reverse geocode
    try:
        geolocator = Nominatim(user_agent="gps_app")
        loc = geolocator.reverse((lat, lon), language="en")
        if loc and loc.address:
            st.success(f"🏠 Address: {loc.address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Error: {e}")

    # Display map with marker
    m = folium.Map(location=[lat, lon], zoom_start=16)
    folium.Marker([lat, lon], popup="📍 You are here").add_to(m)
    st_folium(m, width=700, height=450)
