"""
Enhanced Carbon Footprint Analysis System
Integrates with enhanced inference system for comprehensive environmental impact analysis.
"""

import json
import logging
from typing import Dict, List, Optional
from carbon_footprint import CarbonFootprintCalculator, CarbonAnalysis
from models.enhanced_inference import EnhancedInferenceSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCarbonAnalyzer:
    """Enhanced carbon footprint analyzer with inference integration"""
    
    def __init__(self):
        """Initialize enhanced carbon analyzer"""
        self.carbon_calculator = CarbonFootprintCalculator()
        self.inference_system = EnhancedInferenceSystem()
        logger.info("Enhanced Carbon Analyzer initialized")
    
    def analyze_drawing_carbon_footprint(self, image_path: str, project_type: str = 'commercial') -> Dict:
        """Analyze carbon footprint from drawing image"""
        try:
            # Run enhanced inference to detect elements
            logger.info(f"Running enhanced inference on {image_path}")
            inference_results = self.inference_system.analyze_image(image_path)
            
            if not inference_results or 'elements' not in inference_results:
                logger.warning("No elements detected in image")
                return self._create_empty_report(project_type)
            
            # Convert inference results to carbon analysis format
            elements_for_carbon = self._convert_elements_for_carbon_analysis(inference_results['elements'])
            
            # Perform carbon footprint analysis
            logger.info("Performing carbon footprint analysis")
            carbon_analysis = self.carbon_calculator.analyze_carbon_footprint(elements_for_carbon, project_type)
            
            if not carbon_analysis:
                logger.error("Carbon analysis failed")
                return self._create_empty_report(project_type)
            
            # Generate comprehensive report
            carbon_report = self.carbon_calculator.generate_carbon_report(carbon_analysis)
            
            # Enhance report with inference data
            enhanced_report = self._enhance_report_with_inference_data(carbon_report, inference_results)
            
            logger.info(f"Carbon analysis completed: {carbon_analysis.total_carbon:.2f} kg CO2e")
            return enhanced_report
            
        except Exception as e:
            logger.error(f"Error in enhanced carbon analysis: {e}")
            return self._create_error_report(str(e), project_type)
    
    def analyze_pdf_carbon_footprint(self, pdf_path: str, project_type: str = 'commercial') -> Dict:
        """Analyze carbon footprint from PDF drawings"""
        try:
            # Run enhanced inference on PDF
            logger.info(f"Running enhanced inference on PDF: {pdf_path}")
            inference_results = self.inference_system.analyze_pdf(pdf_path)
            
            if not inference_results or 'pages' not in inference_results:
                logger.warning("No pages detected in PDF")
                return self._create_empty_report(project_type)
            
            # Aggregate elements from all pages
            all_elements = []
            page_analyses = []
            
            for page_idx, page_result in enumerate(inference_results['pages']):
                if 'elements' in page_result:
                    page_elements = self._convert_elements_for_carbon_analysis(page_result['elements'])
                    all_elements.extend(page_elements)
                    
                    # Analyze each page individually
                    page_carbon = self.carbon_calculator.analyze_carbon_footprint(page_elements, project_type)
                    if page_carbon:
                        page_analyses.append({
                            'page_number': page_idx + 1,
                            'carbon_analysis': self.carbon_calculator.generate_carbon_report(page_carbon)
                        })
            
            # Perform overall carbon analysis
            if all_elements:
                overall_analysis = self.carbon_calculator.analyze_carbon_footprint(all_elements, project_type)
                overall_report = self.carbon_calculator.generate_carbon_report(overall_analysis)
            else:
                overall_report = self._create_empty_report(project_type)
            
            # Create comprehensive PDF report
            pdf_report = {
                'overall_analysis': overall_report,
                'page_analyses': page_analyses,
                'total_pages': len(inference_results['pages']),
                'total_elements': len(all_elements),
                'project_type': project_type,
                'analysis_timestamp': inference_results.get('timestamp', ''),
                'inference_confidence': inference_results.get('overall_confidence', 0.0)
            }
            
            logger.info(f"PDF carbon analysis completed: {overall_report.get('summary', {}).get('total_carbon_kg_co2e', 0):.2f} kg CO2e")
            return pdf_report
            
        except Exception as e:
            logger.error(f"Error in PDF carbon analysis: {e}")
            return self._create_error_report(str(e), project_type)
    
    def _convert_elements_for_carbon_analysis(self, elements: List[Dict]) -> List[Dict]:
        """Convert inference elements to carbon analysis format"""
        converted_elements = []
        
        for element in elements:
            # Extract basic information
            element_type = element.get('type', 'unknown')
            material = element.get('material', 'default')
            quantity = element.get('quantity', 0)
            unit = element.get('unit', 'kg')
            confidence = element.get('confidence', 0.5)
            
            # Extract specifications from element data
            specifications = []
            if 'specifications' in element:
                specifications = element['specifications']
            elif 'properties' in element:
                # Convert properties to specifications
                properties = element['properties']
                if properties.get('strength', '').lower() in ['high', 'premium']:
                    specifications.append('high_strength')
                if properties.get('sustainability', '').lower() in ['yes', 'true', 'sustainable']:
                    specifications.append('sustainable')
                if properties.get('recycled', '').lower() in ['yes', 'true', 'recycled']:
                    specifications.append('recycled')
            
            # Determine transportation based on material and context
            transportation = self._determine_transportation(material, element_type)
            
            # Create carbon analysis element
            carbon_element = {
                'type': element_type,
                'material': material,
                'quantity': quantity,
                'unit': unit,
                'specifications': specifications,
                'transportation': transportation,
                'transport_distance': self._estimate_transport_distance(material),
                'confidence': confidence
            }
            
            converted_elements.append(carbon_element)
        
        return converted_elements
    
    def _determine_transportation(self, material: str, element_type: str) -> str:
        """Determine transportation type based on material and element"""
        # Local materials
        local_materials = ['concrete', 'brick', 'stone', 'sand', 'gravel']
        if material in local_materials:
            return 'local'
        
        # Regional materials
        regional_materials = ['steel', 'wood', 'glass', 'tile']
        if material in regional_materials:
            return 'regional'
        
        # National/international materials
        international_materials = ['aluminum', 'copper', 'zinc', 'specialty_materials']
        if material in international_materials:
            return 'national'
        
        return 'regional'  # Default
    
    def _estimate_transport_distance(self, material: str) -> float:
        """Estimate transport distance based on material"""
        distance_map = {
            'concrete': 50,    # Local
            'brick': 75,       # Local
            'stone': 100,      # Regional
            'steel': 200,      # Regional
            'wood': 150,       # Regional
            'glass': 300,      # National
            'aluminum': 500,   # National
            'copper': 800,     # International
            'default': 200     # Default regional
        }
        return distance_map.get(material, distance_map['default'])
    
    def _enhance_report_with_inference_data(self, carbon_report: Dict, inference_results: Dict) -> Dict:
        """Enhance carbon report with inference system data"""
        enhanced_report = carbon_report.copy()
        
        # Add inference metadata
        enhanced_report['inference_metadata'] = {
            'overall_confidence': inference_results.get('overall_confidence', 0.0),
            'detection_accuracy': inference_results.get('accuracy', 0.0),
            'element_count': len(inference_results.get('elements', [])),
            'discipline_breakdown': inference_results.get('discipline_breakdown', {}),
            'ocr_enhancement': inference_results.get('ocr_enhanced', False),
            'text_elements_found': len(inference_results.get('text_elements', []))
        }
        
        # Add element-level carbon details
        if 'elements' in inference_results:
            element_carbon_details = []
            for element in inference_results['elements']:
                element_type = element.get('type', 'unknown')
                material = element.get('material', 'default')
                quantity = element.get('quantity', 0)
                
                # Find corresponding carbon result
                carbon_result = None
                for result in carbon_report.get('element_details', []):
                    if (result.get('element_type') == element_type and 
                        result.get('material') == material):
                        carbon_result = result
                        break
                
                element_carbon_details.append({
                    'element_type': element_type,
                    'material': material,
                    'quantity': quantity,
                    'unit': element.get('unit', 'kg'),
                    'confidence': element.get('confidence', 0.5),
                    'carbon_impact': carbon_result.get('total_carbon', 0) if carbon_result else 0,
                    'carbon_intensity': carbon_result.get('carbon_intensity', 0) if carbon_result else 0
                })
            
            enhanced_report['element_carbon_details'] = element_carbon_details
        
        return enhanced_report
    
    def _create_empty_report(self, project_type: str) -> Dict:
        """Create empty carbon report"""
        return {
            'summary': {
                'total_carbon_kg_co2e': 0.0,
                'carbon_intensity_kg_co2e_per_unit': 0.0,
                'sustainability_score': 0.0,
                'carbon_savings_potential_kg_co2e': 0.0
            },
            'material_breakdown': {},
            'high_impact_elements': [],
            'optimization_recommendations': ['No elements detected for carbon analysis'],
            'compliance_status': {
                'within_benchmark': True,
                'low_carbon_compliant': True,
                'sustainable_compliant': True,
                'passive_house_compliant': True,
                'intensity_acceptable': True
            },
            'benchmarks': {
                'project_type_benchmark': self.carbon_calculator.benchmarks.get(project_type, 1000),
                'low_carbon_benchmark': self.carbon_calculator.benchmarks['low_carbon'],
                'sustainable_benchmark': self.carbon_calculator.benchmarks['sustainable']
            },
            'report_metadata': {
                'timestamp': '2024-01-01T00:00:00',
                'calculator_version': '1.0',
                'database_coverage': len(self.carbon_calculator.carbon_factors),
                'status': 'no_elements_detected'
            }
        }
    
    def _create_error_report(self, error_message: str, project_type: str) -> Dict:
        """Create error carbon report"""
        error_report = self._create_empty_report(project_type)
        error_report['report_metadata']['status'] = 'error'
        error_report['report_metadata']['error_message'] = error_message
        error_report['optimization_recommendations'] = [f'Analysis failed: {error_message}']
        return error_report
    
    def get_carbon_insights(self, carbon_report: Dict) -> Dict:
        """Generate insights from carbon analysis"""
        insights = {
            'key_findings': [],
            'environmental_impact': {},
            'optimization_opportunities': [],
            'sustainability_metrics': {}
        }
        
        summary = carbon_report.get('summary', {})
        total_carbon = summary.get('total_carbon_kg_co2e', 0)
        sustainability_score = summary.get('sustainability_score', 0)
        
        # Key findings
        if total_carbon > 1000:
            insights['key_findings'].append(f"High carbon footprint: {total_carbon:.1f} kg CO2e")
        elif total_carbon < 100:
            insights['key_findings'].append(f"Low carbon footprint: {total_carbon:.1f} kg CO2e")
        
        if sustainability_score > 80:
            insights['key_findings'].append("Excellent sustainability performance")
        elif sustainability_score < 40:
            insights['key_findings'].append("Significant sustainability improvement needed")
        
        # Environmental impact
        insights['environmental_impact'] = {
            'carbon_equivalent': {
                'trees_planted': total_carbon / 22,  # kg CO2 absorbed by one tree per year
                'car_miles': total_carbon * 2.3,     # miles driven by average car
                'flight_hours': total_carbon / 90    # hours of commercial flight
            },
            'carbon_intensity': summary.get('carbon_intensity_kg_co2e_per_unit', 0)
        }
        
        # Optimization opportunities
        material_breakdown = carbon_report.get('material_breakdown', {})
        high_carbon_materials = [mat for mat, carbon in material_breakdown.items() 
                               if carbon > total_carbon * 0.2]  # >20% of total
        
        for material in high_carbon_materials:
            insights['optimization_opportunities'].append(f"Consider alternatives to {material}")
        
        # Sustainability metrics
        insights['sustainability_metrics'] = {
            'sustainability_score': sustainability_score,
            'compliance_status': carbon_report.get('compliance_status', {}),
            'carbon_savings_potential': summary.get('carbon_savings_potential_kg_co2e', 0)
        }
        
        return insights

# Example usage and testing
if __name__ == "__main__":
    # Initialize enhanced carbon analyzer
    analyzer = EnhancedCarbonAnalyzer()
    
    # Test with synthetic data
    test_elements = [
        {
            'type': 'wall',
            'material': 'concrete',
            'quantity': 1000,
            'unit': 'kg',
            'specifications': ['standard'],
            'confidence': 0.8
        },
        {
            'type': 'beam',
            'material': 'steel',
            'quantity': 500,
            'unit': 'kg',
            'specifications': ['high_strength'],
            'confidence': 0.9
        }
    ]
    
    # Test carbon analysis
    carbon_analysis = analyzer.carbon_calculator.analyze_carbon_footprint(test_elements, 'commercial')
    
    if carbon_analysis:
        report = analyzer.carbon_calculator.generate_carbon_report(carbon_analysis)
        insights = analyzer.get_carbon_insights(report)
        
        print("Enhanced Carbon Analysis Test Results:")
        print(json.dumps({
            'carbon_report': report,
            'insights': insights
        }, indent=2))
    else:
        print("Carbon analysis test failed") 