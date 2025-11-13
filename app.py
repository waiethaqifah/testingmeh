import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

# HTML + JS
gps_html = """
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
    <div id="map" style="height:400px; width:100%; margin-top:10px;"></div>
</div>

<input type="text" id="coords_input" style="display:none;">

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
function getLocation() {
    const status = document.getElementById('status');
    const coordsInput = document.getElementById('coords_input');

    if (!navigator.geolocation) {
        status.innerHTML = "Geolocation not supported.";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude.toFixed(6);
            const lon = pos.coords.longitude.toFixed(6);
            const acc = pos.coords.accuracy.toFixed(1);

            status.innerHTML = `Latitude: ${lat}, Longitude: ${lon} (Accuracy ±${acc} m)`;

            // Show map
            var map = L.map('map').setView([lat, lon], 16);
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
            L.marker([lat, lon]).addTo(map)
                .bindPopup("📍 You are here<br>Accuracy ±" + acc + " m")
                .openPopup();

            // Write coordinates to hidden input for Streamlit
            coordsInput.value = lat + "," + lon;
            coordsInput.dispatchEvent(new Event('input', { bubbles: true }));
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>
"""

# Embed HTML
components.html(gps_html, height=500)

# Streamlit reads the hidden input
coords = st.text_input("hidden_coords", value="", label_visibility="collapsed")

if coords:
    try:
        lat_str, lon_str = coords.split(",")
        lat = float(lat_str)
        lon = float(lon_str)

        # Reverse geocode automatically
        geolocator = Nominatim(user_agent="gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            st.success(f"📍 Detected Address: {location.address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")
    except Exception as e:
        st.warning(f"⚠️ Error: {e}")
else:
    st.info("⚠️ Location not detected yet. Click the button above.")
