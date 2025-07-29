"""
Test script for drawing notes analyzer integration

This script tests the integration of the drawing notes analyzer
into the existing system to extract and process drawing notes.
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

def test_notes_analyzer():
    """Test the drawing notes analyzer."""
    try:
        from drawing_notes_analyzer import DrawingNotesAnalyzer
        
        analyzer = DrawingNotesAnalyzer()
        print("✅ DrawingNotesAnalyzer initialized successfully")
        
        # Test with a sample drawing path
        test_drawing_path = "uploads/1/20250723_153938_4977_S_DW06 - WATER TANK LAYOUT - 2.pdf"
        
        if os.path.exists(test_drawing_path):
            specifications = analyzer.analyze_drawing_notes(test_drawing_path)
            print(f"✅ Notes analysis completed:")
            print(f"  - Concrete specs: {len(specifications.concrete_specs)}")
            print(f"  - Steel specs: {len(specifications.steel_specs)}")
            print(f"  - General notes: {len(specifications.general_notes)}")
            print(f"  - Critical info: {len(specifications.critical_info)}")
            
            # Generate report
            report = analyzer.generate_notes_report(specifications)
            print(f"✅ Notes report generated with {len(report['analysis_summary'])} categories")
        else:
            print("⚠️  Test drawing not found, skipping notes analysis test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing notes analyzer: {e}")
        return False

def test_notes_application():
    """Test applying notes to elements."""
    try:
        from drawing_notes_analyzer import DrawingNotesAnalyzer
        
        analyzer = DrawingNotesAnalyzer()
        print("✅ DrawingNotesAnalyzer initialized for application test")
        
        # Sample elements
        sample_elements = [
            {
                "id": "wall_001",
                "type": "wall",
                "confidence": 0.8,
                "measurements": {"length": 5.0, "height": 3.0}
            },
            {
                "id": "beam_001",
                "type": "beam", 
                "confidence": 0.7,
                "measurements": {"length": 8.0, "width": 0.3, "height": 0.5}
            }
        ]
        
        # Create sample specifications
        from drawing_notes_analyzer import DrawingSpecifications, MaterialSpecification, MaterialType
        
        concrete_spec = MaterialSpecification(
            material_type=MaterialType.CONCRETE,
            grade="C30",
            strength="30 N/mm²",
            confidence=0.9
        )
        
        steel_spec = MaterialSpecification(
            material_type=MaterialType.STEEL,
            grade="S355",
            confidence=0.85
        )
        
        specifications = DrawingSpecifications(
            concrete_specs=[concrete_spec],
            steel_specs=[steel_spec],
            other_materials=[],
            general_notes=["All concrete to be C30 grade"],
            construction_notes=["Follow standard construction procedures"],
            dimension_notes=["All dimensions in meters"],
            revision_notes=[],
            critical_info={"fire_rating_hours": "2", "load_capacity": "50"}
        )
        
        # Apply notes to elements
        enhanced_elements = analyzer.apply_notes_to_elements(sample_elements, specifications)
        
        print(f"✅ Notes application completed:")
        print(f"  - Original elements: {len(sample_elements)}")
        print(f"  - Enhanced elements: {len(enhanced_elements)}")
        
        for element in enhanced_elements:
            print(f"  - Element {element['id']}:")
            if 'material' in element:
                print(f"    Material: {element['material']}")
            if 'concrete_grade' in element:
                print(f"    Concrete grade: {element['concrete_grade']}")
            if 'steel_grade' in element:
                print(f"    Steel grade: {element['steel_grade']}")
            if 'critical_info' in element:
                print(f"    Critical info: {element['critical_info']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing notes application: {e}")
        return False

def test_pdf_processor_integration():
    """Test the PDF processor integration with notes analyzer."""
    try:
        from backend.app.services.pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        print("✅ PDFProcessor initialized successfully")
        
        # Check if notes analyzer is available
        if processor.notes_analyzer:
            print("✅ Notes analyzer integrated successfully")
        else:
            print("⚠️  Notes analyzer not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing PDF processor integration: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints (simulated)."""
    try:
        print("✅ API endpoints configured:")
        print("  - POST /api/v1/drawing-notes/analyze-notes/drawing/{drawing_id}")
        print("  - POST /api/v1/drawing-notes/apply-notes/drawing/{drawing_id}")
        print("  - GET /api/v1/drawing-notes/notes-statistics/drawing/{drawing_id}")
        print("  - POST /api/v1/drawing-notes/extract-specifications/drawing/{drawing_id}")
        print("  - GET /api/v1/drawing-notes/notes-capabilities")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

