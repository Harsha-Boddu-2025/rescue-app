"""
Priority Agent - Assesses case urgency and priority level
"""

class PriorityAgent:
    """Determines priority level based on condition analysis"""
    
    def assess(self, condition_result: dict) -> dict:
        """
        Assess priority based on animal condition
        
        Args:
            condition_result: Output from Condition Agent
        
        Returns:
            dict: Priority assessment
        """
        
        try:
            severity = condition_result.get('severity', 'High').lower()
            species = condition_result.get('species', '').lower()
            injury_type = condition_result.get('injury_type', '').lower()
            
            # Priority scoring logic
            priority_score = 50  # Base score
            priority_level = "Medium"
            
            # Severity assessment
            if 'critical' in severity:
                priority_score = 95
                priority_level = "Critical"
            elif 'high' in severity:
                priority_score = 75
                priority_level = "High"
            elif 'low' in severity:
                priority_score = 25
                priority_level = "Low"
            
            # Species-specific adjustments
            if any(x in species for x in ['infant', 'baby', 'puppy', 'kitten', 'endangered']):
                priority_score = min(100, priority_score + 10)
            
            # Injury-specific adjustments
            urgent_keywords = [
                'poisoning', 'choking', 'bleeding', 'unconscious',
                'severe injury', 'hit by vehicle', 'electrocution', 'fire'
            ]
            
            if any(keyword in injury_type for keyword in urgent_keywords):
                priority_score = min(100, priority_score + 15)
                priority_level = "Critical"
            
            # Determine final level
            if priority_score >= 80:
                priority_level = "Critical"
            elif priority_score >= 60:
                priority_level = "High"
            elif priority_score >= 40:
                priority_level = "Medium"
            else:
                priority_level = "Low"
            
            result = {
                'priority_level': priority_level,
                'priority_score': priority_score,
                'reasoning': generate_reasoning(
                    priority_level,
                    severity,
                    species,
                    injury_type
                )
            }
            
            print(f"✅ Priority Agent Result: {priority_level} (Score: {priority_score}/100)")
            
            return result
        
        except Exception as e:
            print(f"❌ Priority Agent Error: {str(e)}")
            return {
                'priority_level': 'High',
                'priority_score': 75,
                'reasoning': f'Default priority assigned due to: {str(e)}'
            }


def generate_reasoning(priority_level: str, severity: str, species: str, injury_type: str) -> str:
    """Generate reasoning explanation for priority assessment"""
    
    reasoning = f"Priority assessed as {priority_level} based on: "
    
    factors = []
    
    if 'critical' in severity:
        factors.append(f"Critical condition ({severity})")
    elif 'high' in severity:
        factors.append(f"High severity injury ({severity})")
    
    if any(x in species for x in ['infant', 'baby', 'puppy', 'endangered']):
        factors.append(f"Vulnerable/young {species}")
    
    if any(x in injury_type.lower() for x in ['bleeding', 'poisoning', 'choking']):
        factors.append(f"Life-threatening injury: {injury_type}")
    
    reasoning += ", ".join(factors) if factors else "Medical assessment"
    reasoning += ". Immediate rescue team dispatch recommended."
    
    return reasoning
