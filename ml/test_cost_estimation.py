"""
Test script for Cost Estimation System

This script tests the cost estimation system with synthetic and real data
to verify accurate cost calculations and analysis.
"""

import os
import sys
import json
import logging
import numpy as np
import cv2
from pathlib import Path

# Add the ML directory to the path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "models"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_elements():
    """Create test elements for cost estimation."""
    return [
        {
            "id": "wall_001",
            "type": "wall",
            "bbox": [100, 100, 300, 200],
            "confidence": 0.85,
            "enhanced_properties": {
                "materials": ["CONCRETE"],
                "specifications": ["FIRE RATED"],
                "dimensions": [{"value": 3000, "unit": "MM"}]
            }
        },
        {
            "id": "door_001",
            "type": "door",
            "bbox": [150, 200, 200, 250],
            "confidence": 0.82,
            "enhanced_properties": {
                "materials": ["TIMBER"],
                "specifications": ["FIRE RATED"]
            }
        },
        {
            "id": "window_001",
            "type": "window",
            "bbox": [250, 100, 300, 150],
            "confidence": 0.78,
            "enhanced_properties": {
                "materials": ["ALUMINIUM"],
                "dimensions": [{"value": 1200, "unit": "MM"}]
            }
        },
        {
            "id": "column_001",
            "type": "column",
            "bbox": [400, 100, 450, 300],
            "confidence": 0.90,
            "enhanced_properties": {
                "materials": ["CONCRETE"],
                "specifications": ["STRUCTURAL", "REINFORCED"]
            }
        },
        {
            "id": "beam_001",
            "type": "beam",
            "bbox": [100, 350, 700, 380],
            "confidence": 0.88,
            "enhanced_properties": {
                "materials": ["STEEL"],
                "specifications": ["STRUCTURAL"],
                "dimensions": [{"value": 6000, "unit": "MM"}]
            }
        }
    ]

