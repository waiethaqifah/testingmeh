import streamlit as st
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim
import json
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

# File to store coordinates
COORDS_FILE = "coords.json"

# --- HTML + JS for getting location ---
gps_html = """
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Get My Location</button>
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

            // Store coordinates in hidden input for Streamlit
            const coordsInput = document.getElementById("coords_input");
            coordsInput.value = JSON.stringify({lat: lat, lon: lon});
            coordsInput.dispatchEvent(new Event('input', { bubbles: true }));
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>

<input type="hidden" id="coords_input">
"""

# Embed HTML in Streamlit
components.html(gps_html, height=500)

# --- Streamlit side: read coordinates from hidden input and store in JSON ---
coords_str = st.experimental_get_query_params().get("coords_input", [""])[0]

# Streamlit hidden text input for JS to write to
coords_input = st.text_input("", key="coords_input", value="", label_visibility="collapsed")

if coords_input:
    try:
        coords_data = json.loads(coords_input)
        lat = coords_data.get("lat")
        lon = coords_data.get("lon")
        if lat is not None and lon is not None:
            # Save to JSON file
            with open(COORDS_FILE, "w") as f:
                json.dump({"lat": lat, "lon": lon}, f)
    except Exception as e:
        st.warning(f"⚠️ Error storing coordinates: {e}")

# --- Read coordinates from JSON file safely ---
lat, lon = None, None
if os.path.exists(COORDS_FILE):
    try:
        with open(COORDS_FILE, "r") as f:
            content = f.read().strip()
        if content:
            data = json.loads(content)
            lat = data.get("lat")
            lon = data.get("lon")
    except Exception as e:
        st.warning(f"⚠️ Error reading coordinates from file: {e}")

# --- Reverse geocode and display ---
if lat is not None and lon is not None:
    st.info(f"📍 Detected coordinates: {lat:.6f}, {lon:.6f}")
    try:
        geolocator = Nominatim(user_agent="gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            st.success(f"✅ Detected Address: {location.address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Error reverse geocoding: {e}")
else:
    st.warning("⚠️ Location not detected yet. Click the button in the map first.")
