import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

COORDS_FILE = "coords.json"

# JS + Leaflet map to get coordinates
gps_html = """
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
    <div id="map" style="height:400px; width:100%; margin-top:10px;"></div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
function getLocation() {
    const status = document.getElementById('status');
    if (!navigator.geolocation) {
        status.innerHTML = "Geolocation not supported by this browser.";
        return;
    }
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const acc = pos.coords.accuracy;

            status.innerHTML = `Latitude: ${lat.toFixed(6)}, Longitude: ${lon.toFixed(6)} (Accuracy ±${acc} m)`;

            // Show map
            var map = L.map('map').setView([lat, lon], 16);
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
            L.marker([lat, lon]).addTo(map)
                .bindPopup("📍 You are here<br>Accuracy ±" + acc + " m")
                .openPopup();

            // Send coordinates to Streamlit via hidden input
            const coordsInput = window.parent.document.getElementById('coords_input');
            coordsInput.value = JSON.stringify({lat: lat, lon: lon});
            coordsInput.dispatchEvent(new Event('input', { bubbles: true }));
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>

<input type="text" id="coords_input" style="display:none;">
"""

# Embed the HTML in Streamlit
components.html(gps_html, height=500)

# Hidden input to get coordinates from JS
coords_json = st.text_input("coords", "", key="coords_input")

# Save to file if detected
if coords_json:
    try:
        coords_data = json.loads(coords_json)
        with open(COORDS_FILE, "w") as f:
            json.dump(coords_data, f)
    except Exception as e:
        st.warning(f"⚠️ Failed to save coordinates: {e}")

# Read coordinates from file
if os.path.exists(COORDS_FILE):
    try:
        with open(COORDS_FILE, "r") as f:
            data = json.load(f)
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is not None and lon is not None:
            st.info(f"📍 Selected coordinates: {lat:.6f}, {lon:.6f}")
            # Reverse geocode
            geolocator = Nominatim(user_agent="gps_app")
            location = geolocator.reverse((lat, lon), language="en")
            if location and location.address:
                st.success(f"✅ Detected Location: {location.address}")
            else:
                st.warning("⚠️ Could not retrieve address from coordinates.")
        else:
            st.warning("⚠️ Location not detected yet. Click the button in the map first.")
    except Exception as e:
        st.warning(f"⚠️ Error reading coordinates from file: {e}")
else:
    st.warning("⚠️ Location not detected yet. Click the button in the map first.")
