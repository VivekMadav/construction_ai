"""
Carbon Footprint Analysis System
Calculates environmental impact of construction projects based on detected elements.
"""

import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CarbonResult:
    """Carbon footprint calculation result"""
    element_type: str
    material: str
    quantity: float
    unit: str
    carbon_factor: float
    total_carbon: float
    carbon_intensity: float
    specification_impact: float
    transportation_impact: float
    confidence: float

@dataclass
class CarbonAnalysis:
    """Comprehensive carbon analysis result"""
    total_carbon: float
    carbon_intensity: float
    material_breakdown: Dict[str, float]
    high_impact_elements: List[Dict]
    optimization_recommendations: List[str]
    compliance_status: Dict[str, bool]
    carbon_savings_potential: float
    sustainability_score: float
    report_timestamp: str

class CarbonFootprintCalculator:
    """Carbon footprint calculation engine"""
    
    def __init__(self):
        """Initialize carbon footprint calculator with comprehensive database"""
        self.carbon_factors = self._initialize_carbon_factors()
        self.specification_multipliers = self._initialize_specification_multipliers()
        self.transportation_factors = self._initialize_transportation_factors()
        self.benchmarks = self._initialize_benchmarks()
        
    def _initialize_carbon_factors(self) -> Dict[str, float]:
        """Initialize comprehensive carbon emission factors (kg CO2e per kg)"""
        return {
            # Concrete & Masonry
            'concrete': 0.15,
            'steel': 2.0,
            'aluminum': 8.1,
            'wood': -0.9,  # Carbon sequestration
            'glass': 0.85,
            'plastic': 2.7,
            'brick': 0.24,
            'stone': 0.08,
            'tile': 0.45,
            'asphalt': 0.12,
            
            # Metals
            'copper': 2.5,
            'zinc': 3.5,
            'lead': 1.8,
            'tin': 4.2,
            
            # Insulation & Finishes
            'fiberglass': 1.2,
            'mineral_wool': 0.8,
            'cellulose': -0.3,
            'spray_foam': 3.1,
            'gypsum': 0.12,
            'paint': 2.4,
            'carpet': 3.2,
            
            # Construction Methods
            'precast': 0.12,
            'cast_in_place': 0.18,
            'modular': 0.10,
            'prefabricated': 0.11,
            
            # Default fallback
            'default': 1.0
        }
    
    def _initialize_specification_multipliers(self) -> Dict[str, float]:
        """Initialize specification impact multipliers"""
        return {
            'high_strength': 1.2,
            'low_carbon': 0.8,
            'recycled': 0.6,
            'sustainable': 0.7,
            'premium': 1.3,
            'standard': 1.0,
            'eco_friendly': 0.75,
            'rapid_set': 1.1,
            'fiber_reinforced': 1.15,
            'lightweight': 0.9,
            'fire_rated': 1.25,
            'sound_absorbing': 1.1,
            'waterproof': 1.2,
            'thermal_insulation': 1.05,
            'structural': 1.1,
            'decorative': 0.95
        }
    
    def _initialize_transportation_factors(self) -> Dict[str, float]:
        """Initialize transportation carbon factors (kg CO2e per kg per km)"""
        return {
            'local': 0.05,      # <50 km
            'regional': 0.08,   # 50-200 km
            'national': 0.12,   # 200-1000 km
            'international': 0.15,  # >1000 km
            'default': 0.08
        }
    
    def _initialize_benchmarks(self) -> Dict[str, float]:
        """Initialize carbon intensity benchmarks (kg CO2e per m²)"""
        return {
            'residential': 800,      # kg CO2e per m²
            'commercial': 1200,      # kg CO2e per m²
            'industrial': 1500,      # kg CO2e per m²
            'infrastructure': 2000,  # kg CO2e per m²
            'low_carbon': 600,       # kg CO2e per m²
            'sustainable': 400,      # kg CO2e per m²
            'passive_house': 200     # kg CO2e per m²
        }
    
    def calculate_element_carbon(self, element: Dict) -> CarbonResult:
        """Calculate carbon footprint for a single element"""
        try:
            element_type = element.get('type', 'unknown')
            material = element.get('material', 'default')
            quantity = element.get('quantity', 0)
            unit = element.get('unit', 'kg')
            specifications = element.get('specifications', [])
            transportation = element.get('transportation', 'default')
            confidence = element.get('confidence', 0.5)
            
            # Get carbon factor
            carbon_factor = self.carbon_factors.get(material, self.carbon_factors['default'])
            
            # Calculate specification impact
            spec_multiplier = 1.0
            for spec in specifications:
                spec_multiplier *= self.specification_multipliers.get(spec, 1.0)
            
            # Calculate transportation impact
            transport_factor = self.transportation_factors.get(transportation, self.transportation_factors['default'])
            transport_distance = element.get('transport_distance', 100)  # Default 100 km
            transportation_impact = transport_factor * transport_distance
            
            # Calculate total carbon
            total_carbon = quantity * carbon_factor * spec_multiplier + transportation_impact
            
            # Calculate carbon intensity (carbon per unit)
            carbon_intensity = total_carbon / quantity if quantity > 0 else 0
            
            return CarbonResult(
                element_type=element_type,
                material=material,
                quantity=quantity,
                unit=unit,
                carbon_factor=carbon_factor,
                total_carbon=total_carbon,
                carbon_intensity=carbon_intensity,
                specification_impact=spec_multiplier,
                transportation_impact=transportation_impact,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error calculating carbon for element: {e}")
            return None
    
    def analyze_carbon_footprint(self, elements: List[Dict], project_type: str = 'commercial') -> CarbonAnalysis:
        """Perform comprehensive carbon footprint analysis"""
        try:
            carbon_results = []
            total_carbon = 0
            material_breakdown = {}
            high_impact_elements = []
            
            # Calculate carbon for each element
            for element in elements:
                result = self.calculate_element_carbon(element)
                if result:
                    carbon_results.append(result)
                    total_carbon += result.total_carbon
                    
                    # Track material breakdown
                    if result.material not in material_breakdown:
                        material_breakdown[result.material] = 0
                    material_breakdown[result.material] += result.total_carbon
                    
                    # Identify high impact elements (>100 kg CO2e)
                    if result.total_carbon > 100:
                        high_impact_elements.append({
                            'element_type': result.element_type,
                            'material': result.material,
                            'carbon_impact': result.total_carbon,
                            'carbon_intensity': result.carbon_intensity
                        })
            
            # Calculate carbon intensity
            total_quantity = sum(result.quantity for result in carbon_results if result.quantity > 0)
            carbon_intensity = total_carbon / total_quantity if total_quantity > 0 else 0
            
            # Generate optimization recommendations
            recommendations = self._generate_recommendations(carbon_results, total_carbon, project_type)
            
            # Check compliance
            compliance_status = self._check_compliance(total_carbon, carbon_intensity, project_type)
            
            # Calculate carbon savings potential
            carbon_savings_potential = self._calculate_savings_potential(carbon_results, project_type)
            
            # Calculate sustainability score
            sustainability_score = self._calculate_sustainability_score(carbon_results, project_type)
            
            return CarbonAnalysis(
                total_carbon=total_carbon,
                carbon_intensity=carbon_intensity,
                material_breakdown=material_breakdown,
                high_impact_elements=high_impact_elements,
                optimization_recommendations=recommendations,
                compliance_status=compliance_status,
                carbon_savings_potential=carbon_savings_potential,
                sustainability_score=sustainability_score,
                report_timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in carbon footprint analysis: {e}")
            return None
    
    def _generate_recommendations(self, carbon_results: List[CarbonResult], total_carbon: float, project_type: str) -> List[str]:
        """Generate carbon optimization recommendations"""
        recommendations = []
        
        # Analyze high carbon materials
        high_carbon_materials = [r for r in carbon_results if r.carbon_factor > 2.0]
        if high_carbon_materials:
            materials = list(set(r.material for r in high_carbon_materials))
            recommendations.append(f"Consider alternatives to high-carbon materials: {', '.join(materials)}")
        
        # Check for optimization opportunities
        if total_carbon > self.benchmarks.get(project_type, 1000):
            recommendations.append(f"Project carbon footprint exceeds {project_type} benchmark - consider optimization")
        
        # Suggest low-carbon alternatives
        if any(r.material == 'concrete' for r in carbon_results):
            recommendations.append("Consider low-carbon concrete alternatives")
        
        if any(r.material == 'steel' for r in carbon_results):
            recommendations.append("Consider recycled steel or alternative materials")
        
        # Transportation optimization
        high_transport = [r for r in carbon_results if r.transportation_impact > 50]
        if high_transport:
            recommendations.append("Consider local sourcing to reduce transportation emissions")
        
        # Specification optimization
        high_spec_impact = [r for r in carbon_results if r.specification_impact > 1.2]
        if high_spec_impact:
            recommendations.append("Review specifications for carbon reduction opportunities")
        
        if not recommendations:
            recommendations.append("Project shows good carbon performance - maintain current approach")
        
        return recommendations
    
    def _check_compliance(self, total_carbon: float, carbon_intensity: float, project_type: str) -> Dict[str, bool]:
        """Check environmental compliance status"""
        benchmark = self.benchmarks.get(project_type, 1000)
        
        return {
            'within_benchmark': total_carbon <= benchmark,
            'low_carbon_compliant': total_carbon <= self.benchmarks['low_carbon'],
            'sustainable_compliant': total_carbon <= self.benchmarks['sustainable'],
            'passive_house_compliant': total_carbon <= self.benchmarks['passive_house'],
            'intensity_acceptable': carbon_intensity <= 2.0
        }
    
    def _calculate_savings_potential(self, carbon_results: List[CarbonResult], project_type: str) -> float:
        """Calculate potential carbon savings"""
        current_total = sum(r.total_carbon for r in carbon_results)
        benchmark = self.benchmarks.get(project_type, 1000)
        
        # Calculate savings from material optimization
        material_savings = 0
        for result in carbon_results:
            if result.carbon_factor > 2.0:  # High carbon materials
                material_savings += result.total_carbon * 0.3  # 30% potential savings
        
        # Calculate savings from specification optimization
        spec_savings = 0
        for result in carbon_results:
            if result.specification_impact > 1.1:
                spec_savings += result.total_carbon * 0.2  # 20% potential savings
        
        total_savings = material_savings + spec_savings
        return min(total_savings, current_total - benchmark)
    
    def _calculate_sustainability_score(self, carbon_results: List[CarbonResult], project_type: str) -> float:
        """Calculate overall sustainability score (0-100)"""
        if not carbon_results:
            return 0
        
        total_carbon = sum(r.total_carbon for r in carbon_results)
        benchmark = self.benchmarks.get(project_type, 1000)
        
        # Base score from carbon performance
        carbon_score = max(0, 100 - (total_carbon / benchmark) * 100)
        
        # Bonus for sustainable materials
        sustainable_materials = [r for r in carbon_results if r.material in ['wood', 'recycled', 'sustainable']]
        material_bonus = min(20, len(sustainable_materials) * 5)
        
        # Penalty for high carbon materials
        high_carbon_penalty = len([r for r in carbon_results if r.carbon_factor > 5.0]) * 10
        
        final_score = carbon_score + material_bonus - high_carbon_penalty
        return max(0, min(100, final_score))
    
    def generate_carbon_report(self, analysis: CarbonAnalysis) -> Dict:
        """Generate comprehensive carbon footprint report"""
        return {
            'summary': {
                'total_carbon_kg_co2e': round(analysis.total_carbon, 2),
                'carbon_intensity_kg_co2e_per_unit': round(analysis.carbon_intensity, 3),
                'sustainability_score': round(analysis.sustainability_score, 1),
                'carbon_savings_potential_kg_co2e': round(analysis.carbon_savings_potential, 2)
            },
            'material_breakdown': {
                material: round(carbon, 2) 
                for material, carbon in analysis.material_breakdown.items()
            },
            'high_impact_elements': analysis.high_impact_elements,
            'optimization_recommendations': analysis.optimization_recommendations,
            'compliance_status': analysis.compliance_status,
            'benchmarks': {
                'project_type_benchmark': self.benchmarks.get('commercial', 1000),
                'low_carbon_benchmark': self.benchmarks['low_carbon'],
                'sustainable_benchmark': self.benchmarks['sustainable']
            },
            'report_metadata': {
                'timestamp': analysis.report_timestamp,
                'calculator_version': '1.0',
                'database_coverage': len(self.carbon_factors)
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize calculator
    calculator = CarbonFootprintCalculator()
    
    # Test elements
    test_elements = [
        {
            'type': 'wall',
            'material': 'concrete',
            'quantity': 1000,
            'unit': 'kg',
            'specifications': ['standard'],
            'transportation': 'local',
            'confidence': 0.8
        },
        {
            'type': 'beam',
            'material': 'steel',
            'quantity': 500,
            'unit': 'kg',
            'specifications': ['high_strength'],
            'transportation': 'regional',
            'confidence': 0.9
        }
    ]
    
    # Perform analysis
    analysis = calculator.analyze_carbon_footprint(test_elements, 'commercial')
    
    if analysis:
        # Generate report
        report = calculator.generate_carbon_report(analysis)
        print("Carbon Footprint Analysis Report:")
        print(json.dumps(report, indent=2))
    else:
        print("Error in carbon footprint analysis") 