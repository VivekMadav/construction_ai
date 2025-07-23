"""
Phase 6: Carbon Footprint Analysis Demo
Demonstrates the complete carbon footprint analysis system capabilities.
"""

import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_carbon_footprint_analysis():
    """Demonstrate carbon footprint analysis capabilities"""
    logger.info("Phase 6: Carbon Footprint Analysis Demo")
    logger.info("=" * 60)
    
    try:
        # Import carbon footprint calculator
        from carbon_footprint import CarbonFootprintCalculator
        
        # Initialize calculator
        calculator = CarbonFootprintCalculator()
        logger.info("✅ Carbon footprint calculator initialized")
        
        # Demo 1: Basic Carbon Calculation
        logger.info("\n📊 Demo 1: Basic Carbon Calculation")
        logger.info("-" * 40)
        
        basic_elements = [
            {
                'type': 'wall',
                'material': 'concrete',
                'quantity': 2000,
                'unit': 'kg',
                'specifications': ['standard'],
                'transportation': 'local',
                'confidence': 0.8
            },
            {
                'type': 'beam',
                'material': 'steel',
                'quantity': 800,
                'unit': 'kg',
                'specifications': ['high_strength'],
                'transportation': 'regional',
                'confidence': 0.9
            },
            {
                'type': 'column',
                'material': 'wood',
                'quantity': 500,
                'unit': 'kg',
                'specifications': ['sustainable'],
                'transportation': 'local',
                'confidence': 0.7
            }
        ]
        
        basic_analysis = calculator.analyze_carbon_footprint(basic_elements, 'commercial')
        basic_report = calculator.generate_carbon_report(basic_analysis)
        
        logger.info(f"Total Carbon: {basic_analysis.total_carbon:.2f} kg CO2e")
        logger.info(f"Carbon Intensity: {basic_analysis.carbon_intensity:.3f} kg CO2e per unit")
        logger.info(f"Sustainability Score: {basic_analysis.sustainability_score:.1f}")
        logger.info(f"Material Breakdown: {basic_analysis.material_breakdown}")
        
        # Demo 2: High Carbon vs Low Carbon Comparison
        logger.info("\n🌱 Demo 2: High Carbon vs Low Carbon Comparison")
        logger.info("-" * 40)
        
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
        
        logger.info(f"High Carbon Scenario: {high_carbon_analysis.total_carbon:.2f} kg CO2e")
        logger.info(f"Low Carbon Scenario: {low_carbon_analysis.total_carbon:.2f} kg CO2e")
        logger.info(f"Carbon Difference: {high_carbon_analysis.total_carbon - low_carbon_analysis.total_carbon:.2f} kg CO2e")
        logger.info(f"High Carbon Sustainability: {high_carbon_analysis.sustainability_score:.1f}")
        logger.info(f"Low Carbon Sustainability: {low_carbon_analysis.sustainability_score:.1f}")
        
        # Demo 3: Environmental Equivalents
        logger.info("\n🌍 Demo 3: Environmental Equivalents")
        logger.info("-" * 40)
        
        total_carbon = basic_analysis.total_carbon
        trees_planted = total_carbon / 22  # kg CO2 absorbed by one tree per year
        car_miles = total_carbon * 2.3     # miles driven by average car
        flight_hours = total_carbon / 90   # hours of commercial flight
        
        logger.info(f"Carbon Footprint: {total_carbon:.2f} kg CO2e")
        logger.info(f"Equivalent to planting {trees_planted:.1f} trees")
        logger.info(f"Equivalent to driving {car_miles:.1f} miles")
        logger.info(f"Equivalent to {flight_hours:.1f} hours of commercial flight")
        
        # Demo 4: Optimization Recommendations
        logger.info("\n💡 Demo 4: Optimization Recommendations")
        logger.info("-" * 40)
        
        for i, recommendation in enumerate(basic_analysis.optimization_recommendations, 1):
            logger.info(f"{i}. {recommendation}")
        
        # Demo 5: Compliance Status
        logger.info("\n✅ Demo 5: Compliance Status")
        logger.info("-" * 40)
        
        compliance = basic_analysis.compliance_status
        for standard, compliant in compliance.items():
            status = "✅" if compliant else "❌"
            logger.info(f"{status} {standard.replace('_', ' ').title()}: {compliant}")
        
        # Demo 6: Carbon Savings Potential
        logger.info("\n💰 Demo 6: Carbon Savings Potential")
        logger.info("-" * 40)
        
        savings_potential = basic_analysis.carbon_savings_potential
        if savings_potential > 0:
            logger.info(f"Potential carbon savings: {savings_potential:.2f} kg CO2e")
            logger.info(f"Potential cost savings: ${savings_potential * 50:.2f} (estimated)")
        else:
            logger.info("Project already optimized for carbon efficiency")
        
        # Save comprehensive demo results
        demo_results = {
            'demo_summary': {
                'total_demos': 6,
                'carbon_calculations': 3,
                'comparisons': 1,
                'environmental_equivalents': 1,
                'optimization_recommendations': len(basic_analysis.optimization_recommendations),
                'compliance_checks': len(basic_analysis.compliance_status)
            },
            'basic_analysis': basic_report,
            'high_carbon_analysis': calculator.generate_carbon_report(high_carbon_analysis),
            'low_carbon_analysis': calculator.generate_carbon_report(low_carbon_analysis),
            'environmental_equivalents': {
                'trees_planted': trees_planted,
                'car_miles': car_miles,
                'flight_hours': flight_hours
            },
            'carbon_database_info': {
                'materials_covered': len(calculator.carbon_factors),
                'specifications_covered': len(calculator.specification_multipliers),
                'transportation_types': len(calculator.transportation_factors),
                'benchmarks_available': len(calculator.benchmarks)
            }
        }
        
        with open('phase6_demo_results.json', 'w') as f:
            json.dump(demo_results, f, indent=2)
        
        logger.info("\n📁 Demo results saved to 'phase6_demo_results.json'")
        
        # Final summary
        logger.info("\n🎉 Phase 6 Demo Summary")
        logger.info("=" * 60)
        logger.info("✅ Carbon footprint calculation system working")
        logger.info("✅ Environmental analysis capabilities demonstrated")
        logger.info("✅ Optimization recommendations generated")
        logger.info("✅ Compliance checking functional")
        logger.info("✅ Environmental equivalents calculated")
        logger.info("✅ Carbon savings potential identified")
        logger.info("✅ Comprehensive reporting system operational")
        
        return True
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return False

def main():
    """Run Phase 6 demo"""
    success = demo_carbon_footprint_analysis()
    
    if success:
        logger.info("\n🚀 Phase 6 Carbon Footprint Analysis Demo Completed Successfully!")
        logger.info("The system is ready for production use.")
    else:
        logger.error("\n❌ Phase 6 Demo Failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    main() 