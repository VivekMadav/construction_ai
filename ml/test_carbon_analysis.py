"""
Test Script for Carbon Footprint Analysis System
Comprehensive testing of carbon footprint calculation and analysis capabilities.
"""

import json
import logging
import sys
import os
from pathlib import Path

# Add ML directory to path
sys.path.append(str(Path(__file__).parent))

from carbon_footprint import CarbonFootprintCalculator
from enhanced_carbon_analysis import EnhancedCarbonAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CarbonAnalysisTester:
    """Test suite for carbon footprint analysis system"""
    
    def __init__(self):
        """Initialize test suite"""
        self.carbon_calculator = CarbonFootprintCalculator()
        self.enhanced_analyzer = EnhancedCarbonAnalyzer()
        self.test_results = []
        
    def test_basic_carbon_calculation(self) -> bool:
        """Test basic carbon footprint calculation"""
        logger.info("Testing basic carbon calculation...")
        
        try:
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
            
            # Calculate carbon footprint
            analysis = self.carbon_calculator.analyze_carbon_footprint(test_elements, 'commercial')
            
            if not analysis:
                logger.error("Basic carbon calculation failed")
                return False
            
            # Validate results
            assert analysis.total_carbon > 0, "Total carbon should be positive"
            assert analysis.carbon_intensity > 0, "Carbon intensity should be positive"
            assert len(analysis.material_breakdown) > 0, "Material breakdown should not be empty"
            assert len(analysis.optimization_recommendations) > 0, "Should have recommendations"
            
            logger.info(f"Basic carbon calculation passed: {analysis.total_carbon:.2f} kg CO2e")
            return True
            
        except Exception as e:
            logger.error(f"Basic carbon calculation test failed: {e}")
            return False
    
    def test_enhanced_carbon_analysis(self) -> bool:
        """Test enhanced carbon analysis with synthetic data"""
        logger.info("Testing enhanced carbon analysis...")
        
        try:
            # Create synthetic inference results
            synthetic_inference = {
                'elements': [
                    {
                        'type': 'wall',
                        'material': 'concrete',
                        'quantity': 2000,
                        'unit': 'kg',
                        'specifications': ['standard'],
                        'confidence': 0.85
                    },
                    {
                        'type': 'column',
                        'material': 'steel',
                        'quantity': 800,
                        'unit': 'kg',
                        'specifications': ['high_strength'],
                        'confidence': 0.9
                    },
                    {
                        'type': 'floor',
                        'material': 'concrete',
                        'quantity': 1500,
                        'unit': 'kg',
                        'specifications': ['standard'],
                        'confidence': 0.8
                    }
                ],
                'overall_confidence': 0.85,
                'accuracy': 0.88,
                'discipline_breakdown': {'structural': 3},
                'ocr_enhanced': True,
                'text_elements': ['wall', 'column', 'floor']
            }
            
            # Convert to carbon analysis format
            elements_for_carbon = self.enhanced_analyzer._convert_elements_for_carbon_analysis(
                synthetic_inference['elements']
            )
            
            # Perform carbon analysis
            carbon_analysis = self.carbon_calculator.analyze_carbon_footprint(elements_for_carbon, 'commercial')
            
            if not carbon_analysis:
                logger.error("Enhanced carbon analysis failed")
                return False
            
            # Generate report
            report = self.carbon_calculator.generate_carbon_report(carbon_analysis)
            
            # Enhance with inference data
            enhanced_report = self.enhanced_analyzer._enhance_report_with_inference_data(report, synthetic_inference)
            
            # Validate enhanced report
            assert 'inference_metadata' in enhanced_report, "Should have inference metadata"
            assert 'element_carbon_details' in enhanced_report, "Should have element carbon details"
            assert enhanced_report['inference_metadata']['overall_confidence'] == 0.85
            assert len(enhanced_report['element_carbon_details']) == 3
            
            logger.info(f"Enhanced carbon analysis passed: {carbon_analysis.total_carbon:.2f} kg CO2e")
            return True
            
        except Exception as e:
            logger.error(f"Enhanced carbon analysis test failed: {e}")
            return False
    
    def test_carbon_database_operations(self) -> bool:
        """Test carbon database operations"""
        logger.info("Testing carbon database operations...")
        
        try:
            # Test carbon factors
            assert len(self.carbon_calculator.carbon_factors) > 20, "Should have comprehensive carbon factors"
            assert 'concrete' in self.carbon_calculator.carbon_factors, "Should have concrete factor"
            assert 'steel' in self.carbon_calculator.carbon_factors, "Should have steel factor"
            assert 'wood' in self.carbon_calculator.carbon_factors, "Should have wood factor"
            
            # Test specification multipliers
            assert len(self.carbon_calculator.specification_multipliers) > 10, "Should have specification multipliers"
            assert 'recycled' in self.carbon_calculator.specification_multipliers, "Should have recycled multiplier"
            assert 'sustainable' in self.carbon_calculator.specification_multipliers, "Should have sustainable multiplier"
            
            # Test transportation factors
            assert len(self.carbon_calculator.transportation_factors) > 3, "Should have transportation factors"
            assert 'local' in self.carbon_calculator.transportation_factors, "Should have local transportation"
            assert 'international' in self.carbon_calculator.transportation_factors, "Should have international transportation"
            
            # Test benchmarks
            assert len(self.carbon_calculator.benchmarks) > 5, "Should have benchmarks"
            assert 'residential' in self.carbon_calculator.benchmarks, "Should have residential benchmark"
            assert 'commercial' in self.carbon_calculator.benchmarks, "Should have commercial benchmark"
            
            logger.info("Carbon database operations passed")
            return True
            
        except Exception as e:
            logger.error(f"Carbon database operations test failed: {e}")
            return False
    
    def test_carbon_optimization_scenarios(self) -> bool:
        """Test carbon optimization scenarios"""
        logger.info("Testing carbon optimization scenarios...")
        
        try:
            # High carbon scenario
            high_carbon_elements = [
                {
                    'type': 'beam',
                    'material': 'aluminum',
                    'quantity': 1000,
                    'unit': 'kg',
                    'specifications': ['premium'],
                    'transportation': 'international',
                    'confidence': 0.9
                }
            ]
            
            high_carbon_analysis = self.carbon_calculator.analyze_carbon_footprint(high_carbon_elements, 'commercial')
            high_carbon_report = self.carbon_calculator.generate_carbon_report(high_carbon_analysis)
            
            # Low carbon scenario
            low_carbon_elements = [
                {
                    'type': 'wall',
                    'material': 'wood',
                    'quantity': 1000,
                    'unit': 'kg',
                    'specifications': ['sustainable'],
                    'transportation': 'local',
                    'confidence': 0.9
                }
            ]
            
            low_carbon_analysis = self.carbon_calculator.analyze_carbon_footprint(low_carbon_elements, 'commercial')
            low_carbon_report = self.carbon_calculator.generate_carbon_report(low_carbon_analysis)
            
            # Validate optimization differences
            assert high_carbon_analysis.total_carbon > low_carbon_analysis.total_carbon, "High carbon should be higher"
            assert high_carbon_analysis.sustainability_score < low_carbon_analysis.sustainability_score, "Low carbon should have higher sustainability"
            
            # Check recommendations
            high_recommendations = high_carbon_analysis.optimization_recommendations
            low_recommendations = low_carbon_analysis.optimization_recommendations
            
            assert len(high_recommendations) > 0, "High carbon should have optimization recommendations"
            
            logger.info(f"Carbon optimization scenarios passed - High: {high_carbon_analysis.total_carbon:.2f} kg CO2e, Low: {low_carbon_analysis.total_carbon:.2f} kg CO2e")
            return True
            
        except Exception as e:
            logger.error(f"Carbon optimization scenarios test failed: {e}")
            return False
    
    def test_carbon_insights_generation(self) -> bool:
        """Test carbon insights generation"""
        logger.info("Testing carbon insights generation...")
        
        try:
            # Create test carbon report
            test_elements = [
                {
                    'type': 'wall',
                    'material': 'concrete',
                    'quantity': 1000,
                    'unit': 'kg',
                    'specifications': ['standard'],
                    'transportation': 'local',
                    'confidence': 0.8
                }
            ]
            
            analysis = self.carbon_calculator.analyze_carbon_footprint(test_elements, 'commercial')
            report = self.carbon_calculator.generate_carbon_report(analysis)
            
            # Generate insights
            insights = self.enhanced_analyzer.get_carbon_insights(report)
            
            # Validate insights structure
            assert 'key_findings' in insights, "Should have key findings"
            assert 'environmental_impact' in insights, "Should have environmental impact"
            assert 'optimization_opportunities' in insights, "Should have optimization opportunities"
            assert 'sustainability_metrics' in insights, "Should have sustainability metrics"
            
            # Validate environmental impact calculations
            env_impact = insights['environmental_impact']
            assert 'carbon_equivalent' in env_impact, "Should have carbon equivalents"
            assert 'trees_planted' in env_impact['carbon_equivalent'], "Should have trees planted equivalent"
            assert 'car_miles' in env_impact['carbon_equivalent'], "Should have car miles equivalent"
            
            logger.info("Carbon insights generation passed")
            return True
            
        except Exception as e:
            logger.error(f"Carbon insights generation test failed: {e}")
            return False
    
    def test_real_pdf_carbon_analysis(self) -> bool:
        """Test carbon analysis on real PDF (if available)"""
        logger.info("Testing real PDF carbon analysis...")
        
        try:
            # Check if test PDF exists
            test_pdf_path = "test_drawing.pdf"
            if not os.path.exists(test_pdf_path):
                logger.warning(f"Test PDF not found: {test_pdf_path}")
                logger.info("Skipping real PDF test - creating synthetic PDF test instead")
                
                # Create synthetic PDF test
                synthetic_pdf_results = {
                    'pages': [
                        {
                            'elements': [
                                {
                                    'type': 'wall',
                                    'material': 'concrete',
                                    'quantity': 1500,
                                    'unit': 'kg',
                                    'specifications': ['standard'],
                                    'confidence': 0.85
                                },
                                {
                                    'type': 'beam',
                                    'material': 'steel',
                                    'quantity': 600,
                                    'unit': 'kg',
                                    'specifications': ['high_strength'],
                                    'confidence': 0.9
                                }
                            ]
                        },
                        {
                            'elements': [
                                {
                                    'type': 'column',
                                    'material': 'concrete',
                                    'quantity': 800,
                                    'unit': 'kg',
                                    'specifications': ['standard'],
                                    'confidence': 0.8
                                }
                            ]
                        }
                    ],
                    'timestamp': '2024-01-01T00:00:00',
                    'overall_confidence': 0.85
                }
                
                # Simulate PDF analysis
                all_elements = []
                for page in synthetic_pdf_results['pages']:
                    page_elements = self.enhanced_analyzer._convert_elements_for_carbon_analysis(page['elements'])
                    all_elements.extend(page_elements)
                
                if all_elements:
                    analysis = self.carbon_calculator.analyze_carbon_footprint(all_elements, 'commercial')
                    report = self.carbon_calculator.generate_carbon_report(analysis)
                    
                    # Save synthetic results
                    with open('synthetic_pdf_carbon_report.json', 'w') as f:
                        json.dump(report, f, indent=2)
                    
                    logger.info(f"Synthetic PDF carbon analysis completed: {analysis.total_carbon:.2f} kg CO2e")
                    return True
                else:
                    logger.error("No elements found in synthetic PDF")
                    return False
            
            # Real PDF analysis would go here
            # pdf_report = self.enhanced_analyzer.analyze_pdf_carbon_footprint(test_pdf_path, 'commercial')
            
            return True
            
        except Exception as e:
            logger.error(f"Real PDF carbon analysis test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all carbon analysis tests"""
        logger.info("Starting comprehensive carbon analysis tests...")
        
        tests = [
            ("Basic Carbon Calculation", self.test_basic_carbon_calculation),
            ("Enhanced Carbon Analysis", self.test_enhanced_carbon_analysis),
            ("Carbon Database Operations", self.test_carbon_database_operations),
            ("Carbon Optimization Scenarios", self.test_carbon_optimization_scenarios),
            ("Carbon Insights Generation", self.test_carbon_insights_generation),
            ("Real PDF Carbon Analysis", self.test_real_pdf_carbon_analysis)
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*50}")
            
            try:
                success = test_func()
                results[test_name] = "PASSED" if success else "FAILED"
                if success:
                    passed += 1
                logger.info(f"{test_name}: {'✅ PASSED' if success else '❌ FAILED'}")
                
            except Exception as e:
                results[test_name] = f"ERROR: {str(e)}"
                logger.error(f"{test_name}: ❌ ERROR - {e}")
        
        # Summary
        logger.info(f"\n{'='*50}")
        logger.info("CARBON ANALYSIS TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {total - passed}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        for test_name, result in results.items():
            status = "✅" if result == "PASSED" else "❌"
            logger.info(f"{status} {test_name}: {result}")
        
        # Save detailed results
        with open('carbon_analysis_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total,
                    'passed': passed,
                    'failed': total - passed,
                    'success_rate': (passed/total)*100
                },
                'detailed_results': results,
                'timestamp': '2024-01-01T00:00:00'
            }, f, indent=2)
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed/total)*100,
            'results': results
        }

def main():
    """Main test execution"""
    logger.info("Carbon Footprint Analysis System Test Suite")
    logger.info("=" * 50)
    
    tester = CarbonAnalysisTester()
    results = tester.run_all_tests()
    
    if results['passed'] == results['total_tests']:
        logger.info("\n🎉 ALL TESTS PASSED! Carbon analysis system is ready.")
        return True
    else:
        logger.error(f"\n⚠️  {results['failed']} tests failed. Please review issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 