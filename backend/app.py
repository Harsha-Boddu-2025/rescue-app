"""
Flask backend API for Pet Rescue Operations
Handles case creation, agent orchestration, and resource matching
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
import requests
from functools import wraps
import threading

# Import agents
from agents.condition_agent import ConditionAgent
from agents.priority_agent import PriorityAgent
from agents.resource_finder_agent import ResourceFinderAgent
from agents.coordinator_agent import CoordinatorAgent

from database.db import Database

app = Flask(__name__)
CORS(app)

# Initialize database
db = Database()

# Initialize agents
condition_agent = ConditionAgent()
priority_agent = PriorityAgent()
resource_finder = ResourceFinderAgent()
coordinator = CoordinatorAgent()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    }), 200


@app.route('/api/cases/create', methods=['POST'])
def create_case():
    """
    Create a new rescue case from citizen report
    """
    try:
        # Validate request
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        photo = request.files['photo']
        
        if not allowed_file(photo.filename):
            return jsonify({'error': 'Invalid file format. Use JPG or PNG'}), 400
        
        # Extract form data
        citizen_name = request.form.get('citizen_name', '').strip()
        citizen_phone = request.form.get('citizen_phone', '').strip()
        citizen_email = request.form.get('citizen_email', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        city = request.form.get('city', '').strip()
        street_address = request.form.get('street_address', '').strip()
        
        # Validation
        if not all([citizen_name, citizen_phone, latitude, longitude, city, street_address]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return jsonify({'error': 'Invalid latitude/longitude'}), 400
        
        # Save photo
        filename = f"{uuid.uuid4()}.jpg"
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)
        
        # Create case in database
        case_id = db.create_case(
            citizen_name=citizen_name,
            citizen_phone=citizen_phone,
            citizen_email=citizen_email,
            latitude=latitude,
            longitude=longitude,
            city=city,
            street_address=street_address,
            photo_url=f'/uploads/{filename}'
        )
        
        # Initialize case object
        case = {
            'case_id': case_id,
            'citizen_name': citizen_name,
            'citizen_phone': citizen_phone,
            'citizen_email': citizen_email,
            'latitude': latitude,
            'longitude': longitude,
            'city': city,
            'street_address': street_address,
            'photo_url': f'/uploads/{filename}',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'status': 'analyzing',
            'agents': {
                'condition': {'status': 'pending', 'result': None},
                'priority': {'status': 'pending', 'result': None},
                'resource': {'status': 'pending', 'result': None},
                'coordinator': {'status': 'pending', 'result': None}
            }
        }
        
        # Start agent processing asynchronously
        thread = threading.Thread(
            target=process_case_agents,
            args=(case_id, case, photo_path)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify(case), 201
    
    except Exception as e:
        print(f"Error creating case: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cases/<case_id>', methods=['GET'])
def get_case(case_id):
    """Get case details with agent progress"""
    try:
        case = db.get_case(case_id)
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        return jsonify(case), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cases/active', methods=['GET'])
def get_active_cases():
    """Get all active cases"""
    try:
        cases = db.get_active_cases()
        return jsonify({'cases': cases}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cases/<case_id>/status', methods=['PUT'])
def update_case_status(case_id):
    """Update case status"""
    try:
        data = request.json
        status = data.get('status')
        db.update_case_status(case_id, status)
        return jsonify({'status': 'updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cases/<case_id>/agent-status', methods=['PUT'])
def update_agent_status(case_id):
    """Update agent progress for a case"""
    try:
        data = request.json
        agent_name = data.get('agent_name')
        agent_status = data.get('status')
        agent_result = data.get('result')
        
        db.update_agent_status(case_id, agent_name, agent_status, agent_result)
        return jsonify({'status': 'updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def process_case_agents(case_id, case, photo_path):
    """
    Process case through agent pipeline
    Runs in separate thread to avoid blocking
    """
    try:
        # Step 1: Condition Agent
        print(f"[Case {case_id}] Running Condition Agent...")
        condition_result = condition_agent.analyze(photo_path, case)
        db.update_agent_status(case_id, 'condition', 'completed', condition_result)
        case['agents']['condition'] = {'status': 'completed', 'result': condition_result}
        
        # Step 2: Priority Agent
        print(f"[Case {case_id}] Running Priority Agent...")
        priority_result = priority_agent.assess(condition_result)
        db.update_agent_status(case_id, 'priority', 'completed', priority_result)
        case['agents']['priority'] = {'status': 'completed', 'result': priority_result}
        
        # Step 3: Resource Finder Agent
        print(f"[Case {case_id}] Running Resource Finder Agent...")
        resource_result = resource_finder.match_resources(
            latitude=case['latitude'],
            longitude=case['longitude'],
            animal_species=condition_result.get('species'),
            injury_severity=condition_result.get('severity')
        )
        db.update_agent_status(case_id, 'resource', 'completed', resource_result)
        case['agents']['resource'] = {'status': 'completed', 'result': resource_result}
        
        # Step 4: Coordinator Agent
        print(f"[Case {case_id}] Running Coordinator Agent...")
        coordinator_result = coordinator.assign_mission(
            case_id=case_id,
            volunteer_id=resource_result.get('volunteer', {}).get('id'),
            vehicle_id=resource_result.get('vehicle', {}).get('id'),
            hospital_id=resource_result.get('hospital', {}).get('id'),
            case_data=case
        )
        db.update_agent_status(case_id, 'coordinator', 'completed', coordinator_result)
        case['agents']['coordinator'] = {'status': 'completed', 'result': coordinator_result}
        
        # Update case status
        db.update_case_status(case_id, 'assigned')
        case['status'] = 'assigned'
        
        print(f"[Case {case_id}] ✅ All agents completed successfully!")
        
    except Exception as e:
        print(f"[Case {case_id}] ❌ Error processing case: {str(e)}")
        db.update_case_status(case_id, 'error')


@app.route('/api/volunteers/nearest', methods=['POST'])
def get_nearest_volunteers():
    """Find nearest available volunteers"""
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 15)
        limit = data.get('limit', 5)
        
        volunteers = db.find_nearest_volunteers(latitude, longitude, radius, limit)
        return jsonify({'volunteers': volunteers}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/vehicles/nearest', methods=['POST'])
def get_nearest_vehicles():
    """Find nearest available vehicles"""
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 20)
        limit = data.get('limit', 5)
        
        vehicles = db.find_nearest_vehicles(latitude, longitude, radius, limit)
        return jsonify({'vehicles': vehicles}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hospitals/nearest', methods=['POST'])
def get_nearest_hospitals():
    """Find nearest veterinary hospitals"""
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        animal_species = data.get('species', 'dog')
        radius = data.get('radius', 25)
        limit = data.get('limit', 5)
        
        hospitals = db.find_nearest_hospitals(latitude, longitude, animal_species, radius, limit)
        return jsonify({'hospitals': hospitals}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get system analytics"""
    try:
        analytics = db.get_analytics()
        return jsonify(analytics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Pet Rescue API Server on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)

