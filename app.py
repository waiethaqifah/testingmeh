import streamlit as st
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim
import json
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

COORDS_FILE = "coords.json"

# --- Functions to read/store coordinates safely ---
def read_coords():
    if os.path.exists(COORDS_FILE):
        try:
            with open(COORDS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    if isinstance(data, list):
                        return data
        except Exception as e:
            st.warning(f"⚠️ Could not read coordinates from file: {e}")
    return []

def store_coords(lat, lon):
    coords_list = read_coords()
    coords_list.append({"lat": lat, "lon": lon})
    try:
        with open(COORDS_FILE, "w") as f:
            json.dump(coords_list, f, indent=2)
    except Exception as e:
        st.warning(f"⚠️ Could not store coordinates: {e}")

# --- JavaScript to detect location and send to Streamlit ---
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

            // Send coordinates to Streamlit via hidden input
            const input = document.getElementById('coords_input');
            input.value = lat + "," + lon;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        },
        (err) => { status.innerHTML = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
}
</script>
<input type="text" id="coords_input" style="display:none;">
"""

components.html(gps_html, height=500)

# --- Streamlit reads coordinates from the hidden input ---
coords = st.text_input("Hidden GPS input", value="", key="coords_hidden")

if coords:
    try:
        lat_str, lon_str = coords.split(",")
        lat = float(lat_str)
        lon = float(lon_str)

        # Store into coords.json
        store_coords(lat, lon)

        st.success(f"📍 Coordinates detected: {lat:.6f}, {lon:.6f}")

        # Reverse geocode to get address
        geolocator = Nominatim(user_agent="streamlit_gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            address = location.address
            st.success(f"✅ Address: {address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")

        # Display map again using Leaflet (optional)
        st.write(f"**Latitude:** {lat}, **Longitude:** {lon}")
    except Exception as e:
        st.warning(f"⚠️ Error processing coordinates: {e}")
else:
    st.info("⚠️ Location not detected yet. Click the button in the map first.")

# --- Display previous coordinates stored ---
all_coords = read_coords()
if all_coords:
    st.subheader("📜 Previous detected locations:")
    for idx, c in enumerate(all_coords[::-1], start=1):
        st.write(f"{idx}. Lat: {c['lat']}, Lon: {c['lon']}")
