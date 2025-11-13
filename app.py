import streamlit as st
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address & Map")

# pip install streamlit-geolocation streamlit-folium folium geopy
try:
    from streamlit_geolocation import geolocation
except ImportError:
    st.error("Please install streamlit-geolocation: pip install streamlit-geolocation")
    st.stop()

# Detect location automatically
user_location = geolocation(timeout=10)

if user_location:
    lat = user_location["lat"]
    lon = user_location["lon"]
    st.success(f"📍 Detected Coordinates: {lat:.6f}, {lon:.6f}")

    # Reverse geocode to get address
    try:
        geolocator = Nominatim(user_agent="gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            st.success(f"🏠 Address: {location.address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Error: {e}")

    # Show map with marker
    m = folium.Map(location=[lat, lon], zoom_start=16)
    folium.Marker([lat, lon], tooltip="You are here", popup=f"Address:\n{location.address}").add_to(m)
    st_folium(m, width=700, height=500)

else:
    st.info("⚠️ Location not detected. Make sure you allow location access in your browser.")
