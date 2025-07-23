"""
Quick Carbon Analysis
Analyze carbon footprint directly from drawing data without backend restart.
"""

import requests
import json
from carbon_footprint import CarbonFootprintCalculator

def analyze_drawing_carbon_quick(drawing_id: int):
    """Quick carbon analysis for a specific drawing"""
    base_url = "http://localhost:8000"
    
    print(f"Quick Carbon Analysis for Drawing ID: {drawing_id}")
    print("=" * 60)
    
    # Get drawing data
    try:
        response = requests.get(f"{base_url}/api/v1/drawings/project/1")
        if response.status_code != 200:
            print("Error getting drawings data")
            return
        
        drawings = response.json()
        drawing = None
        for d in drawings:
            if d['id'] == drawing_id:
                drawing = d
                break
        
        if not drawing:
            print(f"Drawing ID {drawing_id} not found")
            return
        
        print(f"Drawing: {drawing['filename']}")
        print(f"Discipline: {drawing['discipline']}")
        print(f"Elements: {len(drawing.get('elements', []))}")
        print()
        
        if not drawing.get('elements'):
            print("No elements found in drawing")
            return
        
        # Initialize carbon calculator
        calculator = CarbonFootprintCalculator()
        
        # Convert elements to carbon analysis format
        elements_for_carbon = []
        total_area = 0
        
        for element in drawing['elements']:
            element_type = element.get('element_type', 'unknown')
            area = element.get('area', 0)
            total_area += area
            
            # Assign material based on element type
            material = assign_material_to_element(element_type)
            
            # Convert area to weight for carbon calculation
            density_kg_per_m2 = get_material_density(material)
            quantity = area * density_kg_per_m2
            
            carbon_element = {
                'type': element_type,
                'material': material,
                'quantity': quantity,
                'unit': 'kg',
                'specifications': ['standard'],
                'transportation': 'regional',
                'confidence': element.get('confidence_score', 0.5)
            }
            elements_for_carbon.append(carbon_element)
            
            print(f"  {element_type}: {area:.2f} m² → {material} ({quantity:.1f} kg)")
        
        print(f"\nTotal Area: {total_area:.2f} m²")
        
        # Perform carbon analysis
        carbon_analysis = calculator.analyze_carbon_footprint(elements_for_carbon, 'commercial')
        
        if carbon_analysis:
            print(f"\n🌍 CARBON FOOTPRINT RESULTS")
            print("=" * 40)
            print(f"Total Carbon: {carbon_analysis.total_carbon:.2f} kg CO2e")
            print(f"Carbon Intensity: {carbon_analysis.carbon_intensity:.3f} kg CO2e per unit")
            print(f"Sustainability Score: {carbon_analysis.sustainability_score:.1f}")
            
            print(f"\n📊 Material Breakdown:")
            for material, carbon in carbon_analysis.material_breakdown.items():
                print(f"  {material}: {carbon:.2f} kg CO2e")
            
            print(f"\n💡 Optimization Recommendations:")
            for i, rec in enumerate(carbon_analysis.optimization_recommendations, 1):
                print(f"  {i}. {rec}")
            
            print(f"\n✅ Compliance Status:")
            for standard, compliant in carbon_analysis.compliance_status.items():
                status = "✅" if compliant else "❌"
                print(f"  {status} {standard.replace('_', ' ').title()}: {compliant}")
            
            # Environmental equivalents
            total_carbon = carbon_analysis.total_carbon
            trees_planted = total_carbon / 22
            car_miles = total_carbon * 2.3
            flight_hours = total_carbon / 90
            
            print(f"\n🌱 Environmental Equivalents:")
            print(f"  Equivalent to planting {trees_planted:.1f} trees")
            print(f"  Equivalent to driving {car_miles:.1f} miles")
            print(f"  Equivalent to {flight_hours:.1f} hours of commercial flight")
            
        else:
            print("Carbon analysis failed")
            
    except Exception as e:
        print(f"Error: {e}")

