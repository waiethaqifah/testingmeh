import streamlit as st
from streamlit_geolocation import geolocation
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

# Get geolocation
with st.spinner("Detecting your location..."):
    loc = geolocation()
    
if loc is None:
    st.warning("⚠️ Location not detected yet. Make sure to allow location access in your browser.")
else:
    lat = loc["lat"]
    lon = loc["lon"]
    st.success(f"📍 Detected Coordinates: {lat:.6f}, {lon:.6f}")

    # Reverse geocode to get address
    try:
        geolocator = Nominatim(user_agent="gps_tracker_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            address = location.address
            st.success(f"✅ Address: {address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Geocoding error: {e}")

    # Show folium map
    m = folium.Map(location=[lat, lon], zoom_start=16)
    folium.Marker([lat, lon], popup=f"You are here\n{address if 'address' in locals() else ''}").add_to(m)
    st_folium(m, width=700, height=500)
