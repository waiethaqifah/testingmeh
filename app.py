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
import json

st.set_page_config(page_title="📍 GPS Tracker + Map + Address", page_icon="🗺️")
st.title("📍 GPS Tracker with Map and Address")

coords_file = "coords.json"

# --- JS + HTML ---
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

            // Save to file via Streamlit endpoint
            fetch('/save_coords', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({lat: lat, lon: lon})
            });
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>
"""

# Embed JS
components.html(gps_html, height=500)

# --- Python server-side endpoint ---
def save_coords(lat, lon):
    with open(coords_file, "w") as f:
        json.dump({"lat": lat, "lon": lon}, f)

# --- Check if file exists and read ---
if os.path.exists(coords_file):
    with open(coords_file, "r") as f:
        data = json.load(f)
        lat, lon = data.get("lat"), data.get("lon")
        if lat and lon:
            st.info(f"📍 Coordinates: {lat:.6f}, {lon:.6f}")

            # Reverse geocode
            geolocator = Nominatim(user_agent="gps_app")
            try:
                location = geolocator.reverse((lat, lon), language="en")
                if location and location.address:
                    st.success(f"✅ Detected Address: {location.address}")
                else:
                    st.warning("⚠️ Could not retrieve address.")
            except Exception as e:
                st.error(f"⚠️ Reverse geocode error: {e}")

            st.markdown(f"[🌍 Open in Google Maps](https://www.google.com/maps?q={lat},{lon})")

