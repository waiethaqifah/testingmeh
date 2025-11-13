import streamlit as st
from geopy.geocoders import Nominatim
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address & Map")

# Hidden text input to get coords from JS
coords_json = st.text_input("coords_json", "")

# JS HTML to detect location and fill hidden input
js_code = """
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
</div>
<script>
async function getLocation() {
    const status = document.getElementById('status');
    if (!navigator.geolocation) {status.innerHTML="Geolocation not supported"; return;}
    
    navigator.geolocation.getCurrentPosition(async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        let address="Unknown";
        try {
            const resp = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
            const data = await resp.json();
            if(data && data.display_name){ address = data.display_name; }
        } catch(e){ address="Could not get address"; }
        status.innerHTML=`<b>Coordinates:</b> ${lat.toFixed(6)}, ${lon.toFixed(6)}<br><b>Address:</b> ${address}`;
        document.querySelector('input[id="coords_json"]').value = JSON.stringify({lat:lat, lon:lon, address:address});
        document.querySelector('input[id="coords_json"]').dispatchEvent(new Event('input',{bubbles:true}));
    }, err => {status.innerHTML="Error: "+err.message;}, {enableHighAccuracy:true});
}
</script>
"""

# Render the JS
components.html(js_code, height=150)

# If JS has set coordinates, show map
if coords_json:
    try:
        loc = json.loads(coords_json)
        lat, lon, address = loc["lat"], loc["lon"], loc["address"]

        st.success(f"📍 Coordinates: {lat:.6f}, {lon:.6f}")
        st.success(f"✅ Address: {address}")

        # Leaflet map HTML
        map_html = f"""
        <div id="map" style="height:500px; width:100%; margin-top:10px;"></div>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([{lat}, {lon}], 16);
            L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }}).addTo(map);
            L.marker([{lat}, {lon}]).addTo(map)
                .bindPopup("📍 You are here<br>{address}")
                .openPopup();
        </script>
        """
        components.html(map_html, height=500)

    except Exception as e:
        st.warning(f"⚠️ Error parsing coordinates: {e}")
