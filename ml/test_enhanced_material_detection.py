"""
Test Enhanced Material Detection System
Demonstrates text scanning and material identification for construction drawings
"""

import sys
from pathlib import Path
import cv2
import numpy as np
import json
import logging

# Add the ML directory to the path
sys.path.append(str(Path(__file__).parent))

from enhanced_material_detection import EnhancedMaterialDetector
from material_text_analyzer import MaterialTextAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_material_text_analysis():
    """Test the material text analyzer"""
    print("🧪 Testing Material Text Analysis")
    print("=" * 50)
    
    analyzer = MaterialTextAnalyzer()
    
    # Test with a sample image
    test_image_path = "../backend/uploads/1/page_1.png"
    
    if Path(test_image_path).exists():
        print(f"📄 Analyzing image: {test_image_path}")
        
        # Analyze materials in the drawing
        results = analyzer.analyze_drawing_materials(test_image_path)
        
        print(f"\n📊 Analysis Results:")
        print(f"  Total text regions: {results['total_regions']}")
        print(f"  Material regions: {results['material_regions']}")
        print(f"  Material distribution: {results['material_distribution']}")
        
        print(f"\n🔍 Detected Material Text:")
        for material_text in results['material_texts']:
            print(f"  • {material_text.material_type.upper()}: {material_text.text}")
            print(f"    Confidence: {material_text.confidence:.2f}")
            print(f"    Position: {material_text.position}")
        
        return results
    else:
        print(f"❌ Test image not found: {test_image_path}")
        return None

def test_enhanced_material_detection():
    """Test the enhanced material detection system"""
    print("\n🧪 Testing Enhanced Material Detection")
    print("=" * 50)
    
    detector = EnhancedMaterialDetector()
    
    # Test with a sample image
    test_image_path = "../backend/uploads/1/page_1.png"
    
    if Path(test_image_path).exists():
        print(f"📄 Processing image: {test_image_path}")
        
        # Detect elements with materials
        enhanced_elements = detector.detect_elements_with_materials(test_image_path, "structural")
        
        print(f"\n🏗️  Detected Elements with Materials:")
        print(f"  Total elements: {len(enhanced_elements)}")
        
        # Group by material
        material_groups = {}
        for element in enhanced_elements:
            material = element.material
            if material not in material_groups:
                material_groups[material] = []
            material_groups[material].append(element)
        
        for material, elements in material_groups.items():
            print(f"\n  📦 {material.upper()} Elements ({len(elements)}):")
            for element in elements:
                print(f"    • {element.element_type}")
                print(f"      Confidence: {element.confidence:.2f}")
                print(f"      Material Confidence: {element.material_confidence:.2f}")
                print(f"      Area: {element.area:.0f}")
                if element.text_references:
                    print(f"      Text References: {element.text_references}")
        
        return enhanced_elements
    else:
        print(f"❌ Test image not found: {test_image_path}")
        return None

def test_material_identification_accuracy():
    """Test the accuracy of material identification"""
    print("\n🧪 Testing Material Identification Accuracy")
    print("=" * 50)
    
    detector = EnhancedMaterialDetector()
    
    # Test with different image types
    test_images = [
        "../backend/uploads/1/page_1.png",
        "../backend/uploads/page_1.png"
    ]
    
    results = {}
    
    for image_path in test_images:
        if Path(image_path).exists():
            print(f"\n📄 Testing: {image_path}")
            
            # Test material text analysis
            analyzer = MaterialTextAnalyzer()
            text_results = analyzer.analyze_drawing_materials(image_path)
            
            # Test enhanced detection
            enhanced_elements = detector.detect_elements_with_materials(image_path, "structural")
            
            # Calculate accuracy metrics
            total_elements = len(enhanced_elements)
            high_confidence_elements = len([e for e in enhanced_elements if e.material_confidence > 0.7])
            material_variety = len(set([e.material for e in enhanced_elements]))
            
            accuracy_metrics = {
                'total_elements': total_elements,
                'high_confidence_elements': high_confidence_elements,
                'confidence_rate': high_confidence_elements / total_elements if total_elements > 0 else 0,
                'material_variety': material_variety,
                'text_regions': text_results['total_regions'],
                'material_text_regions': text_results['material_regions']
            }
            
            results[image_path] = accuracy_metrics
            
            print(f"  📊 Accuracy Metrics:")
            print(f"    Total Elements: {total_elements}")
            print(f"    High Confidence: {high_confidence_elements}")
            print(f"    Confidence Rate: {accuracy_metrics['confidence_rate']:.2%}")
            print(f"    Material Variety: {material_variety}")
            print(f"    Text Regions: {text_results['total_regions']}")
            print(f"    Material Text: {text_results['material_regions']}")
    
    return results

