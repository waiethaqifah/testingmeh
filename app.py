import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import json
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

# Path to store coordinates
COORDS_FILE = "coords.json"

# --- Embed HTML + JS to get browser location ---
gps_html = """
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Get My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
</div>

<script>
function getLocation() {
    const status = document.getElementById('status');
    if (!navigator.geolocation) {
        status.innerHTML = "Geolocation not supported by your browser.";
        return;
    }
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const acc = pos.coords.accuracy;

            status.innerHTML = `Latitude: ${lat.toFixed(6)}, Longitude: ${lon.toFixed(6)} (Accuracy ±${acc} m)`;

            // Store coordinates in a JSON file via Streamlit
            const coords = {lat: lat, lon: lon};
            const jsonStr = JSON.stringify(coords);
            fetch("/_stcore/file/", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: jsonStr
            });

            // Send coordinates to Streamlit via window.postMessage
            window.parent.postMessage(coords, "*");
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>
"""

# Embed JS in Streamlit
components.html(gps_html, height=150)

# --- Read stored coordinates from JSON file ---
lat = lon = None
if os.path.exists(COORDS_FILE):
    try:
        with open(COORDS_FILE, "r") as f:
            data = json.load(f)
            lat = data.get("lat")
            lon = data.get("lon")
    except Exception as e:
        st.warning(f"⚠️ Could not read stored coordinates: {e}")

if lat is None or lon is None:
    st.warning("⚠️ Location not detected yet. Click the button above in the browser.")
else:
    st.success(f"📍 Detected Coordinates: {lat:.6f}, {lon:.6f}")

    # Reverse geocode
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

    # Show Folium map
    m = folium.Map(location=[lat, lon], zoom_start=16)
    folium.Marker([lat, lon], popup=f"You are here\n{address if 'address' in locals() else ''}").add_to(m)
    st_folium(m, width=700, height=500)
