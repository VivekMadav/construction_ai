#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_processor import PDFProcessor

def test_enhanced_analysis():
    """Test enhanced analysis with a simple drawing"""
    try:
        processor = PDFProcessor()
        
        # Test with a simple drawing
        drawing_id = 19
        pdf_path = "uploads/8/20250729_151014_4977_S_DE01_C01 TRUSS AND GIRDER SECTIONS A0.pdf"
        discipline = "structural"
        
        print(f"Testing enhanced analysis for drawing {drawing_id}")
        print(f"PDF path: {pdf_path}")
        print(f"Discipline: {discipline}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"ERROR: File does not exist: {pdf_path}")
            return
        
        # Test standard processing first
        print("\n1. Testing standard processing...")
        standard_results = processor.process_pdf_drawing(pdf_path, discipline)
        print(f"Standard results: {standard_results}")
        
        # Test enhanced analysis
        print("\n2. Testing enhanced analysis...")
        enhanced_results = processor.process_drawing_with_cross_references(
            drawing_id, pdf_path, discipline
        )
        print(f"Enhanced results: {enhanced_results}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_analysis() 