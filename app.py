import sys
from pathlib import Path
import pandas as pd
import pydeck as pdk
import requests

# Force Python to look inside the 'backend' folder first for package imports
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import streamlit as st
import os
import time
from google import genai
from google.genai import types
from PIL import Image
from datetime import datetime

# Import backend agents safely
try:
    from agents.condition_agent import ConditionAgent
    from agents.priority_agent import PriorityAgent
    from agents.resource_finder_agent import ResourceFinderAgent
    from agents.coordinator_agent import CoordinatorAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    AGENTS_AVAILABLE = False
    IMPORT_ERROR_MSG = str(e)

# Page config with no icon
st.set_page_config(
    page_title="Safe Havens | NGO Rescue Operations",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Modern, Premium Aesthetics & High Contrast Readability
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top left, #1e1b4b, #311042, #0f172a);
        background-attachment: fixed;
        min-height: 100vh;
    }

    div[data-testid="column"]:empty,
    .glass-card:empty {
        display: none !important;
    }
    
    [data-testid="stSidebarNav"] {
        display: none;
    }

    h1 {
        color: #f8fafc !important;
        text-align: center;
        font-weight: 700;
        font-size: 3rem;
        letter-spacing: -0.02em;
        margin-bottom: 0px;
        text-shadow: 0 4px 25px rgba(129, 140, 248, 0.6);
    }

    h2, h3, .stMarkdown h3, [data-testid="stSubheader"] {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }

    .subtitle {
        color: #cbd5e1;
        text-align: center;
        font-size: 1.15rem;
        margin-bottom: 35px;
        font-weight: 400;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }

    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stTimeInput input {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2) !important;
    }

    label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        font-size: 1.05rem;
        font-weight: 600;
        border-radius: 14px;
        width: 100%;
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(99, 102, 241, 0.6);
    }

    .analysis-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-left: 5px solid #6366f1;
        padding: 20px;
        border-radius: 14px;
        color: #f1f5f9;
        margin-top: 15px;
        line-height: 1.6;
    }

    .metric-container {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #818cf8;
    }

    .metric-lbl {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 5px;
    }

    @keyframes pulse-glow {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    .live-pulse {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        animation: pulse-glow 2s infinite;
        margin-right: 6px;
        vertical-align: middle;
    }

    .status-pill {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }

    div[data-testid="stExpanderDetails"], 
    div[data-testid="stExpanderDetails"] p, 
    div[data-testid="stExpanderDetails"] span, 
    div[data-testid="stExpanderDetails"] div {
        color: #f1f5f9 !important;
    }

    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 10px;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    div[data-testid="stStatusWidget"],
    div[data-testid="stStatusWidget"] div,
    div[data-testid="stStatusWidget"] span {
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Granular Sub-Locations Database with Exact Coordinates
CITY_SUBLOCATIONS = {
    "Bangalore": {
        "Indiranagar / MG Road": {"lat": 12.9716, "lng": 77.5946},
        "Koramangala Zone": {"lat": 12.9352, "lng": 77.6245},
        "Whitefield Tech Corridor": {"lat": 12.9689, "lng": 77.5906}
    },
    "Hyderabad": {
        "Banjara Hills / Jubilee Hills": {"lat": 17.4348, "lng": 78.4011},
        "Gachibowli / HITECH City": {"lat": 17.4475, "lng": 78.3614},
        "Kachiguda / Secunderabad": {"lat": 17.3992, "lng": 78.4876}
    },
    "Rajahmundry": {
        "Kotipally Bus Stand Area": {"lat": 17.0096, "lng": 81.7743},
        "Danavaipeta Zone": {"lat": 17.2344, "lng": 81.8112},
        "Rythu Bazaar Outskirt": {"lat": 17.0102, "lng": 81.8002}
    },
    "Visakhapatnam": {
        "RK Beach Road": {"lat": 17.7050, "lng": 83.3000},
        "MVP Colony": {"lat": 17.7425, "lng": 83.3124},
        "Madhurawada Tech Zone": {"lat": 17.8380, "lng": 83.3500}
    },
    "Kolkata": {
        "Park Street Zone": {"lat": 22.5222, "lng": 88.3486},
        "Salt Lake Sector V": {"lat": 22.5074, "lng": 88.3611},
        "Jadavpur University Area": {"lat": 22.4963, "lng": 88.3142}
    },
    "Vizianagaram": {
        "Fort Area Central": {"lat": 18.1180, "lng": 83.4000},
        "RTC Complex Zone": {"lat": 18.1280, "lng": 83.4100},
        "By-pass Junction": {"lat": 18.1050, "lng": 83.4150}
    }
}

# Google Sheet Sync Helper with your updated Web App URL targeting specific tab gid
def sync_to_google_sheet(case_data):
    web_app_url = "https://script.google.com/macros/s/AKfycbznTlJCMXt6JkuXyHbKMIcKDOYRpLIxDgIEdAY-s0ZAdRBJ0nbGJYCA_7qchB-BqPr8/exec"
    try:
        response = requests.post(web_app_url, json=case_data, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# Initialize Agents safely
@st.cache_resource
def init_agents():
    if AGENTS_AVAILABLE:
        try:
            return ConditionAgent(), PriorityAgent(), ResourceFinderAgent(), CoordinatorAgent()
        except Exception as e:
            st.error(f"❌ Agent Initialization Exception: {str(e)}")
            return None, None, None, None
    else:
        st.error(f"❌ Import Error: {locals().get('IMPORT_ERROR_MSG', 'Modules not found')}")
    return None, None, None, None

condition_agent, priority_agent, resource_finder, coordinator_agent = init_agents()

# Initialize session state
if "cases" not in st.session_state:
    st.session_state.cases = []

# Header Section
st.markdown("<h1>🏡 Safe Havens</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>AI-Powered NGO Emergency Animal Rescue & Sanctuary Coordination Platform</p>", unsafe_allow_html=True)

# Main layout split
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📸 Upload Evidence")
    uploaded_file = st.file_uploader("Upload clear photo of the animal", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Animal Photo", use_container_width=True)
        os.makedirs("uploads", exist_ok=True)
        temp_img_path = os.path.join("uploads", uploaded_file.name)
        with open(temp_img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    else:
        st.info("💡 Tip: Upload a well-lit photo showing any injuries clearly for better AI triage.")
        temp_img_path = None
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Rescue Details")
    
    name = st.text_input("Your Name", placeholder="Jane Doe")
    phone = st.text_input("Phone Number", placeholder="9876543210")
    email = st.text_input("Email Address", placeholder="jane@example.com")
    
    selected_city_display = st.selectbox("NGO Hub City", [
        "🏙️ Bangalore", "🏙️ Hyderabad", "🌊 Rajahmundry", "⚓ Visakhapatnam", 
        "🌉 Kolkata", "🏰 Vizianagaram"
    ])
    city_name = selected_city_display.split(" ")[1]
    
    available_sublocs = list(CITY_SUBLOCATIONS.get(city_name, {}).keys())
    selected_subloc = st.selectbox("Sub-Location / Area", available_sublocs)
    
    custom_landmark = st.text_input("Custom Landmark / Street (Optional)", placeholder="e.g., Near Pillar #42")
    incident_time = st.time_input("Incident Time", value=datetime.now().time())
    
    address = f"{custom_landmark}, {selected_subloc}" if custom_landmark else selected_subloc
    st.markdown('</div>', unsafe_allow_html=True)

# Action button
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
if st.button("🚀 Run Multi-Agent Triage & Submit Report", use_container_width=True):
    if not all([name, phone, email, temp_img_path]):
        st.error("⚠️ Please fill out all required fields and upload a photo.")
    elif not os.getenv("GEMINI_API_KEY"):
        st.error("⚠️ GEMINI_API_KEY is missing. Please add it to your environment secrets.")
    elif not AGENTS_AVAILABLE:
        st.error(f"⚠️ Backend agent modules could not be imported: {locals().get('IMPORT_ERROR_MSG', 'Unknown error')}")
    elif not condition_agent:
        st.error("⚠️ Condition Agent failed to initialize. Check backend initializers.")
    else:
        with st.status("🤖 Running Multi-Agent Rescue Pipeline...", expanded=True) as status:
            try:
                case_id = f"C-{len(st.session_state.cases) + 1}"
                case_meta = {
                    'city': city_name, 
                    'street_address': address,
                    'incident_time': incident_time.strftime("%H:%M")
                }

                # Step 1: Condition Agent
                st.write("🔍 **[1/4] Condition Agent**: Analyzing animal species & injury via Gemini Vision...")
                condition_result = condition_agent.analyze(temp_img_path, case_meta)
                time.sleep(0.3)

                # Abstention check
                species = condition_result.get('species', '').lower()
                injury = condition_result.get('injury_type', '').lower()
                is_valid_animal = not any(kw in species or kw in injury for kw in ["none", "not an animal", "n/a", "unknown animal"])

                # Step 2: Priority Agent
                st.write("⚡ **[2/4] Priority Agent**: Evaluating urgency score and injury severity level...")
                priority_result = priority_agent.assess(condition_result)
                severity_level = priority_result.get('priority_level', 'High')
                score = priority_result.get('priority_score', 75)
                time.sleep(0.3)

                # Step 3: Resource Finder Agent
                st.write(f"📍 **[3/4] Resource Finder Agent**: Querying local resources for {incident_time.strftime('%I:%M %p')} dispatch...")
                subloc_coords = CITY_SUBLOCATIONS.get(city_name, {}).get(selected_subloc, {"lat": 12.9716, "lng": 77.5946})
                
                if is_valid_animal and severity_level != "N/A":
                    resource_result = resource_finder.match_resources(
                        latitude=subloc_coords["lat"],
                        longitude=subloc_coords["lng"],
                        animal_species=condition_result.get('species', 'dog'),
                        injury_severity=severity_level
                    )
                else:
                    resource_result = {'volunteer': None, 'vehicle': None, 'hospital': None}
                time.sleep(0.3)

                # Step 4: Coordinator Agent
                st.write("📱 **[4/4] Coordinator Agent**: Generating mission ID and dispatching automated alerts...")
                vol_id = resource_result.get('volunteer', {}).get('id') if resource_result.get('volunteer') else 101
                veh_id = resource_result.get('vehicle', {}).get('id') if resource_result.get('vehicle') else 201
                hosp_id = resource_result.get('hospital', {}).get('id') if resource_result.get('hospital') else 301

                if is_valid_animal and severity_level != "N/A":
                    coordinator_result = coordinator_agent.assign_mission(
                        case_id=case_id,
                        volunteer_id=vol_id,
                        vehicle_id=veh_id,
                        hospital_id=hosp_id,
                        case_data=case_meta
                    )
                    mission_id = coordinator_result.get('mission_id', f"M-{case_id}")
                    status.update(label="🎉 Multi-Agents Executed Successfully! Mission Dispatched.", state="complete", expanded=False)
                else:
                    mission_id = "ABSTAINED-00"
                    status.update(label="⚠️ Abstention Triggered: No animal detected. Rescue dispatch skipped.", state="error", expanded=False)

                v_data = resource_result.get('volunteer')
                veh_data = resource_result.get('vehicle')
                h_data = resource_result.get('hospital')

                assigned_volunteer = f"{v_data['name']} ({v_data['distance']} km away, Ph: {v_data['phone']})" if v_data else "None"
                assigned_vehicle = f"{veh_data.get('type', 'Ambulance')} - Reg: {veh_data['registration']} ({veh_data['distance']} km away)" if veh_data else "None"
                assigned_hospital = f"{h_data['name']} ({h_data['effective_distance']} km away, Beds: {h_data['available_beds']})" if h_data else "None"

                hosp_lat = h_data.get('latitude', subloc_coords['lat'] + 0.05) if h_data else subloc_coords['lat'] + 0.05
                hosp_lng = h_data.get('longitude', subloc_coords['lng'] + 0.05) if h_data else subloc_coords['lng'] + 0.05

                case = {
                    "id": len(st.session_state.cases) + 1,
                    "mission_id": mission_id,
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "city": city_name,
                    "subloc": selected_subloc,
                    "address": address,
                    "time": incident_time.strftime("%I:%M %p"),
                    "lat": subloc_coords["lat"],
                    "lng": subloc_coords["lng"],
                    "hosp_lat": hosp_lat,
                    "hosp_lng": hosp_lng,
                    "analysis": f"**Species:** {condition_result.get('species')}\n\n**Injury:** {condition_result.get('injury_type')}\n\n**Notes:** {condition_result.get('condition_notes')}",
                    "severity": severity_level,
                    "score": score,
                    "volunteer": assigned_volunteer,
                    "vehicle": assigned_vehicle,
                    "hospital": assigned_hospital,
                    "date": datetime.now().strftime("%b %d, %Y"),
                    "status": "Dispatched / Active" if (is_valid_animal and severity_level != "N/A") else "Abstained / Cancelled"
                }
                
                st.session_state.cases.append(case)
                sync_to_google_sheet(case)
                
                st.markdown("---")
                st.subheader("📋 Final Rescue Summary")
                
                if is_valid_animal and severity_level != "N/A":
                    st.markdown(f'''<div class="analysis-box">
                        <b>Mission ID:</b> {mission_id} <br>
                        <b>Incident Time:</b> {case["time"]} <br>
                        <b>Urgency Score:</b> {score}/100 ({severity_level})<br>
                        <b>Assigned Volunteer:</b> {assigned_volunteer}<br>
                        <b>Assigned Vehicle:</b> {assigned_vehicle}<br>
                        <b>Assigned Hospital Partner:</b> {assigned_hospital}<br><br>
                        {case["analysis"]}
                    </div>''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''<div class="analysis-box" style="border-left-color: #f43f5e;">
                        <b>⚠️ Abstention Notice:</b> No animal detected in the uploaded image. Resource dispatch and emergency alerts have been bypassed.<br><br>
                        {case["analysis"]}
                    </div>''', unsafe_allow_html=True)
                
            except Exception as e:
                status.update(label="❌ Pipeline Failed", state="error", expanded=True)
                st.error(f"Pipeline error: {str(e)}")

st.markdown("<br>", unsafe_allow_html=True)

# Dashboard Section
st.subheader("📊 Live NGO Incident Dashboard")

if not st.session_state.cases:
    st.info("📭 No reports logged in this session yet. Submit one above to test the dashboard!")
else:
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f'''
        <div class="metric-container">
            <div class="metric-val">{len(st.session_state.cases)}</div>
            <div class="metric-lbl">Total Reports</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with m2:
        critical_count = sum(1 for c in st.session_state.cases if c["severity"] in ["Critical", "High"])
        st.markdown(f'''
        <div class="metric-container">
            <div class="metric-val" style="color: #f43f5e;">{critical_count}</div>
            <div class="metric-lbl">Critical / High Cases</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with m3:
        latest_case = st.session_state.cases[-1] if st.session_state.cases else None
        is_active_mission = latest_case and "Dispatched" in latest_case["status"]
        
        status_label = "Active" if is_active_mission else "Standby"
        status_color = "#10b981" if is_active_mission else "#f59e0b"
        
        st.markdown(f'''
        <div class="metric-container">
            <div class="metric-val" style="color: {status_color};">{status_label}</div>
            <div class="metric-lbl">Operations Status</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    for case in reversed(st.session_state.cases):
        with st.expander(f"📍 {case['city']} ({case['subloc']}) — {case['name']} ({case.get('mission_id', 'M-1001')}) [{case.get('severity', 'High')}]"):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**⏰ Incident Time:** {case.get('time', 'N/A')}")
                st.write(f"**📞 Phone:** {case['phone']}")
                st.write(f"**📧 Email:** {case['email']}")
                st.write(f"**📍 Landmark / Area:** {case['address']}")
                st.write(f"**🧑‍🤝‍🧑 Assigned Volunteer:** {case.get('volunteer', 'N/A')}")
                st.write(f"**🚑 Assigned Vehicle:** {case.get('vehicle', 'N/A')}")
                st.write(f"**🏥 Assigned Hospital Partner:** {case.get('hospital', 'N/A')}")
                st.markdown(f"**🤖 AI Triage Assessment:**\n\n{case['analysis']}")
            with col_b:
                st.markdown(f'''
                    <div class="status-pill">
                        <span class="live-pulse"></span>{case["status"]}
                    </div>
                ''', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"**🗺️ Live Dispatch Route ({case['subloc']} ➔ Hospital Partner):**")
            
            line_df = pd.DataFrame({
                'start_lat': [case['lat']],
                'start_lon': [case['lng']],
                'end_lat': [case['hosp_lat']],
                'end_lon': [case['hosp_lng']]
            })
            
            points_df = pd.DataFrame({
                'lat': [case['lat'], case['hosp_lat']],
                'lon': [case['lng'], case['hosp_lng']],
                'color': [[244, 63, 94], [129, 140, 248]],
                'name': ['Incident Sub-Location', 'Assigned Hospital']
            })

            layer_line = pdk.Layer(
                "LineLayer",
                line_df,
                get_source_position="[start_lon, start_lat]",
                get_target_position="[end_lon, end_lat]",
                get_color=[129, 140, 248, 220],
                get_width=5,
            )

            layer_points = pdk.Layer(
                "ScatterplotLayer",
                points_df,
                get_position="[lon, lat]",
                get_color="color",
                get_radius=400,
                pickable=True,
            )

            view_state = pdk.ViewState(
                latitude=case['lat'],
                longitude=case['lng'],
                zoom=12,
                pitch=20,
            )

            st.pydeck_chart(pdk.Deck(layers=[layer_line, layer_points], initial_view_state=view_state, tooltip={"text": "{name}"}))

# Footer
st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 0.9em; padding: 40px 0 20px 0;'>
    🏡 Safe Havens NGO Rescue Network • Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)
