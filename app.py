import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

COORD_FILE = "coords.json"

# JS + HTML to get GPS and store into file
gps_html = f"""
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
    <div id="map" style="height:400px; width:100%; margin-top:10px;"></div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
function getLocation() {{
    var status = document.getElementById('status');
    if (!navigator.geolocation) {{
        status.innerHTML = "Geolocation not supported by this browser.";
        return;
    }}
    navigator.geolocation.getCurrentPosition(
        function(pos) {{
            var lat = pos.coords.latitude;
            var lon = pos.coords.longitude;
            var acc = pos.coords.accuracy;

            status.innerHTML = "Latitude: " + lat.toFixed(6) + ", Longitude: " + lon.toFixed(6) + " (Accuracy ±" + acc + " m)";

            // Show map
            var map = L.map('map').setView([lat, lon], 16);
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {{
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }}).addTo(map);
            L.marker([lat, lon]).addTo(map)
                .bindPopup("📍 You are here<br>Accuracy ±" + acc + " m")
                .openPopup();

            // Send coordinates to Streamlit via fetch to a local server (simulate saving)
            fetch("/save_coords", {{
                method: "POST",
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{lat: lat, lon: lon, acc: acc}})
            }});
        }},
        function(err) {{ status.innerHTML = "Error: " + err.message; }},
        {{ enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }}
    );
}}
</script>
"""

components.html(gps_html, height=500)

# --- Python side ---
# Check if file exists
address = None
if os.path.exists(COORD_FILE):
    try:
        with open(COORD_FILE, "r") as f:
            data = json.load(f)
        lat = data["lat"]
        lon = data["lon"]
        acc = data.get("acc", 0)
        st.info(f"📍 Selected coordinates: {lat:.6f}, {lon:.6f}")

        geolocator = Nominatim(user_agent="gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            address = location.address
            st.success(f"✅ Confirmed detailed location: {address}")
    except Exception as e:
        st.warning(f"⚠️ Could not retrieve address from coordinates: {e}")
else:
    st.info("⚠️ Location not detected yet. Click the button above first.")

