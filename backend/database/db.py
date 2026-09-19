"""
Database module - Using in-memory storage for demo
For production, use PostgreSQL with the migration script
"""

import json
from datetime import datetime
import uuid
from typing import Dict, List, Optional

class Database:
    """In-memory database for demo purposes"""
    
    def __init__(self):
        self.cases = {}
        self.missions = {}
        self.agent_logs = {}
    
    def create_case(self, citizen_name: str, citizen_phone: str, citizen_email: str,
                   latitude: float, longitude: float, city: str,
                   street_address: str, photo_url: str) -> str:
        """Create a new case"""
        
        case_id = str(uuid.uuid4())[:8]
        
        case = {
            'case_id': case_id,
            'citizen_name': citizen_name,
            'citizen_phone': citizen_phone,
            'citizen_email': citizen_email,
            'latitude': latitude,
            'longitude': longitude,
            'city': city,
            'street_address': street_address,
            'photo_url': photo_url,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'analyzing',
            'agents': {
                'condition': {'status': 'pending', 'result': None},
                'priority': {'status': 'pending', 'result': None},
                'resource': {'status': 'pending', 'result': None},
                'coordinator': {'status': 'pending', 'result': None}
            }
        }
        
        self.cases[case_id] = case
        print(f"📝 Case created: {case_id}")
        
        return case_id
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """Get case by ID"""
        return self.cases.get(case_id)
    
    def get_active_cases(self) -> List[Dict]:
        """Get all active cases"""
        active = [case for case in self.cases.values()
                 if case['status'] not in ['closed', 'error']]
        return sorted(active, key=lambda x: x['created_at'], reverse=True)
    
    def update_case_status(self, case_id: str, status: str) -> bool:
        """Update case status"""
        
        if case_id in self.cases:
            self.cases[case_id]['status'] = status
            self.cases[case_id]['updated_at'] = datetime.utcnow().isoformat()
            print(f"✏️  Case {case_id} status updated to: {status}")
            return True
        
        return False
    
    def update_agent_status(self, case_id: str, agent_name: str,
                           agent_status: str, result: Dict) -> bool:
        """Update agent progress for a case"""
        
        if case_id in self.cases:
            self.cases[case_id]['agents'][agent_name] = {
                'status': agent_status,
                'result': result
            }
            
            # Update overall case status
            all_completed = all(
                agent['status'] == 'completed'
                for agent in self.cases[case_id]['agents'].values()
            )
            
            if all_completed and self.cases[case_id]['status'] == 'analyzing':
                self.cases[case_id]['status'] = 'ready_dispatch'
            
            # Log agent activity
            self._log_agent_activity(case_id, agent_name, agent_status, result)
            
            print(f"🤖 Agent {agent_name} completed for case {case_id}")
            return True
        
        return False
    
    def _log_agent_activity(self, case_id: str, agent_name: str,
                           status: str, result: Dict):
        """Log agent activity for audit trail"""
        
        log_id = f"{case_id}-{agent_name}-{datetime.utcnow().timestamp()}"
        
        self.agent_logs[log_id] = {
            'case_id': case_id,
            'agent_name': agent_name,
            'status': status,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def create_mission(self, case_id: str, volunteer_id: int,
                      vehicle_id: int, hospital_id: int) -> str:
        """Create a rescue mission"""
        
        mission_id = f"M-{case_id}"
        
        mission = {
            'mission_id': mission_id,
            'case_id': case_id,
            'volunteer_id': volunteer_id,
            'vehicle_id': vehicle_id,
            'hospital_id': hospital_id,
            'status': 'assigned',
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.missions[mission_id] = mission
        print(f"✅ Mission created: {mission_id}")
        
        return mission_id
    
    def find_nearest_volunteers(self, latitude: float, longitude: float,
                               radius: int = 15, limit: int = 5) -> List[Dict]:
        """Find nearest volunteers (mock)"""
        
        # This would call PostgreSQL in production
        return []
    
    def find_nearest_vehicles(self, latitude: float, longitude: float,
                             radius: int = 20, limit: int = 5) -> List[Dict]:
        """Find nearest vehicles (mock)"""
        
        # This would call PostgreSQL in production
        return []
    
    def find_nearest_hospitals(self, latitude: float, longitude: float,
                              animal_species: str, radius: int = 25,
                              limit: int = 5) -> List[Dict]:
        """Find nearest hospitals (mock)"""
        
        # This would call PostgreSQL in production
        return []
    
    def get_analytics(self) -> Dict:
        """Get system analytics"""
        
        total_cases = len(self.cases)
        completed_cases = sum(1 for case in self.cases.values()
                             if case['status'] == 'closed')
        
        return {
            'total_cases': total_cases,
            'completed_cases': completed_cases,
            'active_cases': total_cases - completed_cases,
            'timestamp': datetime.utcnow().isoformat()
        }
