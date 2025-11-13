import streamlit as st
from geopy.geocoders import Nominatim
import json
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address Storage")

COORDS_FILE = "coords.json"

# JavaScript to get location and send to Streamlit
gps_html = """
<button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
<p id="status" style="margin-top:10px;">Waiting for location...</p>
<input type="text" id="coords_input" style="display:none;"/>
<script>
function getLocation() {
    const status = document.getElementById('status');
    if (!navigator.geolocation) {
        status.innerText = "Geolocation not supported by your browser.";
        return;
    }
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const acc = pos.coords.accuracy;
            status.innerText = `Latitude: ${lat.toFixed(6)}, Longitude: ${lon.toFixed(6)} (Accuracy ±${acc} m)`;

            // send coords to Streamlit
            const input = document.getElementById("coords_input");
            input.value = JSON.stringify({lat: lat, lon: lon});
            input.dispatchEvent(new Event('input', { bubbles: true }));
        },
        (err) => { status.innerText = "Error: " + err.message; },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
}
</script>
"""

# Embed JS
components.html(gps_html, height=150)

# Streamlit reads hidden input
coords_json = st.text_input("coords_input", "", key="coords_input")

def store_coords(lat, lon):
    coords_list = []
    if os.path.exists(COORDS_FILE):
        try:
            with open(COORDS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    coords_list = json.loads(content)
        except Exception as e:
            st.warning(f"⚠️ Could not read existing coordinates: {e}")

    coords_list.append({"lat": lat, "lon": lon})

    try:
        with open(COORDS_FILE, "w") as f:
            json.dump(coords_list, f, indent=2)
    except Exception as e:
        st.warning(f"⚠️ Could not store coordinates: {e}")


def read_coords():
    if os.path.exists(COORDS_FILE):
        try:
            with open(COORDS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except Exception as e:
            st.warning(f"⚠️ Could not read coordinates from file: {e}")
    return []


# If JS sent coords, store them
if coords_json:
    try:
        data = json.loads(coords_json)
        store_coords(data["lat"], data["lon"])
        st.success(f"📍 Coordinates stored: {data['lat']:.6f}, {data['lon']:.6f}")
    except Exception as e:
        st.warning(f"⚠️ Error parsing coordinates: {e}")

# Read all stored coordinates and reverse geocode
all_coords = read_coords()
geolocator = Nominatim(user_agent="gps_tracker_app")

if all_coords:
    st.subheader("Stored Locations:")
    for idx, coord in enumerate(all_coords[::-1], start=1):  # show latest first
        lat = coord["lat"]
        lon = coord["lon"]
        try:
            location = geolocator.reverse((lat, lon), language="en")
            address = location.address if location else "Address not found"
        except Exception:
            address = "Could not retrieve address"
        st.write(f"{idx}. 📍 {address} (Lat: {lat:.6f}, Lon: {lon:.6f})")
else:
    st.info("⚠️ No location detected yet. Click the button above first.")
