'''
import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components
import html

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

# HTML + JS to get current location
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

            // Send coordinates to Streamlit
            window.parent.postMessage({lat: lat, lon: lon}, "*");
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>
"""

# Embed the HTML
components.html(gps_html, height=500)

# Listen to JS message and reverse geocode
coords = st.experimental_get_query_params()  # placeholder for later if needed

# Instead of the textarea hack, we can use a simple workaround:
# The JS sends the coordinates via postMessage, but Streamlit cannot catch it directly
# So we can ask user to click the button and then manually input lat/lon in a small input box (for iOS Safari compatibility)
lat = st.number_input("Latitude", value=0.0, format="%.6f")
lon = st.number_input("Longitude", value=0.0, format="%.6f")
click_btn = st.button("Get Address from Coordinates")

if click_btn:
    try:
        geolocator = Nominatim(user_agent="gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            address = location.address
            st.success(f"📍 Detected Address: {address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Error: {e}")
'''
import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

COORD_FILE = "coords.txt"

# HTML + JS to detect location and write to hidden textarea
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
            status.innerHTML = "Latitude: " + lat.toFixed(6) + ", Longitude: " + lon.toFixed(6) + " (Accuracy ±" + acc + " m)";

            // Show map
            var map = L.map('map').setView([lat, lon], 16);
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
            L.marker([lat, lon]).addTo(map)
                .bindPopup("📍 You are here<br>Accuracy ±" + acc + " m")
                .openPopup();

            // Send coords to Streamlit hidden textarea
            const coordsArea = window.parent.document.getElementById("coords_input");
            if (coordsArea) {
                coordsArea.value = JSON.stringify({lat: lat, lon: lon});
                coordsArea.dispatchEvent(new Event('input', { bubbles: true }));
            }
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>

<textarea id="coords_input" style="display:none;"></textarea>
"""

components.html(gps_html, height=500)

# Read hidden textarea (JSON)
coords_json = st.text_area("coords_input", "", height=1, label_visibility="collapsed")

lat = lon = None

# Parse JSON and store to file
if coords_json:
    import json
    try:
        data = json.loads(coords_json)
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is not None and lon is not None:
            with open(COORD_FILE, "w") as f:
                f.write(f"{lat},{lon}")
    except json.JSONDecodeError:
        st.warning("⚠️ Could not parse coordinates JSON.")

# If file exists, read from it
if (lat is None or lon is None) and os.path.exists(COORD_FILE):
    try:
        with open(COORD_FILE, "r") as f:
            file_text = f.read().strip()
            if file_text:
                lat, lon = map(float, file_text.split(","))
    except Exception as e:
        st.warning(f"⚠️ Error reading coordinates from file: {e}")

# Reverse geocode if we have coordinates
if lat is not None and lon is not None:
    st.info(f"📍 Detected coordinates: {lat:.6f}, {lon:.6f}")
    try:
        geolocator = Nominatim(user_agent="gps_tracker_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            st.success(f"✅ Final Location: {location.address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("⚠️ Location not detected yet. Click the button above first.")
