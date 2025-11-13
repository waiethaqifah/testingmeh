import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

st.write("Click the button to get your location. Your address will be detected automatically.")

# Hidden input to store coordinates from JS
coords_input = st.text_input("coords_input", "", key="coords_input", label_visibility="collapsed")

# HTML + JS to detect GPS and update hidden input
gps_html = """
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Get My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
    <div id="map" style="height:400px; width:100%; margin-top:10px;"></div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
var map = L.map('map').setView([0,0],2);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

var marker;

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

            // Update map
            map.setView([lat, lon], 16);
            if (marker) map.removeLayer(marker);
            marker = L.marker([lat, lon]).addTo(map)
                .bindPopup(`📍 You are here<br>Accuracy ±${acc} m`)
                .openPopup();

            // Update hidden input to send coordinates to Streamlit
            const coordsInput = window.parent.document.querySelector('input[id="coords_input"]');
            if (coordsInput) {
                coordsInput.value = lat + "," + lon;
                coordsInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>
"""

components.html(gps_html, height=500)

# Read coordinates from hidden input
if coords_input:
    try:
        lat_str, lon_str = coords_input.split(",")
        lat = float(lat_str)
        lon = float(lon_str)

        st.info(f"📍 Selected coordinates: {lat:.6f}, {lon:.6f}")

        # Reverse geocode
        geolocator = Nominatim(user_agent="streamlit_gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            st.success(f"✅ Detected Address: {location.address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.error(f"⚠️ Error parsing coordinates: {e}")
else:
    st.info("⚠️ Location not detected yet. Click the button above first.")