def generate_material_detection_report():
    """Generate a comprehensive material detection report"""
    print("\n📋 Generating Material Detection Report")
    print("=" * 50)
    
    # Run all tests
    text_analysis_results = test_material_text_analysis()
    enhanced_detection_results = test_enhanced_material_detection()
    accuracy_results = test_material_identification_accuracy()
    
    # Generate report
    report = {
        'text_analysis': text_analysis_results,
        'enhanced_detection': enhanced_detection_results,
        'accuracy_metrics': accuracy_results,
        'summary': {
            'total_material_texts': len(text_analysis_results['material_texts']) if text_analysis_results else 0,
            'total_enhanced_elements': len(enhanced_detection_results) if enhanced_detection_results else 0,
            'average_confidence': np.mean([e.material_confidence for e in enhanced_detection_results]) if enhanced_detection_results else 0
        }
    }
    
    # Save report
    report_path = "ml/enhanced_material_detection_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ Report saved to: {report_path}")
    
    # Print summary
    print(f"\n📈 Summary:")
    print(f"  Material Text Regions: {report['summary']['total_material_texts']}")
    print(f"  Enhanced Elements: {report['summary']['total_enhanced_elements']}")
    print(f"  Average Material Confidence: {report['summary']['average_confidence']:.2f}")
    
    return report

def demonstrate_material_focus():
    """Demonstrate the focus on Timber, Steel, and Concrete materials"""
    print("\n🎯 Demonstrating Material Focus (Timber, Steel, Concrete)")
    print("=" * 60)
    
    detector = EnhancedMaterialDetector()
    
    # Test with structural drawing
    test_image_path = "../backend/uploads/1/page_1.png"
    
    if Path(test_image_path).exists():
        print(f"📄 Analyzing structural drawing: {test_image_path}")
        
        # Detect elements with materials
        enhanced_elements = detector.detect_elements_with_materials(test_image_path, "structural")
        
        # Focus on the three main materials
        focus_materials = ['timber', 'steel', 'concrete']
        
        print(f"\n🏗️  Material-Specific Analysis:")
        
        for material in focus_materials:
            material_elements = [e for e in enhanced_elements if e.material.lower() == material]
            
            print(f"\n  📦 {material.upper()} Elements ({len(material_elements)}):")
            
            if material_elements:
                # Group by element type
                element_types = {}
                for element in material_elements:
                    if element.element_type not in element_types:
                        element_types[element.element_type] = []
                    element_types[element.element_type].append(element)
                
                for element_type, elements in element_types.items():
                    avg_confidence = np.mean([e.material_confidence for e in elements])
                    total_area = sum([e.area for e in elements])
                    
                    print(f"    • {element_type.title()}: {len(elements)} items")
                    print(f"      Avg Confidence: {avg_confidence:.2f}")
                    print(f"      Total Area: {total_area:.0f} pixels")
                    
                    # Show text references if available
                    text_refs = set()
                    for element in elements:
                        text_refs.update(element.text_references)
                    
                    if text_refs:
                        print(f"      Text References: {list(text_refs)}")
            else:
                print(f"    • No {material} elements detected")
        
        # Show detection confidence distribution
        print(f"\n📊 Detection Confidence Distribution:")
        confidence_ranges = {
            'High (>0.8)': len([e for e in enhanced_elements if e.material_confidence > 0.8]),
            'Medium (0.6-0.8)': len([e for e in enhanced_elements if 0.6 <= e.material_confidence <= 0.8]),
            'Low (<0.6)': len([e for e in enhanced_elements if e.material_confidence < 0.6])
        }
        
        for range_name, count in confidence_ranges.items():
            percentage = (count / len(enhanced_elements)) * 100 if enhanced_elements else 0
            print(f"  {range_name}: {count} elements ({percentage:.1f}%)")
    
    else:
        print(f"❌ Test image not found: {test_image_path}")

if __name__ == "__main__":
    print("🚀 Enhanced Material Detection System Test")
    print("=" * 60)
    
    # Run comprehensive tests
    demonstrate_material_focus()
    generate_material_detection_report()
    
    print("\n✅ All tests completed!")
    print("\n🎯 Key Features Demonstrated:")
    print("  • Text scanning for material identification")
    print("  • Enhanced element detection with materials")
    print("  • Focus on Timber, Steel, and Concrete")
    print("  • Confidence scoring for material detection")
    print("  • Spatial association of text with elements") 