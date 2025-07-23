"""
Basic Carbon Footprint Analysis Test
Tests core carbon footprint calculation without enhanced inference dependencies.
"""

import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import carbon footprint calculator
from carbon_footprint import CarbonFootprintCalculator

def test_basic_carbon_calculation():
    """Test basic carbon footprint calculation"""
    logger.info("Testing basic carbon calculation...")
    
    try:
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
            },
            {
                'type': 'column',
                'material': 'wood',
                'quantity': 300,
                'unit': 'kg',
                'specifications': ['sustainable'],
                'transportation': 'local',
                'confidence': 0.7
            }
        ]
        
        # Calculate carbon footprint
        analysis = calculator.analyze_carbon_footprint(test_elements, 'commercial')
        
        if not analysis:
            logger.error("Basic carbon calculation failed")
            return False
        
        # Generate report
        report = calculator.generate_carbon_report(analysis)
        
        # Print results
        logger.info(f"Total Carbon: {analysis.total_carbon:.2f} kg CO2e")
        logger.info(f"Carbon Intensity: {analysis.carbon_intensity:.3f} kg CO2e per unit")
        logger.info(f"Sustainability Score: {analysis.sustainability_score:.1f}")
        logger.info(f"Material Breakdown: {analysis.material_breakdown}")
        logger.info(f"Recommendations: {analysis.optimization_recommendations}")
        
        # Save results
        with open('basic_carbon_test_results.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Basic carbon calculation test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Basic carbon calculation test failed: {e}")
        return False

def test_carbon_database():
    """Test carbon database operations"""
    logger.info("Testing carbon database...")
    
    try:
        calculator = CarbonFootprintCalculator()
        
        # Test carbon factors
        assert len(calculator.carbon_factors) > 20, "Should have comprehensive carbon factors"
        assert 'concrete' in calculator.carbon_factors, "Should have concrete factor"
        assert 'steel' in calculator.carbon_factors, "Should have steel factor"
        assert 'wood' in calculator.carbon_factors, "Should have wood factor"
        
        # Test specification multipliers
        assert len(calculator.specification_multipliers) > 10, "Should have specification multipliers"
        assert 'recycled' in calculator.specification_multipliers, "Should have recycled multiplier"
        assert 'sustainable' in calculator.specification_multipliers, "Should have sustainable multiplier"
        
        # Test transportation factors
        assert len(calculator.transportation_factors) > 3, "Should have transportation factors"
        assert 'local' in calculator.transportation_factors, "Should have local transportation"
        assert 'international' in calculator.transportation_factors, "Should have international transportation"
        
        # Test benchmarks
        assert len(calculator.benchmarks) > 5, "Should have benchmarks"
        assert 'residential' in calculator.benchmarks, "Should have residential benchmark"
        assert 'commercial' in calculator.benchmarks, "Should have commercial benchmark"
        
        logger.info("Carbon database test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Carbon database test failed: {e}")
        return False

def test_carbon_optimization():
    """Test carbon optimization scenarios"""
    logger.info("Testing carbon optimization scenarios...")
    
    try:
        calculator = CarbonFootprintCalculator()
        
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
        
        high_carbon_analysis = calculator.analyze_carbon_footprint(high_carbon_elements, 'commercial')
        high_carbon_report = calculator.generate_carbon_report(high_carbon_analysis)
        
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
        
        low_carbon_analysis = calculator.analyze_carbon_footprint(low_carbon_elements, 'commercial')
        low_carbon_report = calculator.generate_carbon_report(low_carbon_analysis)
        
        # Print comparison
        logger.info(f"High Carbon Scenario: {high_carbon_analysis.total_carbon:.2f} kg CO2e")
        logger.info(f"Low Carbon Scenario: {low_carbon_analysis.total_carbon:.2f} kg CO2e")
        logger.info(f"High Carbon Sustainability: {high_carbon_analysis.sustainability_score:.1f}")
        logger.info(f"Low Carbon Sustainability: {low_carbon_analysis.sustainability_score:.1f}")
        
        # Validate optimization differences
        assert high_carbon_analysis.total_carbon > low_carbon_analysis.total_carbon, "High carbon should be higher"
        assert high_carbon_analysis.sustainability_score < low_carbon_analysis.sustainability_score, "Low carbon should have higher sustainability"
        
        # Save comparison
        comparison = {
            'high_carbon': high_carbon_report,
            'low_carbon': low_carbon_report,
            'comparison': {
                'carbon_difference': high_carbon_analysis.total_carbon - low_carbon_analysis.total_carbon,
                'sustainability_difference': low_carbon_analysis.sustainability_score - high_carbon_analysis.sustainability_score
            }
        }
        
        with open('carbon_optimization_comparison.json', 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info("Carbon optimization test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Carbon optimization test failed: {e}")
        return False

def main():
    """Run all basic carbon tests"""
    logger.info("Basic Carbon Footprint Analysis Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Basic Carbon Calculation", test_basic_carbon_calculation),
        ("Carbon Database", test_carbon_database),
        ("Carbon Optimization", test_carbon_optimization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            if success:
                passed += 1
                logger.info(f"{test_name}: ✅ PASSED")
            else:
                logger.error(f"{test_name}: ❌ FAILED")
                
        except Exception as e:
            logger.error(f"{test_name}: ❌ ERROR - {e}")
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("BASIC CARBON ANALYSIS TEST SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Total Tests: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {total - passed}")
    logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("\n🎉 ALL BASIC TESTS PASSED! Core carbon analysis system is working.")
        return True
    else:
        logger.error(f"\n⚠️  {total - passed} tests failed. Please review issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 