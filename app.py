import streamlit as st
import json
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# --- Configuration ---
COORDS_FILE = "coords.json"

# --- Set up Streamlit Page ---
st.set_page_config(
    page_title="Automatic Location Tracker",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🗺️ Automatic Browser Location Detector")
st.markdown("""
This application uses your browser's Geolocation API to instantly find your position, 
display it on a map (Leaflet), and uses Python's `geopy` library to convert the 
coordinates into a readable address for display and file storage.
""")

# --- Helper Functions (Python Side) ---

def load_coordinates():
    """Reads coordinates from the JSON file."""
    if os.path.exists(COORDS_FILE):
        try:
            with open(COORDS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error(f"Error reading {COORDS_FILE}: File is corrupted.")
            return None
    return None

def save_coordinates(lat, lon):
    """Saves coordinates to the JSON file."""
    data = {"latitude": lat, "longitude": lon, "timestamp": time.time()}
    with open(COORDS_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    st.session_state['last_saved_coords'] = data # Update session state for immediate display

def geocode_coordinates(lat, lon):
    """Uses geopy to reverse geocode coordinates to an address."""
    # Use a custom user_agent as required by Nominatim
    geolocator = Nominatim(user_agent="location_tracker_app_by_gemini")
    try:
        # Retry logic for robust geocoding
        for attempt in range(3):
            location = geolocator.reverse((lat, lon), timeout=10)
            if location:
                return location.address
            time.sleep(2 ** attempt) # Exponential backoff
        return "Geocoding failed after multiple attempts."
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        return f"Geocoding failed: {e}"

# --- JavaScript Component (Injected via Streamlit) ---

# This function generates the HTML/JS component. The JS part is responsible for:
# 1. Getting location via navigator.geolocation.
# 2. Rendering the Leaflet map.
# 3. Finding the hidden Streamlit input and button in the parent frame.
# 4. Updating the input value and clicking the submit button to force a Streamlit rerun.
def inject_geolocation_js(hidden_input_id, hidden_submit_id):
    js_code = f"""
    <head>
        <!-- Load Leaflet CSS and JS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <style>
            #mapid {{ 
                height: 300px; 
                width: 100%; 
                border-radius: 0.75rem; 
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            }}
            .loading {{
                display: flex; justify-content: center; align-items: center; 
                height: 300px; background-color: #e5e7eb; border-radius: 0.75rem;
                font-family: 'Inter', sans-serif; color: #4b5563; font-weight: 600;
                font-size: 1.125rem;
            }}
        </style>
    </head>
    <body>
        <div id="mapid" class="loading">Locating You...</div>
        <script>
            // This is the crucial part: selecting the hidden Streamlit elements 
            // by their generated data-testid and aria-label attributes.
            const coordInput = window.parent.document.querySelector('[data-testid="stTextInput"] [aria-label="{hidden_input_id}"]');
            const submitButton = window.parent.document.querySelector('[data-testid="stFormSubmitButton"] button[aria-label="{hidden_submit_id}"]');
            
            if (!coordInput || !submitButton) {{
                // Fallback for debugging if elements cannot be found
                console.error("Could not find hidden Streamlit elements in parent frame.");
                return;
            }}

            function success(pos) {{
                const crd = pos.coords;
                const lat = crd.latitude;
                const lon = crd.longitude;
                const coordinates = `${{lat}},${{lon}}`;
                
                // 1. Render Leaflet Map
                const mapDiv = document.getElementById('mapid');
                mapDiv.classList.remove('loading');
                
                const map = L.map('mapid').setView([lat, lon], 14);
                
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: 'Map data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }}).addTo(map);
                
                L.marker([lat, lon]).addTo(map)
                    .bindPopup('Your Detected Location')
                    .openPopup();
                
                // 2. Pass coordinates to Streamlit via the hidden input
                coordInput.value = coordinates;
                
                // Simulate a change event to notify Streamlit's React frontend
                const event = new Event('change', {{ bubbles: true }});
                coordInput.dispatchEvent(event);

                // 3. Click the hidden submit button to trigger a rerun (Python processing)
                // Short delay to ensure the input value is registered first
                setTimeout(() => {{
                    submitButton.click();
                }}, 100); 
            }}

            function error(err) {{
                const mapDiv = document.getElementById('mapid');
                mapDiv.innerHTML = '<div style="color: #ef4444; font-weight: 700; text-align: center; padding: 1rem;">ERROR: Location access denied or unavailable. Please check your browser settings. (' + err.message + ')</div>';
                console.warn(`Geolocation Error: ${{err.message}}`);
            }}

            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(success, error, {{ enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }});
            }} else {{
                document.getElementById('mapid').innerHTML = '<div style="color: #ef4444; font-weight: 700; text-align: center; padding: 1rem;">Geolocation is not supported by this browser.</div>';
            }}

        </script>
    </body>
    """
    
    st.components.v1.html(js_code, height=370, scrolling=False)


# --- Main Streamlit Execution Flow ---

# 1. Create the hidden form elements for data transfer
# We must use st.form to capture the data and force a rerun only when the JS triggers it.
with st.form(key="geolocation_form", clear_on_submit=False):
    # Hidden input that will receive the coordinates from JS
    coords_input = st.text_input("Coordinates Payload", key="coords_payload", label_visibility="hidden")
    
    # Hidden button that will be clicked by the JS to trigger the Python script rerun
    # FIX: Removed the unsupported 'label_visibility' argument, which caused the TypeError.
    submit_button = st.form_submit_button("Submit Location Data", type="primary", use_container_width=True)
    
    # Pass the labels/keys as pseudo-IDs to the JS function
    hidden_input_id = "Coordinates Payload"
    hidden_submit_id = "Submit Location Data"
    

# 2. Inject the JS component to start the process
# We only inject the live map/JS on the initial run or if the user hasn't successfully processed location yet.
if 'coords_processed' not in st.session_state:
    st.session_state['coords_processed'] = False

if not st.session_state.coords_processed:
    st.info("Please grant location permission in your browser pop-up. The process is automatic.")
    inject_geolocation_js(hidden_input_id, hidden_submit_id)

# 3. Process the results when the hidden form submits
if submit_button and st.session_state.coords_payload:
    # Check if the payload is fresh (i.e., not an empty string or default value)
    if st.session_state.coords_payload and st.session_state.coords_payload != "Coordinates Payload":
        
        try:
            # Parse the coordinates string: "latitude,longitude"
            lat_str, lon_str = st.session_state.coords_payload.split(',')
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            
            # --- Python Backend Processing ---
            
            # 1. Save to JSON file
            save_coordinates(lat, lon)
            
            # 2. Reverse Geocode
            address = geocode_coordinates(lat, lon)
            
            # 3. Display success message
            st.success("✅ Location successfully detected and processed!")
            st.markdown(f"""
            ### Resolved Location:
            
            **Address:** **{address}**
            
            **Coordinates:** `{lat:.6f}, {lon:.6f}`
            
            *The coordinates have been automatically written to `{COORDS_FILE}`.*
            """)
            
            # Prevent re-injection of the JS map on subsequent page loads/reruns
            st.session_state.coords_processed = True 
            
        except ValueError:
            st.error("Invalid coordinate format received from browser. Something went wrong with the data transmission.")
        except Exception as e:
            st.error(f"An unexpected error occurred during Python processing: {e}")
            
    else:
        st.warning("Location data not yet received or access was denied.")

# 4. Display the currently saved location/address if available (for persistence)
st.markdown("---")
saved_coords = st.session_state.get('last_saved_coords', load_coordinates())

if saved_coords:
    st.subheader("Last Known Location (from `coords.json`)")
    
    saved_lat = saved_coords['latitude']
    saved_lon = saved_coords['longitude']
    
    # Display the static map using Streamlit's built-in map for simplicity
    st.map([{'latitude': saved_lat, 'longitude': saved_lon}])

    # Re-geocode the saved data for display
    # This ensures the address is shown even if the initial geocode failed or page refreshed
    saved_address = geocode_coordinates(saved_lat, saved_lon)
    
    st.markdown("### Details")
    st.code(json.dumps(saved_coords, indent=4), language="json")
    st.markdown(f"""
    **Coordinates:** `{saved_lat:.6f}, {saved_lon:.6f}`
    **Resolved Address:** **{saved_address}**
    
    *Data saved on: {time.ctime(saved_coords['timestamp'])}*
    """)
    
else:
    st.info("No previously saved location data found or detected yet.")

# Final CSS to hide the hidden form elements
st.markdown("""
<style>
    /* Targets the stForm element */
    [data-testid="stForm"] {
        display: none !important; 
    }
</style>
""", unsafe_allow_html=True)
