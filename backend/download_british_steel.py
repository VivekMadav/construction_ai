#!/usr/bin/env python3
"""
Script to download and import British Steel UK sections datasheet
"""

import requests
import tempfile
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.services.steel_database import SteelDatabaseService

def download_british_steel_datasheet():
    """Download the British Steel UK sections datasheet"""
    url = "https://britishsteel.co.uk/media/vv2la1v1/uk-sections-datasheets-100723.pdf"
    
    print("Downloading British Steel UK sections datasheet...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            
            tmp_file_path = tmp_file.name
            print(f"Downloaded to: {tmp_file_path}")
            return tmp_file_path
            
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def import_british_steel_database():
    """Import British Steel database into the system"""
    print("\n=== British Steel UK Sections Database Import ===")
    
    # Download the datasheet
    pdf_path = download_british_steel_datasheet()
    if not pdf_path:
        print("Failed to download British Steel datasheet")
        return False
    
    try:
        # Create database session
        db = SessionLocal()
        steel_service = SteelDatabaseService(db)
        
        # Import the database
        print("\nImporting British Steel sections...")
        result = steel_service.import_british_steel_database_from_pdf(pdf_path)
        
        if result["success"]:
            print(f"✅ Successfully imported {result['sections_added']} British Steel sections")
            print(f"📊 Total sections found: {result['total_sections_found']}")
            print(f"📝 Message: {result['message']}")
            
            # Show some sample sections
            print("\n📋 Sample imported sections:")
            sections = steel_service.get_all_steel_sections()
            for i, section in enumerate(sections[:5]):  # Show first 5
                print(f"  {i+1}. {section.section_name} ({section.section_type}) - {section.kg_per_meter} kg/m")
            
            if len(sections) > 5:
                print(f"  ... and {len(sections) - 5} more sections")
            
            return True
        else:
            print(f"❌ Import failed: {result['message']}")
            if 'error' in result:
                print(f"Error details: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error during import: {e}")
        return False
    finally:
        # Clean up temporary file
        try:
            os.unlink(pdf_path)
            print(f"🧹 Cleaned up temporary file: {pdf_path}")
        except:
            pass
        
        # Close database session
        try:
            db.close()
        except:
            pass

def test_british_steel_detection():
    """Test British Steel section detection"""
    print("\n=== Testing British Steel Section Detection ===")
    
    db = SessionLocal()
    steel_service = SteelDatabaseService(db)
    
    # Test text with British Steel sections
    test_texts = [
        "This drawing shows 127 x 76 x 13 beams and 305 x 102 x 25 columns",
        "Use 356 x 171 x 57 UB for main beams",
        "Columns shall be 203 x 203 x 86 UC",
        "Bracing members: 200 x 100 x 10 UA"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text}")
        detected = steel_service.detect_steel_sections_in_text(text)
        
        if detected:
            for section in detected:
                print(f"  ✅ Detected: {section['section_name']} ({section['section_type']}) - {section['kg_per_meter']} kg/m")
        else:
            print("  ❌ No sections detected")
    
    db.close()

if __name__ == "__main__":
    print("🏗️  British Steel UK Sections Database Setup")
    print("=" * 50)
    
    # Import the database
    success = import_british_steel_database()
    
    if success:
        # Test detection
        test_british_steel_detection()
        
        print("\n🎉 British Steel database setup complete!")
        print("\nYou can now:")
        print("1. Upload structural drawings with British Steel sections")
        print("2. The system will detect sections like '127 x 76 x 13'")
        print("3. Calculate mass automatically using kg/m values")
        print("4. View all imported sections in the web interface")
    else:
        print("\n❌ Setup failed. Please check the error messages above.") 