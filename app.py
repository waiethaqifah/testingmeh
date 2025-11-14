'''
import streamlit as st
import json
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Map and Address")

# Hidden input to receive JS coordinates
coords_json = st.text_input("coords_json", "", key="coords_json_hidden", label_visibility="collapsed")

# HTML + JS to get location and show Leaflet map, send data to Streamlit
gps_html = """
<div style="text-align:center; margin-bottom:10px;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
    <p id="status" style="margin-top:5px;">Waiting for location...</p>
    <input type="hidden" id="coords_json">
    <div id="map" style="height:500px; width:100%; margin-top:10px;"></div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
async function getLocation() {
    const status = document.getElementById('status');
    const coordsInput = document.getElementById('coords_json');

    if (!navigator.geolocation) {
        status.innerHTML = "Geolocation not supported by this browser.";
        return;
    }

    navigator.geolocation.getCurrentPosition(async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        const acc = pos.coords.accuracy;

        let address = "Unknown";
        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
            const data = await res.json();
            if(data && data.display_name) address = data.display_name;
        } catch(e) { address = "Could not get address"; }

        status.innerHTML = `<b>Coordinates:</b> ${lat.toFixed(6)}, ${lon.toFixed(6)}<br><b>Address:</b> ${address}`;

        // Show Leaflet map
        var map = L.map('map').setView([lat, lon], 16);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        L.marker([lat, lon]).addTo(map)
            .bindPopup("📍 You are here<br>Accuracy ±" + acc + " m")
            .openPopup();

        // Send coordinates & address to Streamlit hidden input
        coordsInput.value = JSON.stringify({lat: lat, lon: lon, address: address});
        coordsInput.dispatchEvent(new Event('input', { bubbles: true }));
    }, (err) => { status.innerHTML = "Error: " + err.message; }, { enableHighAccuracy:true });
}
</script>
"""

# Embed HTML+JS
st.components.v1.html(gps_html, height=600)

# Python side: read coordinates & address
if coords_json:
    try:
        loc = json.loads(coords_json)
        lat, lon, address = loc["lat"], loc["lon"], loc["address"]

        st.success(f"📍 Coordinates: {lat:.6f}, {lon:.6f}")
        st.success(f"✅ Address: {address}")

        # Show Folium map in Streamlit as well
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker([lat, lon], popup=f"📍 You are here\n{address}").add_to(m)
        st_folium(m, width=700, height=500)

    except Exception as e:
        st.warning(f"⚠️ Error parsing coordinates: {e}")
'''


import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

st.title("📍 Detect Location Test")

# Initialize session state
if 'coords_json' not in st.session_state:
    st.session_state.coords_json = ""

# Hidden input to receive coordinates
coords_json = st.text_input(
    "coords_json",
    st.session_state.coords_json,
    key="coords_input",
    label_visibility="collapsed"
)

# HTML + JS for geolocation
gps_html = """
<div style="text-align:center; margin-bottom:10px;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
    <p id="status" style="margin-top:5px;">Waiting for location...</p>
    <input type="hidden" id="coords_json">
</div>

<script>
async function getLocation() {
    const status = document.getElementById('status');
    const coordsInput = document.getElementById('coords_json');

    if (!navigator.geolocation) {
        status.innerHTML = "Geolocation not supported by this browser.";
        return;
    }

    navigator.geolocation.getCurrentPosition(async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        let address = "Unknown";
        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
            const data = await res.json();
            if(data && data.display_name) address = data.display_name;
        } catch(e) { address = "Could not get address"; }

        status.innerHTML = `<b>Coordinates:</b> ${lat.toFixed(6)}, ${lon.toFixed(6)}<br><b>Address:</b> ${address}`;

        // Send data to Python via hidden input
        coordsInput.value = JSON.stringify({lat: lat, lon: lon, address: address});
        coordsInput.dispatchEvent(new Event('input', { bubbles: true }));
    }, (err) => { status.innerHTML = "Error: " + err.message; }, { enableHighAccuracy:true });
}
</script>
"""

st.components.v1.html(gps_html, height=250)

# Parse coordinates in Python
lat, lon, address = None, None, None
if coords_json:
    try:
        loc = json.loads(coords_json)
        lat, lon, address = loc["lat"], loc["lon"], loc["address"]
        st.success(f"📍 Detected Address: {address}")
    except:
        st.warning("⚠️ Unable to parse location.")

# Save to CSV
if address and st.button("💾 Save Location to CSV"):
    df = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Latitude": lat,
        "Longitude": lon,
        "Address": address
    }])
    file_name = "test_locations.csv"
    if not os.path.exists(file_name):
        df.to_csv(file_name, mode='w', header=True, index=False)
    else:
        df.to_csv(file_name, mode='a', header=False, index=False)
    st.success(f"✅ Location saved to {file_name}")

