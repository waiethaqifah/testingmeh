import streamlit as st
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim
import json
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

COORDS_FILE = "coords.json"

# Function to save coordinates and address to file
def save_coords(lat, lon, address):
    data = {"lat": lat, "lon": lon, "address": address}
    with open(COORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# Function to load saved coordinates
def load_coords():
    if os.path.exists(COORDS_FILE):
        try:
            with open(COORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

# Load previous coords if exist
saved = load_coords()
if saved:
    st.success(f"📍 Last saved location: {saved.get('address', 'Unknown')}")
    st.map([[saved['lat'], saved['lon']]])

# HTML + JS to detect user location automatically
gps_html = """
<div style="text-align:center;">
    <p id="status">Detecting location...</p>
    <div id="map" style="height:400px; width:100%; margin-top:10px;"></div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
navigator.geolocation.getCurrentPosition(
    function(position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const acc = position.coords.accuracy;

        document.getElementById("status").innerHTML = 
            `Latitude: ${lat.toFixed(6)}, Longitude: ${lon.toFixed(6)} (Accuracy ±${acc} m)`;

        // Show map
        var map = L.map('map').setView([lat, lon], 16);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        L.marker([lat, lon]).addTo(map)
            .bindPopup("📍 You are here<br>Accuracy ±" + acc + " m")
            .openPopup();

        // Send coords back to Streamlit
        const coordsBox = document.getElementById("coords_box");
        coordsBox.value = lat + "," + lon;
        coordsBox.dispatchEvent(new Event('input', { bubbles: true }));
    },
    function(error) {
        document.getElementById("status").innerHTML = "Error: " + error.message;
    },
    { enableHighAccuracy: true }
);
</script>
<input type="text" id="coords_box" style="display:none;">
"""

components.html(gps_html, height=500)

# Streamlit reads the hidden input
coords_input = st.text_input("Detected Coordinates (hidden)", value="", key="coords_box")

if coords_input:
    try:
        lat, lon = map(float, coords_input.split(","))
        st.info(f"📍 Detected coordinates: {lat:.6f}, {lon:.6f}")

        geolocator = Nominatim(user_agent="streamlit_gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            address = location.address
            st.success(f"✅ Confirmed location: {address}")
            save_coords(lat, lon, address)  # save to coords.json
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Error parsing coordinates: {e}")
else:
    st.info("⏳ Detecting location automatically...")
