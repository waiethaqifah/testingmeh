import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address & Map")

# HTML + JS to detect location and reverse geocode
gps_html = """
<div style="text-align:center;">
    <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
    <p id="status" style="margin-top:10px;">Waiting for location...</p>
</div>

<script>
async function getLocation() {
    const status = document.getElementById('status');
    if (!navigator.geolocation) {
        status.innerHTML = "Geolocation not supported by this browser.";
        return;
    }

    navigator.geolocation.getCurrentPosition(async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        // Reverse geocode using Nominatim
        let address = "Unknown";
        try {
            const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`;
            const resp = await fetch(url);
            const data = await resp.json();
            if (data && data.display_name) {
                address = data.display_name;
            }
        } catch (e) {
            address = "Could not retrieve address";
        }

        status.innerHTML = `<b>Detected:</b> ${lat.toFixed(6)}, ${lon.toFixed(6)}<br><b>Address:</b> ${address}`;

        // Send coordinates + address to Streamlit
        const message = {lat: lat, lon: lon, address: address};
        window.parent.postMessage({isStreamlitMessage: true, data: message}, "*");
    }, (err) => {
        status.innerHTML = "Error: " + err.message;
    }, {enableHighAccuracy:true, timeout:20000});
}
</script>
<input type="hidden" id="coords_json">
"""

# Embed the GPS detector
components.html(gps_html, height=150)

# JS listener to fill hidden input
components.html("""
<script>
window.addEventListener("message", (event) => {
    if(event.data && event.data.isStreamlitMessage){
        const loc = event.data.data;
        const coordsEl = document.getElementById("coords_json");
        coordsEl.value = JSON.stringify(loc);
        coordsEl.dispatchEvent(new Event('input', { bubbles: true }));
    }
});
</script>
<input type="text" id="coords_input" style="display:none;">
""", height=0)

# Streamlit input that receives the JS data
coords_json = st.text_input("coords_input", "")

# Store latest location in session state
if "latest_location" not in st.session_state:
    st.session_state["latest_location"] = None

if coords_json:
    try:
        loc_data = json.loads(coords_json)
        st.session_state["latest_location"] = loc_data
    except:
        pass

# Display the latest detected location and Leaflet map
if st.session_state["latest_location"]:
    loc = st.session_state["latest_location"]
    lat = loc["lat"]
    lon = loc["lon"]
    address = loc["address"]

    st.success(f"📍 Coordinates: {lat:.6f}, {lon:.6f}\n✅ Address: {address}")

    # Leaflet map
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

    # Render the map using st.components.v1.html
    components.html(map_html, height=500)
