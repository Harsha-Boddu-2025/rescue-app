"""
Condition Agent - Analyzes animal condition from uploaded photo using Gemini
"""

import os
from google import genai
from google.genai import types
from pathlib import Path
import json

class ConditionAgent:
    """Analyzes animal condition from uploaded photo using Gemini"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = "gemini-3.6-flash"  # Exact model required
    
    def analyze(self, image_path: str, case_meta: dict) -> dict:
        """Analyze image to determine animal species, injury type, and severity"""
        
        if not self.client:
            print("❌ Condition Agent Error: GEMINI_API_KEY is not set.")
            return {
                "is_animal": False,
                "species": "Unknown",
                "injury_type": "Configuration Error",
                "severity": "High",
                "condition_notes": "GEMINI_API_KEY is not set in backend environment."
            }
        
        try:
            # Read image file bytes
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
            
            # Determine image type
            image_ext = Path(image_path).suffix.lower()
            media_type = "image/jpeg" if image_ext in ['.jpg', '.jpeg'] else "image/png"
            
            prompt = """You are an expert animal rescue coordinator analyzing emergency photos.

Analyze this photo and provide:
1. IS_ANIMAL: boolean (true if a live animal is clearly visible in the image, false if it is a car, landscape, object, or completely unrelated image).
2. SPECIES: Identify the type of animal (dog, cat, bird, reptile, wild animal, cattle, etc.). If no animal is present, state "None".
3. INJURY_TYPE: Describe the visible injury or condition (fracture, wound, poisoning, soft-tissue trauma, none visible, etc., or N/A if not an animal).
4. SEVERITY: Rate as Critical (immediate life threat), High (serious injury), Medium (moderate), Low (minor/healthy), or N/A (if not an animal).
5. CONDITION_NOTES: Brief description of the animal's condition and immediate needs, or explanation if no animal is detected.

Respond ONLY in valid JSON format with these exact keys:
{
    "is_animal": true,
    "species": "string",
    "injury_type": "string", 
    "severity": "string",
    "condition_notes": "string"
}"""
            
            # Call Gemini Vision API with JSON mime type configuration
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=media_type),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            response_text = response.text.strip()
            print(f"🔍 Raw Gemini Response: {response_text}")
            
            # Extract JSON from response safely
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                result = json.loads(clean_text)
            
            # Validate required keys
            required_keys = ['is_animal', 'species', 'injury_type', 'severity', 'condition_notes']
            for key in required_keys:
                if key not in result:
                    if key == 'is_animal':
                        result[key] = True
                    else:
                        result[key] = "Unknown"
            
            # Normalize severity
            severity_map = {
                'critical': 'Critical',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low',
                'n/a': 'N/A'
            }
            
            severity = str(result.get('severity', 'High')).lower()
            result['severity'] = severity_map.get(severity, 'High')
            
            print(f"✅ Condition Agent Success: Animal Detected={result['is_animal']}, Species={result['species']} - Severity={result['severity']}")
            return result
        
        except Exception as e:
            err_str = str(e)
            print(f"❌ Condition Agent Exception: {err_str}")
            
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                print("⚠️ Rate limit encountered. Utilizing mock rescue analysis data to proceed.")
                return {
                    "is_animal": True,
                    "species": "Dog",
                    "injury_type": "Laceration / Soft Tissue Trauma (Fallback)",
                    "severity": "High",
                    "condition_notes": "API quota limit reached; automated fallback data applied to test multi-agent dispatch and logging."
                }
                
            return {
                "is_animal": False,
                "species": "Unknown Animal",
                "injury_type": "Unable to analyze",
                "severity": "High",
                "condition_notes": f"Error during analysis: {err_str}"
            }
