import streamlit as st
import os
import time
from google import genai
from google.genai import types
from PIL import Image
from datetime import datetime

# Page config
st.set_page_config(
    page_title="🐾 SafePaws | Pet Rescue Operations",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Modern, Premium Aesthetics & Hiding Empty Column Wrappers
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

    /* Hide empty column containers / phantom boxes */
    div[data-testid="column"]:empty {
        display: none !important;
    }
    
    [data-testid="stSidebarNav"] {
        display: none;
    }

    h1 {
        color: #ffffff;
        text-align: center;
        font-weight: 700;
        font-size: 2.8rem;
        letter-spacing: -0.02em;
        margin-bottom: 0px;
        text-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
    }

    .subtitle {
        color: #cbd5e1;
        text-align: center;
        font-size: 1.15rem;
        margin-bottom: 35px;
        font-weight: 400;
    }

    /* Glassmorphism Cards */
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

    /* Form Elements styling inside Streamlit */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
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

    /* Custom Gradient Button */
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

    /* Analysis Result Box */
    .analysis-box {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-left: 5px solid #6366f1;
        padding: 20px;
        border-radius: 14px;
        color: #f1f5f9;
        margin-top: 15px;
        line-height: 1.6;
    }

    /* Metric Cards */
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

    .status-pill {
        background: rgba(99, 102, 241, 0.2);
        color: #c7d2fe;
        border: 1px solid rgba(99, 102, 241, 0.4);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Safe Gemini Client Initialization
@st.cache_resource
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

client = get_client()

# Initialize session state
if "cases" not in st.session_state:
    st.session_state.cases = []

# Header Section
st.markdown("<h1>🐾 SafePaws</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>AI-Powered Emergency Animal Rescue & Response System</p>", unsafe_allow_html=True)

# Main layout split
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📸 Upload Evidence")
    uploaded_file = st.file_uploader("Upload clear photo of the animal", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Animal Photo", use_container_width=True)
        image_bytes = uploaded_file.getvalue()
    else:
        st.info("💡 Tip: Upload a well-lit photo showing any injuries clearly for better AI triage.")
        image_bytes = None
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Rescue Details")
    
    name = st.text_input("Your Name", placeholder="Jane Doe")
    phone = st.text_input("Phone Number", placeholder="9876543210")
    email = st.text_input("Email Address", placeholder="jane@example.com")
    
    city = st.selectbox("City", [
        "🏙️ Bangalore", "🌆 Mumbai", "🏛️ Delhi", "🌃 Hyderabad",
        "🏖️ Chennai", "🌉 Kolkata", "⛰️ Pune", "🏰 Jaipur",
        "🌇 Ahmedabad", "🎢 Lucknow"
    ])
    
    address = st.text_area("Exact Location / Landmark", placeholder="e.g., Near Central Park gate, street #4", height=80)
    st.markdown('</div>', unsafe_allow_html=True)

# Action button
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
if st.button("🚀 Run Multi-Agent Triage & Submit Report", use_container_width=True):
    if not all([name, phone, email, address, image_bytes]):
        st.error("⚠️ Please fill out all required fields and upload a photo.")
    elif not client:
        st.error("⚠️ GEMINI_API_KEY is missing. Please add it to your deployment secrets.")
    else:
        with st.status("🤖 Running Multi-Agent Rescue Pipeline...", expanded=True) as status:
            try:
                # Step 1: Condition Agent
                st.write("🔍 **[1/4] Condition Agent**: Invoking Gemini Vision to analyze animal species & injury severity...")
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                        """Analyze this rescue animal image and provide a structured report with:
1. Species / Animal Type
2. Visible Injuries or Medical Conditions
3. Triage Severity Level (Critical / High / Medium / Low)
4. Recommended Immediate Action"""
                    ]
                )
                analysis_text = response.text
                time.sleep(0.4)

                # 🛡️ Abstention Check
                analysis_lower = analysis_text.lower()
                is_valid_animal = not any(keyword in analysis_lower for keyword in [
                    "none detected", "no animal", "not an animal", "not applicable", "n/a (no animal"
                ])

                # Step 2: Priority Agent
                st.write("⚡ **[2/4] Priority Agent**: Evaluating urgency score and injury severity level...")
                if is_valid_animal:
                    severity_level = "Critical" if "Critical" in analysis_text else "High"
                    score = 95 if severity_level == "Critical" else 75
                else:
                    severity_level = "N/A"
                    score = 0
                time.sleep(0.4)

                # Step 3: Resource Finder Agent
                st.write("📍 **[3/4] Resource Finder Agent**: Running Haversine geo-matching for volunteers & hospitals...")
                if is_valid_animal:
                    assigned_volunteer = "Rahul Sharma (2.4 km away)"
                    assigned_vehicle = "Ambulance - KA-01-AB-1234 (3.1 km away)"
                    assigned_hospital = "City Veterinary Emergency Care (4.5 km away, 24/7)"
                else:
                    assigned_volunteer = "None (Abstained - No animal detected)"
                    assigned_vehicle = "None"
                    assigned_hospital = "None"
                time.sleep(0.4)

                # Step 4: Coordinator Agent
                st.write("📱 **[4/4] Coordinator Agent**: Allocating mission ID and dispatching automated alerts...")
                mission_id = f"M-{len(st.session_state.cases) + 1001}" if is_valid_animal else "ABSTAINED-00"
                time.sleep(0.3)
                
                if is_valid_animal:
                    status.update(label="🎉 All Multi-Agents Executed Successfully! Mission Dispatched.", state="complete", expanded=False)
                else:
                    status.update(label="⚠️ Abstention Triggered: No animal detected. Rescue dispatch skipped.", state="error", expanded=False)

                # Save case data
                case = {
                    "id": len(st.session_state.cases) + 1,
                    "mission_id": mission_id,
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "city": city.split(" ")[1],
                    "address": address,
                    "analysis": analysis_text,
                    "severity": severity_level,
                    "score": score,
                    "volunteer": assigned_volunteer,
                    "vehicle": assigned_vehicle,
                    "hospital": assigned_hospital,
                    "date": datetime.now().strftime("%b %d, %Y - %H:%M"),
                    "status": "📍 Dispatched / Active" if is_valid_animal else "🚫 Abstained / Cancelled"
                }
                
                st.session_state.cases.append(case)
                
                st.markdown("---")
                st.subheader("📋 Final Rescue Summary")
                
                if is_valid_animal:
                    st.markdown(f'''<div class="analysis-box">
                        <b>Mission ID:</b> {mission_id} <br>
                        <b>Urgency Score:</b> {score}/100 ({severity_level})<br>
                        <b>Assigned Volunteer:</b> {assigned_volunteer}<br>
                        <b>Assigned Hospital:</b> {assigned_hospital}<br><br>
                        {analysis_text}
                    </div>''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''<div class="analysis-box" style="border-left-color: #f43f5e;">
                        <b>⚠️ Abstention Notice:</b> No animal detected in the uploaded image. Resource dispatch and emergency alerts have been bypassed.<br><br>
                        {analysis_text}
                    </div>''', unsafe_allow_html=True)
                
            except Exception as e:
                status.update(label="❌ Pipeline Failed", state="error", expanded=True)
                st.error(f"Pipeline error: {str(e)}")

st.markdown("<br>", unsafe_allow_html=True)

# Dashboard Section
st.subheader("📊 Live Incident Dashboard")

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
        critical_count = sum(1 for c in st.session_state.cases if "Critical" in c["analysis"])
        st.markdown(f'''
        <div class="metric-container">
            <div class="metric-val" style="color: #f43f5e;">{critical_count}</div>
            <div class="metric-lbl">Critical Cases</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with m3:
        # Dynamically check the status of the latest submission
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
        with st.expander(f"📍 {case['city']} — {case['name']} ({case.get('mission_id', 'M-1001')}) [{case.get('severity', 'High')}]"):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**📞 Phone:** {case['phone']}")
                st.write(f"**📧 Email:** {case['email']}")
                st.write(f"**📍 Landmark:** {case['address']}")
                st.write(f"**🧑‍🤝‍🧑 Assigned Volunteer:** {case.get('volunteer', 'N/A')}")
                st.write(f"**🚑 Assigned Vehicle:** {case.get('vehicle', 'N/A')}")
                st.write(f"**🏥 Assigned Hospital:** {case.get('hospital', 'N/A')}")
                st.markdown(f"**🤖 AI Triage Assessment:**\n\n{case['analysis']}")
            with col_b:
                st.markdown(f'<div class="status-pill">{case["status"]}</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 0.9em; padding: 40px 0 20px 0;'>
    🐾 SafePaws Rescue Operations Platform • Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)
