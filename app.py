import streamlit as st
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address")

# Path for temporary coordinate storage
COORD_FILE = "coords.json"

# --- HTML + JS for getting GPS and saving to JSON via Streamlit ---
gps_html = f"""
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
</div>

<script>
async function getLocation() {{
    const status = document.getElementById('status');
    if (!navigator.geolocation) {{
        status.innerHTML = "Geolocation not supported by this browser.";
        return;
    }}

    navigator.geolocation.getCurrentPosition(
        async (pos) => {{
            const lat = pos.coords.latitude.toFixed(6);
            const lon = pos.coords.longitude.toFixed(6);
            const acc = pos.coords.accuracy.toFixed(1);
            status.innerHTML = `Latitude: ${lat}, Longitude: ${lon} (Accuracy ±${acc} m)`;

            // Save coordinates to Streamlit server via fetch API
            const response = await fetch("/save_coords", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},
                body: JSON.stringify({{lat: lat, lon: lon}})
            }});
        }},
        (err) => {{ status.innerHTML = "Error: " + err.message; }},
        {{ enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }}
    );
}}
</script>
"""

# --- Display JS button ---
components.html(gps_html, height=150)

# --- Save endpoint for JS to call ---
from fastapi import FastAPI, Request
from streamlit.web.server import server

app: FastAPI = server.get_current()._app

@app.post("/save_coords")
async def save_coords(req: Request):
    data = await req.json()
    with open(COORD_FILE, "w") as f:
        json.dump(data, f)
    return {"status": "ok"}

# --- Python reads the stored coordinates ---
if os.path.exists(COORD_FILE):
    try:
        with open(COORD_FILE, "r") as f:
            coords = json.load(f)
        lat = float(coords["lat"])
        lon = float(coords["lon"])

        st.success(f"📍 Coordinates detected: Latitude {lat}, Longitude {lon}")

        # Reverse geocode
        geolocator = Nominatim(user_agent="streamlit_gps_app")
        location = geolocator.reverse((lat, lon), language="en")
        if location and location.address:
            st.success(f"✅ Detected Address: {location.address}")
        else:
            st.warning("⚠️ Could not retrieve address from coordinates.")

    except Exception as e:
        st.error(f"⚠️ Error reading coordinates or geocoding: {e}")
else:
    st.info("Click the 'Detect My Location' button above and allow location permission.")
