import streamlit as st
import os
from anthropic import Anthropic
import base64
from PIL import Image
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="🐾 Pet Rescue",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 20px;
    }
    
    .stContainer {
        max-width: 600px;
    }
    
    h1 {
        color: white;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .subtitle {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    
    .upload-box {
        background: white;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    
    .result-box {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin-top: 20px;
    }
    
    .case-card {
        background: white;
        border-left: 5px solid #667eea;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .status-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9em;
        margin-top: 10px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        font-size: 1.1em;
        border-radius: 10px;
        width: 100%;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
    }
    
    .input-field {
        background: #f8f9ff;
        border: 1px solid #e0e0ff;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    .analysis-result {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .metric-number {
        font-size: 2em;
        color: #667eea;
        font-weight: bold;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Get API client
@st.cache_resource
def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY not found in Streamlit Secrets!")
        st.stop()
    return Anthropic(api_key=api_key)

client = get_client()

# Initialize session state
if "cases" not in st.session_state:
    st.session_state.cases = []

# Header
st.markdown("<h1>🐾 Pet Rescue</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Help animals in need with AI-powered analysis</p>", unsafe_allow_html=True)

# Main container
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.subheader("📤 Report Rescue")
    
    # Upload photo
    uploaded_file = st.file_uploader("Choose animal photo", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your photo", use_column_width=True)
        image_bytes = uploaded_file.getvalue()
    else:
        st.info("📸 Upload an animal photo to get started")
        image_bytes = None
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.subheader("📋 Details")
    
    name = st.text_input("Your Name", placeholder="Enter your name")
    phone = st.text_input("Phone Number", placeholder="9876543210")
    email = st.text_input("Email", placeholder="your@email.com")
    city = st.selectbox("City", [
        "🏙️ Bangalore",
        "🌆 Mumbai", 
        "🏛️ Delhi",
        "🌃 Hyderabad",
        "🏖️ Chennai",
        "🌉 Kolkata",
        "⛰️ Pune",
        "🏰 Jaipur",
        "🌇 Ahmedabad",
        "🎢 Lucknow"
    ])
    
    address = st.text_area("Location Details", placeholder="Where did you find the animal?", height=80)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Submit button
if st.button("🚀 Analyze Animal", use_container_width=True):
    if not all([name, phone, email, address, image_bytes]):
        st.error("❌ Please fill all fields and upload a photo!")
    else:
        with st.spinner("🔍 Analyzing animal... This may take a moment"):
            try:
                # Encode image
                base64_image = base64.standard_b64encode(image_bytes).decode("utf-8")
                
                # Call Claude Vision
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": base64_image,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": """Analyze this animal and provide:
1. Species/Animal Type
2. Visible Injuries or Conditions
3. Severity (Critical/High/Medium/Low)
4. Recommended Action

Be concise and clear."""
                                }
                            ],
                        }
                    ],
                )
                
                analysis_text = message.content[0].text
                
                # Save case
                case = {
                    "id": len(st.session_state.cases) + 1,
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "city": city.split(" ")[1],  # Remove emoji
                    "address": address,
                    "analysis": analysis_text,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "📍 Reported"
                }
                
                st.session_state.cases.append(case)
                
                # Show result
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.success("✅ Report submitted successfully!")
                st.subheader("🤖 AI Analysis")
                st.markdown(f'<div class="analysis-result">{analysis_text}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Divider
st.divider()

# Cases section
st.subheader("📊 All Reports")

if not st.session_state.cases:
    st.info("📭 No rescue reports yet. Submit one to get started!")
else:
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-number">{len(st.session_state.cases)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Reports</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        critical = sum(1 for c in st.session_state.cases if "Critical" in c["analysis"])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-number" style="color: #ff6b6b;">{critical}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Critical Cases</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-number" style="color: #51cf66;">✅</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Active</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Cases list
    for case in reversed(st.session_state.cases):
        with st.expander(f"📍 {case['name']} - {case['city']} ({case['date']})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Phone:** {case['phone']}")
                st.write(f"**Email:** {case['email']}")
                st.write(f"**Location:** {case['address']}")
                st.markdown(f"**Analysis:**\n\n{case['analysis']}")
            
            with col2:
                st.markdown(f'<div class="status-badge">{case["status"]}</div>', unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em; padding: 20px;'>
    🐾 Pet Rescue Operations | Powered by Claude AI
    <br>
    <span style='font-size: 0.85em;'>Helping animals in need</span>
</div>
""", unsafe_allow_html=True)
