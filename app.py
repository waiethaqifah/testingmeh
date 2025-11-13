# app.py
import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

BACKEND_URL = "http://localhost:8000"  # Change if deployed

# HTML + JS to send coordinates to FastAPI
gps_html = f"""
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Get My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
    <div id="map" style="height:400px; width:100%; margin-top:10px;"></div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
async function getLocation() {{
    const status = document.getElementById("status");
    if (!navigator.geolocation) {{
        status.innerHTML = "Geolocation not supported.";
        return;
    }}
    navigator.geolocation.getCurrentPosition(async (pos) => {{
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        const acc = pos.coords.accuracy;
        status.innerHTML = `Latitude: ${lat.toFixed(6)}, Longitude: ${lon.toFixed(6)} (Accuracy ±${acc} m)`;

        // Show map
        var map = L.map('map').setView([lat, lon], 16);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);
        L.marker([lat, lon]).addTo(map)
            .bindPopup("📍 You are here<br>Accuracy ±" + acc + " m")
            .openPopup();

        // Send to FastAPI backend
        await fetch("{BACKEND_URL}/save_coords", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json"
            }},
            body: JSON.stringify({{lat: lat, lon: lon}})
        }});
    }},
    (err) => {{ status.innerHTML = "Error: " + err.message; }},
    {{enableHighAccuracy:true, timeout:20000}});
}}
</script>
"""

components.html(gps_html, height=500)

# Button to retrieve saved coordinates and show address
if st.button("Show Detected Address"):
    try:
        r = requests.get(f"{BACKEND_URL}/get_coords")
        data = r.json()
        lat = data.get("lat", 0.0)
        lon = data.get("lon", 0.0)

        if lat == 0.0 and lon == 0.0:
            st.warning("⚠️ Location not detected yet. Click the button above first.")
        else:
            st.info(f"📍 Selected coordinates: {lat:.6f}, {lon:.6f}")
            geolocator = Nominatim(user_agent="streamlit_gps_app")
            location = geolocator.reverse((lat, lon), language="en")
            if location and location.address:
                st.success(f"✅ Confirmed detailed location: {location.address}")
            else:
                st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
