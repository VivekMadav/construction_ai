"""
Test Carbon Analysis API
Simple test to verify carbon analysis endpoints are working.
"""

import requests
import json

def test_carbon_api():
    """Test carbon analysis API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Carbon Analysis API...")
    print("=" * 50)
    
    # Test project carbon analysis
    print("1. Testing project carbon analysis...")
    try:
        response = requests.get(f"{base_url}/api/v1/analysis/project/1/carbon")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total Carbon: {data.get('total_carbon_kg_co2e', 0):.2f} kg CO2e")
            print(f"Sustainability Score: {data.get('sustainability_score', 0):.1f}")
            print(f"Drawing Count: {data.get('drawing_count', 0)}")
            print(f"Element Count: {data.get('element_count', 0)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Testing drawing carbon analysis...")
    try:
        response = requests.get(f"{base_url}/api/v1/analysis/drawing/7/carbon")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total Carbon: {data.get('total_carbon_kg_co2e', 0):.2f} kg CO2e")
            print(f"Carbon Intensity: {data.get('carbon_intensity_kg_co2e_per_unit', 0):.3f}")
            print(f"Material Breakdown: {data.get('material_breakdown', {})}")
            print(f"Recommendations: {data.get('optimization_recommendations', [])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Testing available drawings...")
    try:
        response = requests.get(f"{base_url}/api/v1/drawings/project/1")
        if response.status_code == 200:
            drawings = response.json()
            print(f"Found {len(drawings)} drawings:")
            for drawing in drawings:
                if drawing.get('processing_status') == 'completed':
                    print(f"  - {drawing['filename']} (ID: {drawing['id']}, Elements: {len(drawing.get('elements', []))})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_carbon_api() 