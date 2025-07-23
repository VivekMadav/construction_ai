"""
Test script for Enhanced Inference System with OCR Mapping

This script tests the enhanced inference system that combines multi-head
detection with OCR text mapping for improved element classification.
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

def create_test_image_with_text(width: int = 800, height: int = 600) -> np.ndarray:
    """Create a test image with synthetic text and elements."""
    # Create white background
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw some geometric shapes (elements)
    # Room outline
    cv2.rectangle(image, (50, 50), (350, 250), (0, 0, 0), 2)
    
    # Door
    cv2.rectangle(image, (150, 200), (200, 250), (0, 0, 0), 2)
    
    # Window
    cv2.rectangle(image, (250, 100), (300, 150), (0, 0, 0), 2)
    
    # Column
    cv2.rectangle(image, (400, 100), (450, 300), (0, 0, 0), 3)
    
    # Beam
    cv2.rectangle(image, (100, 350), (700, 380), (0, 0, 0), 3)
    
    # Add text labels (simulated OCR targets)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2
    
    # Room label
    cv2.putText(image, "BEDROOM", (60, 80), font, font_scale, (0, 0, 0), thickness)
    
    # Door label
    cv2.putText(image, "DOOR", (160, 220), font, 0.6, (0, 0, 0), thickness)
    
    # Window label
    cv2.putText(image, "WINDOW", (260, 120), font, 0.6, (0, 0, 0), thickness)
    
    # Column label
    cv2.putText(image, "COLUMN", (410, 120), font, 0.6, (0, 0, 0), thickness)
    
    # Beam label
    cv2.putText(image, "BEAM", (120, 370), font, 0.6, (0, 0, 0), thickness)
    
    # Dimensions
    cv2.putText(image, "3000MM", (60, 30), font, 0.5, (0, 0, 0), thickness)
    cv2.putText(image, "2400MM", (60, 270), font, 0.5, (0, 0, 0), thickness)
    
    # Materials
    cv2.putText(image, "CONCRETE", (500, 50), font, 0.6, (0, 0, 0), thickness)
    cv2.putText(image, "STEEL", (500, 80), font, 0.6, (0, 0, 0), thickness)
    
    return image

def test_enhanced_inference_system():
    """Test the enhanced inference system."""
    print("Enhanced Inference System Test")
    print("=" * 50)
    
    try:
        # Import the enhanced inference system
        from models.enhanced_inference import EnhancedInferenceSystem, Discipline
        
        # Initialize the system
        print("Initializing Enhanced Inference System...")
        enhanced_system = EnhancedInferenceSystem()
        
        # Get system statistics
        stats = enhanced_system.get_system_statistics()
        print("\nSystem Statistics:")
        print(json.dumps(stats, indent=2))
        
        # Create test image
        print("\nCreating test image with synthetic text and elements...")
        test_image = create_test_image_with_text()
        
        # Save test image
        test_image_path = "test_enhanced_image.png"
        cv2.imwrite(test_image_path, test_image)
        print(f"Test image saved to: {test_image_path}")
        
        # Test enhanced detection for each discipline
        disciplines = [Discipline.ARCHITECTURAL, Discipline.STRUCTURAL, Discipline.CIVIL, Discipline.MEP]
        
        for discipline in disciplines:
            print(f"\n{'='*20} Testing {discipline.value.upper()} Detection {'='*20}")
            
            # Test enhanced detection
            results = enhanced_system.detect_elements_enhanced(
                test_image, discipline, use_ocr=True
            )
            
            print(f"Results for {discipline.value}:")
            print(f"  Total Elements: {results.get('total_elements', 0)}")
            print(f"  Total Texts: {results.get('total_texts', 0)}")
            print(f"  Processing Method: {results.get('processing_method', 'unknown')}")
            print(f"  Enhancement Applied: {results.get('enhancement_applied', False)}")
            
            # Show element details
            elements = results.get('elements', [])
            if elements:
                print(f"  Elements detected:")
                for i, element in enumerate(elements[:5]):  # Show first 5 elements
                    element_type = element.get('type', 'unknown')
                    confidence = element.get('confidence', 0)
                    text_mappings = element.get('text_mappings', [])
                    
                    print(f"    {i+1}. {element_type} (confidence: {confidence:.2f})")
                    if text_mappings:
                        print(f"       Text mappings: {len(text_mappings)}")
                        for mapping in text_mappings[:2]:  # Show first 2 mappings
                            text = mapping.get('text', '')
                            relationship = mapping.get('relationship', '')
                            print(f"         - '{text}' ({relationship})")
            
            # Show text analysis
            text_analysis = results.get('text_analysis', {})
            if text_analysis:
                print(f"  Text Analysis:")
                text_types = text_analysis.get('text_types', {})
                for text_type, count in text_types.items():
                    print(f"    {text_type}: {count}")
        
        # Test comprehensive analysis
        print(f"\n{'='*20} Testing Comprehensive Analysis {'='*20}")
        analysis_results = enhanced_system.analyze_drawing_content(
            test_image, Discipline.ARCHITECTURAL
        )
        
        print("Comprehensive Analysis Results:")
        print(analysis_results.get('summary', 'No summary available'))
        
        # Save results
        output_file = "enhanced_inference_results.json"
        enhanced_system.save_enhanced_results(analysis_results, output_file)
        print(f"\nResults saved to: {output_file}")
        
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all required modules are available.")
        return False
    except Exception as e:
        print(f"Error during testing: {e}")
        return False

def test_with_real_pdf():
    """Test with a real PDF from the backend uploads."""
    print(f"\n{'='*20} Testing with Real PDF {'='*20}")
    
    try:
        from models.enhanced_inference import EnhancedInferenceSystem, Discipline
        import fitz  # PyMuPDF
        
        # Initialize system
        enhanced_system = EnhancedInferenceSystem()
        
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
        
        # Test enhanced detection
        results = enhanced_system.detect_elements_enhanced(
            image_rgb, Discipline.ARCHITECTURAL, use_ocr=True
        )
        
        print(f"Real PDF Results:")
        print(f"  Total Elements: {results.get('total_elements', 0)}")
        print(f"  Total Texts: {results.get('total_texts', 0)}")
        print(f"  Processing Method: {results.get('processing_method', 'unknown')}")
        print(f"  Enhancement Applied: {results.get('enhancement_applied', False)}")
        
        # Show some extracted texts
        texts = results.get('extracted_texts', [])
        if texts:
            print(f"  Extracted Texts (first 5):")
            for i, text_info in enumerate(texts[:5]):
                text = text_info.get('text', '')
                text_type = text_info.get('text_type', 'unknown')
                confidence = text_info.get('confidence', 0)
                print(f"    {i+1}. '{text}' ({text_type}, confidence: {confidence:.2f})")
        
        # Save results
        output_file = "real_pdf_enhanced_results.json"
        enhanced_system.save_enhanced_results(results, output_file)
        print(f"Results saved to: {output_file}")
        
        pdf_document.close()
        return True
        
    except Exception as e:
        print(f"Error testing with real PDF: {e}")
        return False

def main():
    """Main test function."""
    print("Enhanced Inference System with OCR Mapping Test")
    print("=" * 60)
    
    # Test 1: Synthetic image
    success1 = test_enhanced_inference_system()
    
    # Test 2: Real PDF
    success2 = test_with_real_pdf()
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"  Synthetic Image Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"  Real PDF Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Enhanced inference system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 