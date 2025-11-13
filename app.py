import streamlit as st
import json
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="📍 GPS Tracker", page_icon="🗺️")
st.title("📍 GPS Tracker with Map and Address")

# Empty placeholder for hidden input
coords_holder = st.empty()

# Hidden HTML input
coords_html = """
<input type="hidden" id="coords_json_hidden">
<div style="text-align:center; margin-bottom:10px;">
  <button onclick="getLocation()" style="padding:10px 20px; font-size:16px;">📍 Detect My Location</button>
  <p id="status">Waiting for location...</p>
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
    let address = "Unknown";
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
      const data = await res.json();
      if (data && data.display_name) { address = data.display_name; }
    } catch(e){ address = "Could not get address"; }
    status.innerHTML = `<b>Coordinates:</b> ${lat.toFixed(6)}, ${lon.toFixed(6)}<br><b>Address:</b> ${address}`;
    
    // send to Streamlit
    document.getElementById('coords_json_hidden').value = JSON.stringify({lat: lat, lon: lon, address: address});
    document.getElementById('coords_json_hidden').dispatchEvent(new Event('input', { bubbles: true }));
  }, (err) => { status.innerHTML = "Error: "+err.message; }, { enableHighAccuracy:true });
}
</script>
"""
coords_holder.components.html(coords_html, height=150)

# Read the hidden input value from Streamlit
coords_json = st.session_state.get("coords_json_hidden", "")

if coords_json:
    try:
        loc = json.loads(coords_json)
        lat, lon, address = loc["lat"], loc["lon"], loc["address"]

        st.success(f"📍 Coordinates: {lat:.6f}, {lon:.6f}")
        st.success(f"✅ Address: {address}")

        # Folium map
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker([lat, lon], popup=f"📍 You are here\n{address}").add_to(m)
        st_folium(m, width=700, height=500)
    except Exception as e:
        st.warning(f"⚠️ Error parsing coordinates: {e}")