def assign_material_to_element(element_type: str) -> str:
    """Assign default material based on element type"""
    material_mapping = {
        'beam': 'steel',
        'column': 'concrete',
        'slab': 'concrete',
        'foundation': 'concrete',
        'wall': 'concrete',
        'floor': 'concrete',
        'roof': 'concrete',
        'room': 'concrete',
        'door': 'wood',
        'window': 'glass',
        'partition': 'gypsum',
        'road': 'asphalt',
        'utility': 'concrete',
        'hvac_duct': 'steel',
        'electrical_panel': 'steel',
        'unknown': 'concrete',
        'element': 'concrete'
    }
    return material_mapping.get(element_type.lower(), 'concrete')

def get_material_density(material: str) -> float:
    """Get material density in kg per m²"""
    density_mapping = {
        'concrete': 480.0,  # kg/m² (2400 kg/m³ * 0.2m thickness)
        'steel': 78.5,      # kg/m² (7850 kg/m³ * 0.01m thickness)
        'wood': 30.0,       # kg/m² (600 kg/m³ * 0.05m thickness)
        'glass': 25.0,      # kg/m² (2500 kg/m³ * 0.01m thickness)
        'gypsum': 24.0,     # kg/m² (1200 kg/m³ * 0.02m thickness)
        'asphalt': 230.0,   # kg/m² (2300 kg/m³ * 0.1m thickness)
        'brick': 360.0,     # kg/m² (1800 kg/m³ * 0.2m thickness)
        'stone': 540.0,     # kg/m² (2700 kg/m³ * 0.2m thickness)
        'tile': 40.0,       # kg/m² (2000 kg/m³ * 0.02m thickness)
        'plastic': 12.0,    # kg/m² (1200 kg/m³ * 0.01m thickness)
        'aluminum': 27.0,   # kg/m² (2700 kg/m³ * 0.01m thickness)
        'copper': 89.6,     # kg/m² (8960 kg/m³ * 0.01m thickness)
        'zinc': 71.4,       # kg/m² (7140 kg/m³ * 0.01m thickness)
        'lead': 113.4,      # kg/m² (11340 kg/m³ * 0.01m thickness)
        'tin': 73.1,        # kg/m² (7310 kg/m³ * 0.01m thickness)
        'fiberglass': 90.0, # kg/m² (1800 kg/m³ * 0.05m thickness)
        'mineral_wool': 10.0, # kg/m² (100 kg/m³ * 0.1m thickness)
        'cellulose': 5.0,   # kg/m² (50 kg/m³ * 0.1m thickness)
        'spray_foam': 3.0,  # kg/m² (30 kg/m³ * 0.1m thickness)
        'paint': 1.2,       # kg/m² (1200 kg/m³ * 0.001m thickness)
        'carpet': 20.0,     # kg/m² (2000 kg/m³ * 0.01m thickness)
        'precast': 480.0,   # kg/m² (2400 kg/m³ * 0.2m thickness)
        'cast_in_place': 480.0, # kg/m² (2400 kg/m³ * 0.2m thickness)
        'modular': 480.0,   # kg/m² (2400 kg/m³ * 0.2m thickness)
        'prefabricated': 480.0, # kg/m² (2400 kg/m³ * 0.2m thickness)
        'default': 480.0    # kg/m² (2400 kg/m³ * 0.2m thickness)
    }
    return density_mapping.get(material, 480.0)

def list_available_drawings():
    """List all available drawings"""
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/api/v1/drawings/project/1")
        if response.status_code == 200:
            drawings = response.json()
            print("Available Drawings:")
            print("=" * 30)
            for drawing in drawings:
                if drawing.get('processing_status') == 'completed':
                    print(f"ID: {drawing['id']} - {drawing['filename']}")
                    print(f"  Discipline: {drawing['discipline']}")
                    print(f"  Elements: {len(drawing.get('elements', []))}")
                    print()
        else:
            print("Error getting drawings")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Quick Carbon Analysis Tool")
    print("=" * 30)
    
    # List available drawings
    list_available_drawings()
    
    # Analyze the most recent drawing (ID 10)
    print("Analyzing most recent drawing (ID 10)...")
    analyze_drawing_carbon_quick(10)
    
    print("\nTo analyze other drawings, run:")
    print("analyze_drawing_carbon_quick(drawing_id)") 