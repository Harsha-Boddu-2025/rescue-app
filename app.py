import streamlit as st
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="🐾 Pet Rescue Operations",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "### 🐾 Pet Rescue Operations\nAI-powered animal rescue system"
    }
)

# Custom CSS for pet-friendly theme
st.markdown("""
    <style>
        /* Main background */
        .main {
            background: linear-gradient(135deg, #fff5e6 0%, #ffe8d6 100%);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ff8c42 0%, #ff6b35 100%);
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: white;
        }
        
        /* Headers */
        h1 {
            color: #ff6b35 !important;
            font-family: 'Comic Sans MS', 'Arial Rounded MT Bold' !important;
        }
        
        h2 {
            color: #ff8c42 !important;
            font-family: 'Comic Sans MS', 'Arial Rounded MT Bold' !important;
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            border: 3px solid #ff8c42;
            box-shadow: 0 4px 6px rgba(255, 107, 53, 0.1);
            margin: 10px 0;
        }
        
        .card-header {
            color: #ff6b35;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
            transition: transform 0.2s !important;
        }
        
        .stButton > button:hover {
            transform: scale(1.05) !important;
        }
        
        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            margin: 5px;
        }
        
        .status-analyzing {
            background-color: #fff3cd;
            color: #856404;
            border: 2px solid #ffc107;
        }
        
        .status-assigned {
            background-color: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
        }
        
        .status-completed {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 2px solid #17a2b8;
        }
        
        /* Agent cards */
        .agent-card {
            background: linear-gradient(135deg, #fff9e6 0%, #fff3d9 100%);
            border-left: 5px solid #ff8c42;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }
        
        .agent-card.active {
            border-left-color: #28a745;
            background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        }
        
        .agent-card.completed {
            border-left-color: #17a2b8;
            background: linear-gradient(135deg, #e0f2f1 0%, #e8f5e9 100%);
        }
        
        /* Success message */
        .success-msg {
            background-color: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        /* Warning message */
        .warning-msg {
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        /* Info message */
        .info-msg {
            background-color: #d1ecf1;
            border: 2px solid #17a2b8;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'upload'

if 'case_data' not in st.session_state:
    st.session_state.case_data = None

if 'agent_status' not in st.session_state:
    st.session_state.agent_status = {
        'condition': {'status': 'pending', 'result': None},
        'priority': {'status': 'pending', 'result': None},
        'resource': {'status': 'pending', 'result': None},
        'coordinator': {'status': 'pending', 'result': None}
    }

# Sidebar navigation
with st.sidebar:
    st.markdown("## 🐾 Navigation")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Upload", use_container_width=True, key="nav_upload"):
            st.session_state.current_page = 'upload'
            st.rerun()
    
    with col2:
        if st.button("📋 Cases", use_container_width=True, key="nav_cases"):
            st.session_state.current_page = 'cases'
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🐾 Cases", "12", "+2", delta_color="off")
    with col2:
        st.metric("✅ Completed", "8", "+1", delta_color="off")
    
    st.markdown("---")
    st.markdown("### 🏙️ Cities Active")
    cities = ["🌆 Bangalore", "🏙️ Mumbai", "🌃 Delhi", "🌉 Hyderabad"]
    for city in cities:
        st.write(f"• {city}")
    
    st.markdown("---")
    st.write("Built with 🐾 for animal rescue")

# Main content
if st.session_state.current_page == 'upload':
    # Import the upload page
    from pages.upload import show_upload_page
    show_upload_page()
else:
    # Import the cases page
    from pages.cases import show_cases_page
    show_cases_page()