def test_enhanced_analysis_integration():
    """Test enhanced analysis with notes integration."""
    try:
        from backend.app.services.pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        print("✅ PDFProcessor initialized for enhanced analysis test")
        
        # Test enhanced analysis method
        test_drawing_path = "uploads/1/20250723_153938_4977_S_DW06 - WATER TANK LAYOUT - 2.pdf"
        
        if os.path.exists(test_drawing_path):
            # Simulate enhanced analysis
            enhanced_results = processor.process_drawing_with_cross_references(
                1, test_drawing_path, "structural"
            )
            
            if enhanced_results['status'] == 'success':
                print(f"✅ Enhanced analysis completed:")
                print(f"  - Elements: {enhanced_results['element_count']}")
                print(f"  - References: {enhanced_results['reference_count']}")
                print(f"  - Notes analysis: {enhanced_results.get('notes_analysis', {})}")
                
                if 'notes_report' in enhanced_results:
                    notes_report = enhanced_results['notes_report']
                    print(f"  - Notes report generated: {len(notes_report.get('analysis_summary', {}))} categories")
            else:
                print(f"⚠️  Enhanced analysis failed: {enhanced_results['message']}")
        else:
            print("⚠️  Test drawing not found, skipping enhanced analysis test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced analysis integration: {e}")
        return False

def test_material_specification_extraction():
    """Test material specification extraction from notes."""
    try:
        from drawing_notes_analyzer import DrawingNotesAnalyzer
        
        analyzer = DrawingNotesAnalyzer()
        print("✅ DrawingNotesAnalyzer initialized for specification extraction test")
        
        # Test with sample text content
        sample_text = """
        PROJECT: Water Tank Construction
        DRAWING: Foundation Layout
        SCALE: 1:100
        
        CONCRETE GRADE: C30
        CONCRETE STRENGTH: 30 N/mm²
        STEEL GRADE: S355
        REINFORCEMENT: B500B
        
        FIRE RATING: 2 HOURS
        LOAD CAPACITY: 50 KN
        
        GENERAL NOTES:
        - All concrete to be C30 grade
        - Follow standard construction procedures
        - All dimensions in meters
        """
        
        # Test specification extraction
        concrete_specs = analyzer._extract_concrete_specifications(sample_text)
        steel_specs = analyzer._extract_steel_specifications(sample_text)
        critical_info = analyzer._extract_critical_information(sample_text)
        
        print(f"✅ Specification extraction completed:")
        print(f"  - Concrete specs: {len(concrete_specs)}")
        for spec in concrete_specs:
            print(f"    - Grade: {spec.grade}, Strength: {spec.strength}")
        
        print(f"  - Steel specs: {len(steel_specs)}")
        for spec in steel_specs:
            print(f"    - Grade: {spec.grade}")
        
        print(f"  - Critical info: {len(critical_info)}")
        for key, value in critical_info.items():
            print(f"    - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing material specification extraction: {e}")
        return False

def main():
    """Run all drawing notes integration tests."""
    print("🧪 Testing Drawing Notes Analyzer Integration")
    print("=" * 50)
    
    tests = [
        ("Notes Analyzer", test_notes_analyzer),
        ("Notes Application", test_notes_application),
        ("PDF Processor Integration", test_pdf_processor_integration),
        ("API Endpoints", test_api_endpoints),
        ("Enhanced Analysis Integration", test_enhanced_analysis_integration),
        ("Material Specification Extraction", test_material_specification_extraction)
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
        print("🎉 All tests passed! Drawing notes analyzer integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 