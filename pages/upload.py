import streamlit as st
import requests
import io
from PIL import Image
from datetime import datetime
import json

def show_upload_page():
    """Main upload page for citizen reports"""
    
    st.markdown("""
        <h1 style="text-align: center; margin-bottom: 10px;">🐾 Report an Animal in Need</h1>
        <p style="text-align: center; color: #666; font-size: 16px;">
            Help us rescue animals quickly. Upload a photo and your details.
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create two columns
    col1, col2 = st.columns([1, 1], gap="large")
    
    # Left column - Image upload
    with col1:
        st.markdown("### 📸 Step 1: Upload Photo")
        st.markdown("Take a clear photo of the animal that needs help")
        
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=['jpg', 'jpeg', 'png'],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            # Display image
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True, caption="Uploaded photo")
            
            # Show image info
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"📷 Size: {image.width}x{image.height}px")
            with col_b:
                st.info(f"📁 File: {uploaded_file.name}")
        else:
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #fff9e6 0%, #fff3d9 100%);
                    border: 2px dashed #ff8c42;
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    color: #999;
                ">
                    <div style="font-size: 40px; margin-bottom: 10px;">📷</div>
                    <p>Drag and drop an image or click to upload</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Right column - Form
    with col2:
        st.markdown("### 👤 Step 2: Your Details")
        
        # Form
        form = st.form("citizen_report_form")
        
        with form:
            # Name
            citizen_name = st.text_input(
                "Your Name",
                placeholder="John Doe",
                help="Your full name"
            )
            
            # Phone
            citizen_phone = st.text_input(
                "Phone Number",
                placeholder="+91 98765 43210",
                help="We'll use this to contact you about the rescue"
            )
            
            # Email (optional)
            citizen_email = st.text_input(
                "Email (Optional)",
                placeholder="john@example.com"
            )
            
            # Location
            st.markdown("**📍 Location Details**")
            col_lat, col_lon = st.columns(2)
            
            with col_lat:
                latitude = st.text_input(
                    "Latitude",
                    placeholder="12.9716",
                    help="Your location's latitude"
                )
            
            with col_lon:
                longitude = st.text_input(
                    "Longitude",
                    placeholder="77.5946",
                    help="Your location's longitude"
                )
            
            # City
            city = st.selectbox(
                "Nearest City",
                ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Kolkata", 
                 "Chennai", "Pune", "Jaipur", "Ahmedabad", "Lucknow"],
                help="Select the nearest major city"
            )
            
            # Street address
            street_address = st.text_area(
                "Street Address / Landmarks",
                placeholder="Near Central Park, Market Street",
                height=60,
                help="Describe the exact location or landmarks"
            )
            
            submit_button = form.form_submit_button(
                "✅ Create Case & Start Rescue",
                use_container_width=True
            )
    
    # Process form submission
    if submit_button:
        # Validation
        errors = []
        
        if not citizen_name:
            errors.append("Please enter your name")
        if not citizen_phone:
            errors.append("Please enter your phone number")
        if not uploaded_file:
            errors.append("Please upload an animal photo")
        if not latitude or not longitude:
            errors.append("Please enter location coordinates")
        if not street_address:
            errors.append("Please describe the location")
        
        if errors:
            st.error("❌ Please fix these errors:")
            for error in errors:
                st.write(f"• {error}")
        else:
            # Create case
            create_case(
                citizen_name=citizen_name,
                citizen_phone=citizen_phone,
                citizen_email=citizen_email,
                latitude=float(latitude),
                longitude=float(longitude),
                city=city,
                street_address=street_address,
                photo_file=uploaded_file
            )


def create_case(citizen_name, citizen_phone, citizen_email, latitude, longitude, city, street_address, photo_file):
    """Submit case to backend API"""
    
    try:
        # Show loading state
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        with progress_placeholder.container():
            st.info("🚀 Creating case and submitting to rescue team...")
        
        # Prepare form data
        files = {
            'photo': (photo_file.name, photo_file, 'image/jpeg')
        }
        
        data = {
            'citizen_name': citizen_name,
            'citizen_phone': citizen_phone,
            'citizen_email': citizen_email,
            'latitude': latitude,
            'longitude': longitude,
            'city': city,
            'street_address': street_address,
        }
        
        # Send to backend API
        API_URL = "http://localhost:8000"  # Configure in .env
        
        response = requests.post(
            f"{API_URL}/api/cases/create",
            data=data,
            files=files,
            timeout=30
        )
        
        if response.status_code == 201:
            case_result = response.json()
            case_id = case_result.get('case_id')
            
            # Clear loading state
            progress_placeholder.empty()
            
            # Show success
            with status_placeholder.container():
                st.markdown("""
                    <div class="success-msg">
                        <div style="font-size: 24px; margin-bottom: 10px;">✅ Case Created Successfully!</div>
                        <p style="margin: 10px 0;">
                            <strong>Case ID:</strong> #<span style="font-size: 18px; color: #28a745;">{}</span>
                        </p>
                        <p style="margin: 10px 0;">
                            Our rescue team is already analyzing the situation and finding the best resources.
                        </p>
                    </div>
                """.format(case_id), unsafe_allow_html=True)
            
            st.balloons()
            
            # Store case data in session
            st.session_state.case_data = case_result
            st.session_state.selected_case_id = case_id
            
            # Show next steps
            st.markdown("### 📋 What happens next?")
            
            col1, col2, col3, col4 = st.columns(4)
            
            steps = [
                ("🔍", "Condition Analysis", "We analyze the animal's condition"),
                ("🚨", "Priority Assessment", "Determine urgency level"),
                ("🎯", "Resource Matching", "Find best volunteer & vehicle"),
                ("👥", "Team Dispatch", "Send rescue team to location")
            ]
            
            for i, (emoji, title, desc) in enumerate(steps):
                with [col1, col2, col3, col4][i]:
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #fff9e6 0%, #fff3d9 100%);
                            border: 2px solid #ff8c42;
                            border-radius: 10px;
                            padding: 15px;
                            text-align: center;
                        ">
                            <div style="font-size: 28px; margin-bottom: 8px;">{emoji}</div>
                            <div style="font-weight: bold; color: #ff6b35; font-size: 14px;">{title}</div>
                            <div style="color: #666; font-size: 12px; margin-top: 5px;">{desc}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Redirect button
            st.markdown("---")
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("📊 View Case Status", use_container_width=True, key="view_case"):
                    st.session_state.current_page = 'cases'
                    st.rerun()
        
        else:
            st.error(f"❌ Error creating case: {response.text}")
    
    except requests.exceptions.ConnectionError:
        st.error("""
            ⚠️ **Connection Error**: Cannot reach the rescue server.
            
            Make sure the backend API is running:
            ```bash
            python backend/app.py
            ```
        """)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