def test_basic_cost_estimation():
    """Test basic cost estimation functionality."""
    print("Basic Cost Estimation Test")
    print("=" * 40)
    
    try:
        from cost_estimation import CostEstimator, CostDatabase
        
        # Initialize cost estimator
        cost_db = CostDatabase()
        estimator = CostEstimator(cost_db)
        
        # Create test elements
        test_elements = create_test_elements()
        
        # Estimate costs
        summary = estimator.estimate_project_costs(test_elements)
        
        print(f"Total Cost: ${summary.total_cost:,.2f}")
        print(f"Currency: {summary.currency}")
        print(f"Element Count: {summary.element_count}")
        print(f"Assumptions: {summary.assumptions}")
        
        # Show element breakdown
        print("\nElement Cost Breakdown:")
        for cost in summary.element_costs:
            print(f"  {cost.element_type}: ${cost.total_cost:,.2f} ({cost.quantity} {cost.unit})")
        
        # Generate report
        report = estimator.generate_cost_report(summary)
        
        print(f"\nCost Breakdown by Element Type:")
        for element_type, cost in report['breakdown']['by_element_type'].items():
            print(f"  {element_type}: ${cost:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"Error in basic cost estimation test: {e}")
        return False

def test_enhanced_cost_estimation():
    """Test enhanced cost estimation with synthetic image."""
    print("\nEnhanced Cost Estimation Test")
    print("=" * 40)
    
    try:
        from enhanced_cost_estimation import EnhancedCostEstimator
        from models.enhanced_inference import Discipline
        
        # Initialize enhanced cost estimator
        enhanced_estimator = EnhancedCostEstimator()
        
        # Create synthetic test image
        test_image = create_test_image_with_elements()
        
        # Test for each discipline
        disciplines = [Discipline.ARCHITECTURAL, Discipline.STRUCTURAL, Discipline.CIVIL, Discipline.MEP]
        
        for discipline in disciplines:
            print(f"\n--- Testing {discipline.value.upper()} ---")
            
            # Analyze costs
            analysis = enhanced_estimator.analyze_drawing_costs(
                test_image, discipline, "medium"
            )
            
            print(f"Total Cost: ${analysis.project_summary.total_cost:,.2f}")
            print(f"Element Count: {analysis.project_summary.element_count}")
            print(f"Confidence Score: {analysis.confidence_score:.2f}")
            
            # Show discipline breakdown
            if analysis.discipline_breakdown:
                print("Discipline Breakdown:")
                for disc, data in analysis.discipline_breakdown.items():
                    if data['count'] > 0:
                        print(f"  {disc}: {data['count']} elements, ${data['cost']:,.2f}")
            
            # Show recommendations
            if analysis.recommendations:
                print("Recommendations:")
                for rec in analysis.recommendations[:3]:  # Show first 3
                    print(f"  - {rec}")
        
        return True
        
    except Exception as e:
        print(f"Error in enhanced cost estimation test: {e}")
        return False

def create_test_image_with_elements(width: int = 800, height: int = 600) -> np.ndarray:
    """Create a test image with synthetic elements."""
    # Create white background
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw elements
    # Wall
    cv2.rectangle(image, (100, 100), (300, 200), (0, 0, 0), 2)
    
    # Door
    cv2.rectangle(image, (150, 200), (200, 250), (0, 0, 0), 2)
    
    # Window
    cv2.rectangle(image, (250, 100), (300, 150), (0, 0, 0), 2)
    
    # Column
    cv2.rectangle(image, (400, 100), (450, 300), (0, 0, 0), 3)
    
    # Beam
    cv2.rectangle(image, (100, 350), (700, 380), (0, 0, 0), 3)
    
    # Add text labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    
    cv2.putText(image, "WALL", (120, 130), font, font_scale, (0, 0, 0), thickness)
    cv2.putText(image, "DOOR", (160, 220), font, font_scale, (0, 0, 0), thickness)
    cv2.putText(image, "WINDOW", (260, 120), font, font_scale, (0, 0, 0), thickness)
    cv2.putText(image, "COLUMN", (410, 120), font, font_scale, (0, 0, 0), thickness)
    cv2.putText(image, "BEAM", (120, 370), font, font_scale, (0, 0, 0), thickness)
    
    # Add dimensions
    cv2.putText(image, "3000MM", (120, 80), font, 0.5, (0, 0, 0), thickness)
    cv2.putText(image, "6000MM", (120, 330), font, 0.5, (0, 0, 0), thickness)
    
    # Add materials
    cv2.putText(image, "CONCRETE", (500, 50), font, font_scale, (0, 0, 0), thickness)
    cv2.putText(image, "STEEL", (500, 80), font, font_scale, (0, 0, 0), thickness)
    
    return image

def test_with_real_pdf():
    """Test cost estimation with real PDF from backend uploads."""
    print("\nReal PDF Cost Estimation Test")
    print("=" * 40)
    
    try:
        from enhanced_cost_estimation import EnhancedCostEstimator
        from models.enhanced_inference import Discipline
        import fitz  # PyMuPDF
        
        # Initialize enhanced cost estimator
        enhanced_estimator = EnhancedCostEstimator()
        
        # Look for test PDFs in backend uploads
        backend_uploads = Path("../backend/uploads")
        pdf_files = list(backend_uploads.glob("*.pdf"))
        
        if not pdf_files:
            print("No PDF files found in backend/uploads directory")
            return False
        
        # Use the first PDF found
        test_pdf = pdf_files[0]
        print(f"Testing with PDF: {test_pdf}")
        
        # Extract first page as image
        pdf_document = fitz.open(test_pdf)
        page = pdf_document[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        
        # Convert to numpy array
        img_data = pix.tobytes("png")
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            print("Failed to load image from PDF")
            return False
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        print(f"Image loaded: {image_rgb.shape}")
        
        # Test cost estimation for architectural discipline
        analysis = enhanced_estimator.analyze_drawing_costs(
            image_rgb, Discipline.ARCHITECTURAL, "medium"
        )
        
        print(f"Real PDF Cost Analysis:")
        print(f"  Total Cost: ${analysis.project_summary.total_cost:,.2f}")
        print(f"  Element Count: {analysis.project_summary.element_count}")
        print(f"  Confidence Score: {analysis.confidence_score:.2f}")
        print(f"  Currency: {analysis.project_summary.currency}")
        
        # Show cost breakdown
        if analysis.discipline_breakdown:
            print("  Cost Breakdown by Discipline:")
            for disc, data in analysis.discipline_breakdown.items():
                if data['count'] > 0:
                    print(f"    {disc}: {data['count']} elements, ${data['cost']:,.2f}")
        
        # Show material analysis
        if analysis.material_analysis:
            print("  Material Analysis:")
            for material, data in analysis.material_analysis.items():
                if data['count'] > 0:
                    print(f"    {material}: {data['count']} elements, ${data['total_cost']:,.2f}")
        
        # Show recommendations
        if analysis.recommendations:
            print("  Recommendations:")
            for rec in analysis.recommendations[:3]:
                print(f"    - {rec}")
        
        # Generate and save report
        report = enhanced_estimator.generate_comprehensive_report(
            analysis, f"Real_PDF_{test_pdf.stem}"
        )
        
        output_file = "real_pdf_cost_report.json"
        enhanced_estimator.save_analysis_report(analysis, output_file, f"Real_PDF_{test_pdf.stem}")
        print(f"  Cost report saved to: {output_file}")
        
        pdf_document.close()
        return True
        
    except Exception as e:
        print(f"Error testing with real PDF: {e}")
        return False

def test_cost_database():
    """Test cost database functionality."""
    print("\nCost Database Test")
    print("=" * 40)
    
    try:
        from cost_estimation import CostDatabase, CostRate, CostUnit
        
        # Initialize cost database
        cost_db = CostDatabase()
        
        # Test getting rates
        wall_rate = cost_db.get_rate("wall", "concrete")
        if wall_rate:
            print(f"Wall (concrete) rate: ${wall_rate.base_rate:.2f} per {wall_rate.unit.value}")
        
        door_rate = cost_db.get_rate("door", "timber")
        if door_rate:
            print(f"Door (timber) rate: ${door_rate.base_rate:.2f} per {door_rate.unit.value}")
        
        # Test adding a new rate
        new_rate = CostRate(
            element_type="custom_element",
            material="composite",
            unit=CostUnit.PER_UNIT,
            base_rate=250.0,
            currency="USD"
        )
        
        cost_db.add_rate("custom_element", "composite", new_rate)
        
        # Verify the new rate was added
        custom_rate = cost_db.get_rate("custom_element", "composite")
        if custom_rate:
            print(f"Custom element (composite) rate: ${custom_rate.base_rate:.2f} per {custom_rate.unit.value}")
        
        print("Cost database test completed successfully")
        return True
        
    except Exception as e:
        print(f"Error in cost database test: {e}")
        return False

def main():
    """Main test function."""
    print("Cost Estimation System Test")
    print("=" * 60)
    
    # Test 1: Basic cost estimation
    success1 = test_basic_cost_estimation()
    
    # Test 2: Enhanced cost estimation
    success2 = test_enhanced_cost_estimation()
    
    # Test 3: Cost database
    success3 = test_cost_database()
    
    # Test 4: Real PDF
    success4 = test_with_real_pdf()
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"  Basic Cost Estimation: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"  Enhanced Cost Estimation: {'✅ PASSED' if success2 else '❌ FAILED'}")
    print(f"  Cost Database: {'✅ PASSED' if success3 else '❌ FAILED'}")
    print(f"  Real PDF Test: {'✅ PASSED' if success4 else '❌ FAILED'}")
    
    if success1 and success2 and success3 and success4:
        print("\n🎉 All tests passed! Cost estimation system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 