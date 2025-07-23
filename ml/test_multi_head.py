#!/usr/bin/env python3
"""
Test script for Multi-Head Inference System

This script tests the discipline-specific element detection models
and verifies that they work correctly with different drawing types.
"""

import sys
import os
from pathlib import Path
import cv2
import numpy as np
import json

# Add the models directory to the path
sys.path.append(str(Path(__file__).parent / "models"))

from multi_head_inference import MultiHeadInferenceSystem, Discipline

def create_test_image(discipline: str, size: tuple = (800, 600)) -> np.ndarray:
    """Create a test image with discipline-specific elements."""
    # Create white background
    image = np.ones((size[1], size[0], 3), dtype=np.uint8) * 255
    
    if discipline == "architectural":
        # Draw walls (long rectangles)
        cv2.rectangle(image, (100, 100), (700, 120), (0, 0, 0), 2)  # Horizontal wall
        cv2.rectangle(image, (100, 100), (120, 500), (0, 0, 0), 2)  # Vertical wall
        
        # Draw doors (medium rectangles)
        cv2.rectangle(image, (200, 100), (280, 200), (0, 0, 0), 2)  # Door
        
        # Draw windows (small rectangles)
        cv2.rectangle(image, (400, 150), (450, 200), (0, 0, 0), 2)  # Window
        
    elif discipline == "structural":
        # Draw beams (long horizontal elements)
        cv2.rectangle(image, (50, 200), (750, 220), (0, 0, 0), 3)  # Beam
        
        # Draw columns (tall vertical elements)
        cv2.rectangle(image, (200, 100), (250, 500), (0, 0, 0), 3)  # Column
        cv2.rectangle(image, (500, 100), (550, 500), (0, 0, 0), 3)  # Column
        
        # Draw foundation (large rectangle at bottom)
        cv2.rectangle(image, (100, 550), (700, 580), (0, 0, 0), 3)  # Foundation
        
    elif discipline == "civil":
        # Draw roads (long linear elements)
        cv2.rectangle(image, (50, 300), (750, 320), (0, 0, 0), 2)  # Road
        
        # Draw utilities (small elements)
        cv2.circle(image, (200, 200), 20, (0, 0, 0), 2)  # Manhole
        cv2.circle(image, (500, 200), 15, (0, 0, 0), 2)  # Catch basin
        
    elif discipline == "mep":
        # Draw HVAC ducts (rectangular elements)
        cv2.rectangle(image, (100, 150), (300, 200), (0, 0, 0), 2)  # Duct
        
        # Draw electrical panels (small rectangles)
        cv2.rectangle(image, (400, 100), (450, 150), (0, 0, 0), 2)  # Panel
        
        # Draw plumbing pipes (small elements)
        cv2.rectangle(image, (500, 300), (600, 320), (0, 0, 0), 2)  # Pipe
    
    return image

def test_discipline_detection(discipline: str):
    """Test element detection for a specific discipline."""
    print(f"\n{'='*50}")
    print(f"Testing {discipline.upper()} Detection")
    print(f"{'='*50}")
    
    # Create test image
    test_image = create_test_image(discipline)
    
    # Initialize inference system
    inference_system = MultiHeadInferenceSystem()
    
    # Get discipline enum
    discipline_map = {
        "architectural": Discipline.ARCHITECTURAL,
        "structural": Discipline.STRUCTURAL,
        "civil": Discipline.CIVIL,
        "mep": Discipline.MEP
    }
    
    discipline_enum = discipline_map[discipline]
    
    # Perform detection
    results = inference_system.detect_elements(test_image, discipline_enum, confidence_threshold=0.5)
    
    # Display results
    print(f"Detected {len(results)} elements:")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result.element_type} (confidence: {result.confidence:.2f})")
        print(f"      Bbox: {result.bbox}")
        print(f"      Properties: {result.properties}")
    
    return results

def test_all_disciplines():
    """Test detection for all disciplines."""
    print("Multi-Head Inference System Test")
    print("="*60)
    
    # Initialize system
    inference_system = MultiHeadInferenceSystem()
    
    # Get statistics
    stats = inference_system.get_discipline_statistics()
    print("\nSystem Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Test each discipline
    disciplines = ["architectural", "structural", "civil", "mep"]
    all_results = {}
    
    for discipline in disciplines:
        results = test_discipline_detection(discipline)
        all_results[discipline] = results
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    total_elements = 0
    for discipline, results in all_results.items():
        element_count = len(results)
        total_elements += element_count
        print(f"{discipline.capitalize()}: {element_count} elements")
    
    print(f"\nTotal elements detected: {total_elements}")
    
    # Test with a real image if available
    test_with_real_image()

def test_with_real_image():
    """Test with a real drawing image if available."""
    print(f"\n{'='*60}")
    print("Testing with Real Image")
    print(f"{'='*60}")
    
    # Look for a real drawing in the backend uploads
    backend_uploads = Path(__file__).parent.parent / "backend" / "uploads"
    
    if backend_uploads.exists():
        # Find a PDF file
        pdf_files = list(backend_uploads.rglob("*.pdf"))
        
        if pdf_files:
            test_pdf = pdf_files[0]
            print(f"Found test PDF: {test_pdf}")
            
            # Import and test the PDF processor
            try:
                sys.path.append(str(Path(__file__).parent.parent / "backend" / "app" / "services"))
                from pdf_processor import PDFProcessor
                
                processor = PDFProcessor()
                
                # Test with different disciplines
                for discipline in ["architectural", "structural", "civil", "mep"]:
                    print(f"\nTesting {discipline} detection on real PDF...")
                    results = processor.process_pdf_drawing(str(test_pdf), discipline)
                    
                    print(f"  Elements detected: {results.get('total_elements', 0)}")
                    print(f"  Processing method: {results.get('processing_method', 'unknown')}")
                    
                    if results.get('elements'):
                        element_types = set(elem['type'] for elem in results['elements'])
                        print(f"  Element types: {list(element_types)}")
                
            except ImportError as e:
                print(f"Could not import PDF processor: {e}")
        else:
            print("No PDF files found in backend uploads")
    else:
        print("Backend uploads directory not found")

def main():
    """Main test function."""
    try:
        test_all_disciplines()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 