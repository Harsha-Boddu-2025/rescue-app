"""
Resource Finder Agent - Matches volunteers, vehicles, and hospitals
"""

import math
import pandas as pd
from pathlib import Path

class ResourceFinderAgent:
    """Finds and matches best rescue resources"""
    
    def __init__(self):
        """Initialize with CSV data"""
        data_dir = Path(__file__).parent.parent.parent / 'data'
        
        self.volunteers_df = pd.read_csv(str(data_dir / 'volunteers.csv'))
        self.vehicles_df = pd.read_csv(str(data_dir / 'vehicles.csv'))
        self.hospitals_df = pd.read_csv(str(data_dir / 'hospitals.csv'))
    
    def match_resources(self, latitude: float, longitude: float,
                        animal_species: str, injury_severity: str) -> dict:
        """
        Match best volunteer, vehicle, and hospital for rescue
        
        Args:
            latitude: Case latitude
            longitude: Case longitude
            animal_species: Type of animal
            injury_severity: Severity level
        
        Returns:
            dict: Matched resources with scores
        """
        
        try:
            # 🛡️ Abstention Check: If no animal was detected, skip resource matching
            species_check = str(animal_species).lower()
            severity_check = str(injury_severity).lower()
            
            if "none detected" in species_check or "no animal" in species_check or severity_check == "n/a":
                print("⚠️ Resource Finder Abstained: No valid animal detected.")
                return {
                    'volunteer': None,
                    'vehicle': None,
                    'hospital': None,
                    'alternates': {
                        'volunteers': [],
                        'vehicles': [],
                        'hospitals': []
                    },
                    'matching_score': 0,
                    'reasoning': 'Abstained: No animal detected, resource dispatch skipped.'
                }

            # Find resources
            volunteers = self._find_volunteers(latitude, longitude)
            vehicles = self._find_vehicles(latitude, longitude)
            hospitals = self._find_hospitals(latitude, longitude, animal_species)
            
            # Get best matches
            best_volunteer = volunteers[0] if volunteers else None
            best_vehicle = vehicles[0] if vehicles else None
            best_hospital = hospitals[0] if hospitals else None
            
            # Calculate matching score
            matching_score = self._calculate_score(
                best_volunteer,
                best_vehicle,
                best_hospital
            )
            
            result = {
                'volunteer': best_volunteer,
                'vehicle': best_vehicle,
                'hospital': best_hospital,
                'alternates': {
                    'volunteers': volunteers[1:3] if len(volunteers) > 1 else [],
                    'vehicles': vehicles[1:3] if len(vehicles) > 1 else [],
                    'hospitals': hospitals[1:3] if len(hospitals) > 1 else []
                },
                'matching_score': matching_score
            }
            
            print(f"✅ Resource Finder Result: Score {matching_score}/100")
            
            return result
        
        except Exception as e:
            print(f"❌ Resource Finder Error: {str(e)}")
            return {
                'volunteer': None,
                'vehicle': None,
                'hospital': None,
                'matching_score': 0,
                'error': str(e)
            }
    
    def _calculate_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates (km)"""
        
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon / 2) ** 2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _find_volunteers(self, latitude: float, longitude: float,
                        max_distance: float = 15, limit: int = 3) -> list:
        """Find nearest available volunteers"""
        
        try:
            available = self.volunteers_df[
                self.volunteers_df['availability'].astype(str) == 'true'
            ].copy()
            
            # Calculate distances
            available['distance'] = available.apply(
                lambda row: self._calculate_distance(
                    latitude, longitude,
                    float(row['latitude']), float(row['longitude'])
                ), axis=1
            )
            
            # Filter by distance and sort
            available = available[available['distance'] <= max_distance]
            available = available.sort_values('distance')
            
            # Format results
            results = []
            for _, v in available.head(limit).iterrows():
                results.append({
                    'id': int(v['id']),
                    'name': str(v['name']),
                    'city': str(v['city']),
                    'phone': str(v['phone']),
                    'distance': round(float(v['distance']), 1),
                    'skills': str(v['skills']).split(';'),
                    'certifications': str(v['certifications'])
                })
            
            return results
        
        except Exception as e:
            print(f"Error finding volunteers: {str(e)}")
            return []
    
    def _find_vehicles(self, latitude: float, longitude: float,
                      max_distance: float = 20, limit: int = 3) -> list:
        """Find nearest available vehicles"""
        
        try:
            available = self.vehicles_df[
                self.vehicles_df['status'].astype(str) == 'available'
            ].copy()
            
            # Calculate distances
            available['distance'] = available.apply(
                lambda row: self._calculate_distance(
                    latitude, longitude,
                    float(row['latitude']), float(row['longitude'])
                ), axis=1
            )
            
            # Priority: ambulance > van > pickup
            type_priority = {'ambulance': 0, 'van': 1, 'pickup': 2}
            available['type_priority'] = available['type'].map(type_priority)
            
            # Filter and sort
            available = available[available['distance'] <= max_distance]
            available = available.sort_values(['type_priority', 'distance'])
            
            # Format results
            results = []
            for _, v in available.head(limit).iterrows():
                results.append({
                    'id': int(v['id']),
                    'registration': str(v['registration']),
                    'type': str(v['type']),
                    'city': str(v['city']),
                    'distance': round(float(v['distance']), 1),
                    'capacity': int(v['capacity']),
                    'equipment': str(v['equipment']).split(';')
                })
            
            return results
        
        except Exception as e:
            print(f"Error finding vehicles: {str(e)}")
            return []
    
    def _find_hospitals(self, latitude: float, longitude: float,
                       animal_species: str = 'dog',
                       max_distance: float = 25, limit: int = 3) -> list:
        """Find nearest veterinary hospitals"""
        
        try:
            # Filter hospitals with available beds
            available = self.hospitals_df[
                self.hospitals_df['available_beds'].astype(int) > 0
            ].copy()
            
            # Calculate distances
            available['distance'] = available.apply(
                lambda row: self._calculate_distance(
                    latitude, longitude,
                    float(row['latitude']), float(row['longitude'])
                ), axis=1
            )
            
            # Check for specialization
            available['has_specialization'] = available['specializations'].apply(
                lambda specs: animal_species.lower() in str(specs).lower()
            )
            
            # Emergency priority
            available['is_emergency'] = available['emergency_24h'].astype(str) == 'true'
            
            # Filter and sort
            available = available[available['distance'] <= max_distance]
            available = available.sort_values(
                by=['has_specialization', 'is_emergency', 'distance'],
                ascending=[False, False, True]
            )
            
            # Format results
            results = []
            for _, h in available.head(limit).iterrows():
                results.append({
                    'id': int(h['id']),
                    'name': str(h['name']),
                    'city': str(h['city']),
                    'phone': str(h['phone']),
                    'distance': round(float(h['distance']), 1),
                    'specializations': str(h['specializations']).split(';'),
                    'available_beds': int(h['available_beds']),
                    'emergency_24h': h['emergency_24h'].astype(str) == 'true',
                    'operation_hours': str(h['operation_hours'])
                })
            
            return results
        
        except Exception as e:
            print(f"Error finding hospitals: {str(e)}")
            return []
    
    def _calculate_score(self, volunteer, vehicle, hospital) -> int:
        """Calculate overall matching score"""
        
        if not (volunteer and vehicle and hospital):
            return 0
        
        # Component scores
        volunteer_score = 80  # Found suitable volunteer
        vehicle_score = 75    # Found suitable vehicle
        
        # Distance factor (max 60km for 0 points)
        avg_distance = (volunteer['distance'] + vehicle['distance'] + 
                       hospital['distance']) / 3
        distance_score = max(0, 100 - (avg_distance * 1.5))
        
        # Final score
        final_score = int((volunteer_score + vehicle_score + distance_score) / 3)
        
        return max(0, min(100, final_score))
