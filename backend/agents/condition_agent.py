"""
Condition Agent - Uses Claude Vision to analyze animal condition from image
"""

import anthropic
import base64
from pathlib import Path
import json

class ConditionAgent:
    """Analyzes animal condition from uploaded photo"""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-3-5-sonnet-20241022"
    
    def analyze(self, image_path: str, case_data: dict) -> dict:
        """
        Analyze image to determine animal species, injury type, and severity
        
        Args:
            image_path: Path to uploaded image
            case_data: Case information
        
        Returns:
            dict: Analysis result with species, injury_type, severity
        """
        
        try:
            # Read and encode image
            with open(image_path, 'rb') as img_file:
                image_data = base64.standard_b64encode(img_file.read()).decode('utf-8')
            
            # Determine image type
            image_ext = Path(image_path).suffix.lower()
            media_type = "image/jpeg" if image_ext in ['.jpg', '.jpeg'] else "image/png"
            
            # Create prompt for Claude
            prompt = """You are an expert animal rescue coordinator analyzing emergency photos.

Analyze this photo and provide:
1. SPECIES: Identify the type of animal (dog, cat, bird, reptile, wild animal, etc.)
2. INJURY_TYPE: Describe the visible injury or condition (fracture, wound, poisoning, stuck, etc.)
3. SEVERITY: Rate as Critical (immediate life threat), High (serious injury), Medium (moderate), or Low (minor)
4. CONDITION_NOTES: Brief description of the animal's condition and immediate needs

Respond ONLY in valid JSON format with these exact keys:
{
    "species": "string",
    "injury_type": "string", 
    "severity": "string",
    "condition_notes": "string"
}"""
            
            # Call Claude Vision API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Extract JSON from response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, return mock data
                result = {
                    "species": "Unknown Animal",
                    "injury_type": "Requires immediate assessment",
                    "severity": "High",
                    "condition_notes": "Animal requires urgent veterinary care"
                }
            
            # Validate result
            required_keys = ['species', 'injury_type', 'severity', 'condition_notes']
            for key in required_keys:
                if key not in result:
                    result[key] = "Unknown"
            
            # Normalize severity
            severity_map = {
                'critical': 'Critical',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low'
            }
            
            severity = result.get('severity', 'High').lower()
            result['severity'] = severity_map.get(severity, 'High')
            
            print(f"✅ Condition Agent Result: {result['species']} - {result['severity']} severity")
            
            return result
        
        except Exception as e:
            print(f"❌ Condition Agent Error: {str(e)}")
            # Return default analysis on error
            return {
                "species": "Unknown Animal",
                "injury_type": "Unable to analyze",
                "severity": "High",
                "condition_notes": f"Error during analysis: {str(e)}"
            }
