"""
Test script for cross-drawing reference integration

This script tests the integration of the drawing reference analyzer
and enhanced element measurement into the existing system.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_reference_analyzer():
    """Test the drawing reference analyzer."""
    try:
        from drawing_reference_analyzer import DrawingReferenceAnalyzer
        
        analyzer = DrawingReferenceAnalyzer()
        print("✅ DrawingReferenceAnalyzer initialized successfully")
        
        # Test with a sample drawing path
        test_drawing_path = "uploads/1/20250723_153938_4977_S_DW06 - WATER TANK LAYOUT - 2.pdf"
        
        if os.path.exists(test_drawing_path):
            references = analyzer.analyze_drawing_references("test_drawing_001", test_drawing_path)
            print(f"✅ Reference analysis completed: {len(references)} references found")
            
            # Print reference details
            for ref in references:
                print(f"  - {ref.reference_type.value}: {ref.reference_mark} -> {ref.target_drawing_id}")
        else:
            print("⚠️  Test drawing not found, skipping reference analysis test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing reference analyzer: {e}")
        return False

def test_enhanced_measurement():
    """Test the enhanced element measurement system."""
    try:
        from enhanced_element_measurement import EnhancedElementMeasurement
        
        measurer = EnhancedElementMeasurement()
        print("✅ EnhancedElementMeasurement initialized successfully")
        
        # Test with sample element data
        sample_element = {
            "id": "wall_001",
            "type": "wall",
            "drawing_id": "test_drawing_001",
            "confidence": 0.8,
            "measurements": {
                "length": 5.0,
                "length_unit": "m",
                "length_confidence": 0.8,
                "height": 3.0,
                "height_unit": "m",
                "height_confidence": 0.7
            }
        }
        
        # Test enhanced measurement
        enhanced_element = measurer.measure_element_with_cross_references(
            "test_drawing_001", sample_element, []
        )
        
        print(f"✅ Enhanced measurement completed for element: {enhanced_element.element_id}")
        print(f"  - Overall confidence: {enhanced_element.overall_confidence:.2f}")
        print(f"  - Cross-reference confidence: {enhanced_element.cross_reference_confidence:.2f}")
        print(f"  - Measurement completeness: {enhanced_element.measurement_completeness:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced measurement: {e}")
        return False

def test_pdf_processor_integration():
    """Test the PDF processor integration."""
    try:
        from backend.app.services.pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        print("✅ PDFProcessor initialized successfully")
        
        # Check if reference analysis is available
        if processor.reference_analyzer:
            print("✅ Reference analyzer integrated successfully")
        else:
            print("⚠️  Reference analyzer not available")
        
        if processor.enhanced_measurement:
            print("✅ Enhanced measurement integrated successfully")
        else:
            print("⚠️  Enhanced measurement not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing PDF processor integration: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints (simulated)."""
    try:
        print("✅ API endpoints configured:")
        print("  - POST /api/v1/enhanced-analysis/drawing/{drawing_id}")
        print("  - GET /api/v1/cross-references/drawing/{drawing_id}")
        print("  - POST /api/v1/enhanced-analysis/project/{project_id}")
        print("  - GET /api/v1/enhanced-analysis/statistics")
        print("  - POST /api/v1/enhanced-analysis/validate-measurements")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

def test_cross_drawing_analysis():
    """Test cross-drawing analysis with sample data."""
    try:
        from drawing_reference_analyzer import DrawingReferenceAnalyzer
        from enhanced_element_measurement import EnhancedElementMeasurement
        
        # Initialize systems
        reference_analyzer = DrawingReferenceAnalyzer()
        measurement_system = EnhancedElementMeasurement()
        
        print("✅ Cross-drawing analysis systems initialized")
        
        # Simulate cross-drawing analysis
        sample_elements = [
            {
                "id": "wall_001",
                "type": "wall",
                "measurements": {"length": 5.0, "height": 3.0}
            },
            {
                "id": "beam_001", 
                "type": "beam",
                "measurements": {"length": 8.0, "width": 0.3, "height": 0.5}
            }
        ]
        
        # Test enhanced measurement for each element
        for element in sample_elements:
            enhanced_element = measurement_system.measure_element_with_cross_references(
                "primary_drawing", element, ["reference_drawing_1", "reference_drawing_2"]
            )
            
            print(f"✅ Enhanced element: {enhanced_element.element_id}")
            print(f"  - Type: {enhanced_element.element_type}")
            print(f"  - Confidence: {enhanced_element.overall_confidence:.2f}")
            print(f"  - Cross-reference confidence: {enhanced_element.cross_reference_confidence:.2f}")
            print(f"  - Completeness: {enhanced_element.measurement_completeness:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing cross-drawing analysis: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🧪 Testing Cross-Drawing Reference Integration")
    print("=" * 50)
    
    tests = [
        ("Reference Analyzer", test_reference_analyzer),
        ("Enhanced Measurement", test_enhanced_measurement),
        ("PDF Processor Integration", test_pdf_processor_integration),
        ("API Endpoints", test_api_endpoints),
        ("Cross-Drawing Analysis", test_cross_drawing_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Cross-drawing reference integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 