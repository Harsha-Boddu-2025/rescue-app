import streamlit as st
import requests
import time
from datetime import datetime
import json

def show_cases_page():
    """Display all cases with agent progress"""
    
    st.markdown("""
        <h1 style="text-align: center; margin-bottom: 10px;">📋 Active Rescue Cases</h1>
        <p style="text-align: center; color: #666; font-size: 16px;">
            Track animal rescues and agent progress in real-time
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🔴 Live Cases", "✅ Completed", "📊 Analytics"])
    
    with tab1:
        show_live_cases()
    
    with tab2:
        show_completed_cases()
    
    with tab3:
        show_analytics()


def show_live_cases():
    """Show live/active cases"""
    
    try:
        API_URL = "http://localhost:8000"
        
        # Fetch cases
        response = requests.get(f"{API_URL}/api/cases/active", timeout=10)
        
        if response.status_code == 200:
            cases = response.json().get('cases', [])
            
            if not cases:
                st.info("✨ No active cases right now. Great job! 🎉")
                return
            
            # Display each case
            for case in cases:
                display_case_card(case)
        else:
            st.error("Could not fetch cases")
    
    except requests.exceptions.ConnectionError:
        show_mock_cases()
    except Exception as e:
        st.error(f"Error: {str(e)}")


def display_case_card(case):
    """Display a single case with agent progress"""
    
    case_id = case.get('case_id', 'Unknown')
    citizen_name = case.get('citizen_name', 'Unknown')
    animal_species = case.get('species', 'Unknown')
    status = case.get('status', 'analyzing')
    created_at = case.get('created_at', 'Unknown')
    photo_url = case.get('photo_url', '')
    
    # Determine status badge color
    status_colors = {
        'analyzing': 'status-analyzing',
        'assigned': 'status-assigned',
        'in_progress': 'status-in_progress',
        'completed': 'status-completed'
    }
    
    with st.container():
        st.markdown(f"""
            <div style="
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                border-left: 5px solid #ff8c42;
                box-shadow: 0 4px 6px rgba(255, 107, 53, 0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div>
                        <h3 style="margin: 0; color: #ff6b35;">Case #{case_id}</h3>
                        <p style="margin: 5px 0; color: #666; font-size: 14px;">{created_at}</p>
                    </div>
                    <div style="padding: 8px 16px; background: #d4edda; border-radius: 20px; color: #155724; font-weight: bold; font-size: 12px;">
                        ✅ {status.upper()}
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div>
                        <p style="margin: 5px 0; color: #666;"><strong>👤 Reporter:</strong> {citizen_name}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>🐾 Animal:</strong> {animal_species.title()}</p>
                    </div>
                    <div>
                        <p style="margin: 5px 0; color: #666;"><strong>📍 Status:</strong> {status.title()}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>⏱️ Duration:</strong> ~5 mins</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Agent progress section
        st.markdown("### 🤖 Agent Progress")
        
        agents = case.get('agents', {})
        
        # Create columns for each agent
        col1, col2, col3, col4 = st.columns(4)
        
        agent_info = [
            ('condition', '🔍', 'Condition', 'Analyzing animal condition...'),
            ('priority', '🚨', 'Priority', 'Assessing urgency level...'),
            ('resource', '🎯', 'Resources', 'Finding best team...'),
            ('coordinator', '👥', 'Assignment', 'Coordinating rescue...')
        ]
        
        for col, (agent_key, emoji, title, desc) in zip([col1, col2, col3, col4], agent_info):
            with col:
                agent = agents.get(agent_key, {})
                agent_status = agent.get('status', 'pending')
                agent_result = agent.get('result', {})
                
                # Status colors
                if agent_status == 'completed':
                    status_color = '#28a745'
                    bg_color = '#d4edda'
                    icon = '✅'
                elif agent_status == 'processing':
                    status_color = '#ffc107'
                    bg_color = '#fff3cd'
                    icon = '⏳'
                else:
                    status_color = '#ccc'
                    bg_color = '#f0f0f0'
                    icon = '⏸️'
                
                st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        border-left: 4px solid {status_color};
                        border-radius: 8px;
                        padding: 12px;
                        text-align: center;
                    ">
                        <div style="font-size: 24px; margin-bottom: 5px;">{emoji} {icon}</div>
                        <div style="font-weight: bold; color: {status_color}; margin-bottom: 5px;">{title}</div>
                        <div style="font-size: 12px; color: #666;">{desc}</div>
                        
                        {format_agent_result(agent_key, agent_result)}
                    </div>
                """, unsafe_allow_html=True)
        
        # Show matched resources if available
        if agents.get('resource', {}).get('status') == 'completed':
            st.markdown("### 🏆 Matched Resources")
            
            resource_result = agents.get('resource', {}).get('result', {})
            volunteer = resource_result.get('volunteer', {})
            vehicle = resource_result.get('vehicle', {})
            hospital = resource_result.get('hospital', {})
            match_score = resource_result.get('matching_score', 0)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
                        border: 2px solid #28a745;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: center;
                    ">
                        <div style="font-size: 28px; margin-bottom: 8px;">👤</div>
                        <p style="margin: 0; font-weight: bold; color: #155724;">{volunteer.get('name', 'N/A')}</p>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">📍 {volunteer.get('distance', 'N/A')}km away</p>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">📱 {volunteer.get('phone', 'N/A')}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e0f2f1 0%, #e8f5e9 100%);
                        border: 2px solid #17a2b8;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: center;
                    ">
                        <div style="font-size: 28px; margin-bottom: 8px;">🚑</div>
                        <p style="margin: 0; font-weight: bold; color: #0c5460;">{vehicle.get('registration', 'N/A')}</p>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">{vehicle.get('type', 'N/A').title()}</p>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">📍 {vehicle.get('distance', 'N/A')}km away</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
                        border: 2px solid #c2185b;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: center;
                    ">
                        <div style="font-size: 28px; margin-bottom: 8px;">🏥</div>
                        <p style="margin: 0; font-weight: bold; color: #880e4f;">{hospital.get('name', 'N/A')}</p>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">📍 {hospital.get('distance', 'N/A')}km away</p>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">🛏️ {hospital.get('available_beds', 'N/A')} beds available</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Match score
            st.markdown(f"""
                <div style="text-align: center; margin-top: 15px;">
                    <p style="font-size: 12px; color: #666;">OVERALL MATCH QUALITY</p>
                    <div style="font-size: 32px; font-weight: bold; color: #ff6b35;">{match_score}/100</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")


def format_agent_result(agent_key, result):
    """Format agent result for display"""
    
    if not result:
        return ""
    
    if agent_key == 'condition':
        species = result.get('species', 'Unknown')
        severity = result.get('severity', 'Unknown')
        return f"""
            <div style="font-size: 11px; color: #555; margin-top: 8px;">
                <p style="margin: 0;">🐾 {species}</p>
                <p style="margin: 2px 0;">⚠️ {severity}</p>
            </div>
        """
    
    elif agent_key == 'priority':
        priority = result.get('level', 'Unknown')
        return f"""
            <div style="font-size: 11px; color: #555; margin-top: 8px;">
                <p style="margin: 0;">Priority: {priority}</p>
            </div>
        """
    
    elif agent_key == 'coordinator':
        assigned = result.get('assigned', False)
        if assigned:
            return f"""
                <div style="font-size: 11px; color: #555; margin-top: 8px;">
                    <p style="margin: 0;">✅ Team dispatched</p>
                </div>
            """
    
    return ""


def show_completed_cases():
    """Show completed cases"""
    
    st.info("✅ No completed cases in the last 24 hours")
    
    # Mock data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Rescued", "247", "+12 this week")
    
    with col2:
        st.metric("⏱️ Avg Response", "8.5 min", "-1.2 min")
    
    with col3:
        st.metric("🎯 Success Rate", "94%", "+2%")


def show_analytics():
    """Show analytics dashboard"""
    
    st.markdown("### 📊 System Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🐾 Total Cases", "247", "+12")
    with col2:
        st.metric("👥 Active Volunteers", "30", "100% available")
    with col3:
        st.metric("🚑 Vehicles Ready", "30", "All operational")
    with col4:
        st.metric("🏥 Hospitals Active", "30", "Full capacity")
    
    st.markdown("---")
    
    # City-wise distribution
    st.markdown("### 🏙️ City-wise Cases")
    
    city_data = {
        "Bangalore": 45,
        "Mumbai": 38,
        "Delhi": 42,
        "Hyderabad": 35,
        "Kolkata": 28,
        "Chennai": 32,
        "Pune": 25,
        "Others": 22
    }
    
    col_labels = []
    col_values = []
    for city, count in city_data.items():
        col_labels.append(city)
        col_values.append(count)
    
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(12, 4))
    bars = ax.barh(col_labels, col_values, color='#ff8c42')
    ax.set_xlabel('Number of Cases', fontweight='bold')
    ax.set_title('Cases by City', fontweight='bold', fontsize=14, color='#ff6b35')
    ax.set_facecolor('#fff9e6')
    fig.patch.set_facecolor('#fff5e6')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, col_values)):
        ax.text(value + 1, i, str(value), va='center', fontweight='bold', color='#ff6b35')
    
    st.pyplot(fig, use_container_width=True)


