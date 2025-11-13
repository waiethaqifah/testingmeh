import streamlit as st
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim
import json
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

# File to store coordinates
COORD_FILE = "coords.txt"

# JS + HTML to get current location
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
    var status = document.getElementById("status");
    if (!navigator.geolocation) {
        status.innerHTML = "Geolocation not supported.";
        return;
    }
    navigator.geolocation.getCurrentPosition(function(pos) {
        var lat = pos.coords.latitude;
        var lon = pos.coords.longitude;
        var acc = pos.coords.accuracy;

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

        // Send coordinates to Streamlit via file
        fetch("/save_coords", {
            method: "POST",
            body: JSON.stringify({lat: lat, lon: lon}),
            headers: {"Content-Type": "application/json"}
        });
    }, function(err) {
        status.innerHTML = "Error: " + err.message;
    }, {enableHighAccuracy:true, timeout:20000});
}
</script>
"""

# Embed the JS
components.html(gps_html, height=500)

# --- Python side ---
# Load coordinates from file if exists
lat, lon = None, None
if os.path.exists(COORD_FILE):
    try:
        with open(COORD_FILE, "r") as f:
            data = json.load(f)
            lat, lon = data.get("lat"), data.get("lon")
    except Exception as e:
        st.warning(f"⚠️ Error reading coordinates from file: {e}")

# If we have coordinates, show map and address
if lat is not None and lon is not None:
    st.success(f"📍 Detected coordinates: Latitude {lat:.6f}, Longitude {lon:.6f}")
    # Reverse geocode
    try:
        geolocator = Nominatim(user_agent="streamlit_gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            address = location.address
            st.success(f"✅ Address: {address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Geocoding error: {e}")
else:
    st.info("⚠️ Location not detected yet. Click the button above first.")

# Optional: show Google Maps link
if lat is not None and lon is not None:
    st.markdown(f"[🌍 Open in Google Maps](https://www.google.com/maps?q={lat},{lon})")

