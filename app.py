import streamlit as st
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Address & Map")

# Hidden text input for JS to fill coordinates
coords_json = st.text_input("coords_json", "")

# JS to detect location and put it in the hidden input
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

st.components.v1.html(js_code, height=150)

# If JS has detected coordinates, parse them and display map
if coords_json:
    try:
        loc = json.loads(coords_json)
        lat, lon, address = loc["lat"], loc["lon"], loc["address"]

        st.success(f"📍 Coordinates: {lat:.6f}, {lon:.6f}")
        st.success(f"✅ Address: {address}")

        # Create a folium map
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker([lat, lon], popup=f"📍 You are here\n{address}").add_to(m)

        # Display map using streamlit_folium
        st_folium(m, width=700, height=500)

    except Exception as e:
        st.warning(f"⚠️ Error parsing coordinates: {e}")