def show_mock_cases():
    """Show mock cases when API is not available"""
    
    st.warning("📡 Running in demo mode (API not connected)")
    
    # Mock case 1
    case1 = {
        'case_id': '001',
        'citizen_name': 'Raj Kumar',
        'species': 'dog',
        'status': 'in_progress',
        'created_at': 'Today, 2:30 PM',
        'agents': {
            'condition': {'status': 'completed', 'result': {'species': 'Dog', 'severity': 'High'}},
            'priority': {'status': 'completed', 'result': {'level': 'Critical'}},
            'resource': {
                'status': 'completed',
                'result': {
                    'volunteer': {'name': 'Priya Singh', 'distance': 0.2, 'phone': '9876543211'},
                    'vehicle': {'registration': 'KA-09-AB-1234', 'type': 'ambulance', 'distance': 0.3},
                    'hospital': {'name': 'Bangalore Pet Hospital', 'distance': 1.5, 'available_beds': 5},
                    'matching_score': 94
                }
            },
            'coordinator': {'status': 'processing', 'result': {}}
        }
    }
    
    # Mock case 2
    case2 = {
        'case_id': '002',
        'citizen_name': 'Anjali Verma',
        'species': 'bird',
        'status': 'analyzing',
        'created_at': 'Today, 2:15 PM',
        'agents': {
            'condition': {'status': 'processing', 'result': {}},
            'priority': {'status': 'pending', 'result': {}},
            'resource': {'status': 'pending', 'result': {}},
            'coordinator': {'status': 'pending', 'result': {}}
        }
    }
    
    display_case_card(case1)
    display_case_card(case2)
