"""
Coordinator Agent - Assigns rescue missions and notifies team
"""

from datetime import datetime

class CoordinatorAgent:
    """Coordinates and assigns rescue missions"""
    
    def assign_mission(self, case_id: str, volunteer_id: int, vehicle_id: int,
                       hospital_id: int, case_data: dict) -> dict:
        """
        Create and assign a rescue mission
        
        Args:
            case_id: Case ID
            volunteer_id: Selected volunteer ID
            vehicle_id: Selected vehicle ID
            hospital_id: Selected hospital ID
            case_data: Full case data
        
        Returns:
            dict: Mission assignment details
        """
        
        try:
            # Create mission record
            mission = {
                'mission_id': f'M-{case_id}',
                'case_id': case_id,
                'volunteer_id': volunteer_id,
                'vehicle_id': vehicle_id,
                'hospital_id': hospital_id,
                'status': 'assigned',
                'assigned_at': datetime.utcnow().isoformat(),
                'notifications_sent': self._send_notifications(
                    case_id, volunteer_id, vehicle_id, hospital_id, case_data
                )
            }
            
            print(f"✅ Coordinator Result: Mission {mission['mission_id']} assigned")
            
            return mission
        
        except Exception as e:
            print(f"❌ Coordinator Error: {str(e)}")
            return {
                'mission_id': f'M-{case_id}',
                'status': 'failed',
                'error': str(e)
            }
    
    def _send_notifications(self, case_id: str, volunteer_id: int,
                           vehicle_id: int, hospital_id: int,
                           case_data: dict) -> list:
        """Send notifications to assigned resources"""
        
        notifications = []
        
        try:
            # Simulate sending SMS to volunteer
            notifications.append({
                'type': 'SMS',
                'recipient': 'volunteer',
                'phone': f"+91-{volunteer_id}xxx",
                'status': 'sent',
                'message': f"Rescue Case #{case_id}: Animal rescue needed at {case_data.get('street_address', 'location')}"
            })
            
            # Simulate sending SMS to hospital
            notifications.append({
                'type': 'SMS',
                'recipient': 'hospital',
                'phone': f"+91-{hospital_id}xxx",
                'status': 'sent',
                'message': f"Case #{case_id}: Incoming animal rescue. {case_data.get('species', 'animal')} with {case_data.get('injury_severity', 'injury')} condition. ETA: 15 mins"
            })
            
            # Log notification
            notifications.append({
                'type': 'LOG',
                'recipient': 'system',
                'status': 'logged',
                'message': f"Case #{case_id}: Mission created and team notified"
            })
            
            print(f"📱 Notifications sent for case {case_id}")
            
        except Exception as e:
            print(f"⚠️ Error sending notifications: {str(e)}")
        
        return notifications
    
    def get_mission_status(self, mission_id: str) -> dict:
        """Get current mission status"""
        
        # Mock mission status
        return {
            'mission_id': mission_id,
            'status': 'en_route',
            'volunteer_location': {'lat': 12.971, 'lng': 77.594},
            'estimated_arrival': '5 minutes',
            'vehicle_distance': '0.5 km'
        }
    
    def update_mission_status(self, mission_id: str, status: str,
                              location: dict = None) -> dict:
        """Update mission status during rescue operation"""
        
        return {
            'mission_id': mission_id,
            'status': status,
            'updated_at': datetime.utcnow().isoformat(),
            'location': location
        }
