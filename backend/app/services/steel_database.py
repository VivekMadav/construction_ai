import logging
import json
import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.models import SteelSection, SteelElement
from ..models.schemas import SteelSectionCreate, SteelElementCreate
import cv2
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class SteelDatabaseService:
    """Service for managing steel section database and detection"""
    
    def __init__(self, db: Session):
        self.db = db
        # Updated patterns for British Steel UK sections
        self.section_patterns = {
            'UB': r'(\d{3})\s*x\s*(\d{2,3})\s*x\s*(\d{1,2})',  # 305 x 102 x 25
            'UC': r'(\d{3})\s*x\s*(\d{2,3})\s*x\s*(\d{1,2})',  # 305 x 305 x 118
            'UA': r'(\d{2,3})\s*x\s*(\d{2,3})\s*x\s*(\d{1,2})',  # 200 x 100 x 10
            'PIPE': r'PIPE\s*(\d{1,3})',  # PIPE 100
            'TUBE': r'TUBE\s*(\d{1,3})x(\d{1,3})',  # TUBE 100x100x5
        }
        
        # British Steel section type mappings
        self.british_steel_mappings = {
            'UB': 'Universal Beam',
            'UC': 'Universal Column', 
            'UA': 'Unequal Angle',
            'PIPE': 'Pipe',
            'TUBE': 'Tube'
        }
    
    def add_steel_section(self, section_data: SteelSectionCreate) -> SteelSection:
        """Add a new steel section to the database"""
        db_section = SteelSection(**section_data.dict())
        self.db.add(db_section)
        self.db.commit()
        self.db.refresh(db_section)
        logger.info(f"Added steel section: {section_data.section_name}")
        return db_section
    
    def get_steel_section(self, section_name: str) -> Optional[SteelSection]:
        """Get steel section by name"""
        return self.db.query(SteelSection).filter(SteelSection.section_name == section_name).first()
    
    def get_all_steel_sections(self) -> List[SteelSection]:
        """Get all steel sections"""
        return self.db.query(SteelSection).all()
    
    def search_steel_sections(self, query: str) -> List[SteelSection]:
        """Search steel sections by name or type"""
        return self.db.query(SteelSection).filter(
            SteelSection.section_name.ilike(f"%{query}%")
        ).all()
    
    def detect_steel_sections_in_text(self, text: str) -> List[Dict]:
        """Detect steel section references in text including hollow sections"""
        detected_sections = []
        
        # All steel section patterns including hollow sections
        steel_patterns = {
            # British Steel sections
            'UB': r'(\d{3})\s*x\s*(\d{2,3})\s*x\s*(\d{1,2})',  # 305 x 102 x 25
            'UC': r'(\d{3})\s*x\s*(\d{2,3})\s*x\s*(\d{1,2})',  # 305 x 305 x 118
            'UA': r'(\d{2,3})\s*x\s*(\d{2,3})\s*x\s*(\d{1,2})',  # 200 x 100 x 10
            
            # Hollow sections with prefixes
            'CHS': r'CHS\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)',  # CHS 21.3 x 3.0
            'RHS': r'RHS\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)',  # RHS 50 x 30 x 3.2
            'SHS': r'SHS\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)',  # SHS 20 x 20 x 2.0
            
            # Hollow sections without prefixes (need to be detected by context)
            'CHS_IMPLICIT': r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)(?!\s*x)',  # 21.3 x 3.0 (two dimensions)
            'RHS_IMPLICIT': r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)',  # 50 x 30 x 3.2 (three dimensions)
        }
        
        for section_type, pattern in steel_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if section_type in ['CHS', 'CHS_IMPLICIT']:
                    # Circular Hollow Section
                    diameter = match.group(1)
                    thickness = match.group(2)
                    section_name = f"CHS {diameter} x {thickness}"
                    
                    # Search for this section in database
                    db_section = self.get_steel_section(section_name)
                    
                    if db_section:
                        detected_sections.append({
                            'section_name': section_name,
                            'section_type': 'CHS',
                            'kg_per_meter': db_section.kg_per_meter,
                            'confidence': 0.9,
                            'text_match': match.group(0),
                            'position': match.span(),
                            'depth_mm': db_section.depth_mm,
                            'width_mm': db_section.width_mm,
                            'thickness_mm': db_section.thickness_mm
                        })
                
                elif section_type in ['RHS', 'RHS_IMPLICIT']:
                    # Rectangular or Square Hollow Section
                    width = match.group(1)
                    height = match.group(2)
                    thickness = match.group(3)
                    
                    # Determine if it's RHS or SHS based on dimensions
                    if abs(float(width) - float(height)) < 5:  # Similar dimensions suggest SHS
                        section_type_detected = 'SHS'
                        section_name = f"SHS {width} x {height} x {thickness}"
                    else:
                        section_type_detected = 'RHS'
                        section_name = f"RHS {width} x {height} x {thickness}"
                    
                    # Search for this section in database
                    db_section = self.get_steel_section(section_name)
                    
                    if db_section:
                        detected_sections.append({
                            'section_name': section_name,
                            'section_type': section_type_detected,
                            'kg_per_meter': db_section.kg_per_meter,
                            'confidence': 0.9,
                            'text_match': match.group(0),
                            'position': match.span(),
                            'depth_mm': db_section.depth_mm,
                            'width_mm': db_section.width_mm,
                            'thickness_mm': db_section.thickness_mm
                        })
                
                else:
                    # British Steel sections (UB, UC, UA)
                    depth = match.group(1)
                    width = match.group(2)
                    thickness = match.group(3)
                    section_name = f"{depth} x {width} x {thickness}"
                    
                    # Search for this section in database
                    db_section = self.get_steel_section(section_name)
                    
                    if db_section:
                        detected_sections.append({
                            'section_name': section_name,
                            'section_type': section_type,
                            'kg_per_meter': db_section.kg_per_meter,
                            'confidence': 0.9,
                            'text_match': match.group(0),
                            'position': match.span(),
                            'depth_mm': db_section.depth_mm,
                            'width_mm': db_section.width_mm,
                            'thickness_mm': db_section.thickness_mm
                        })
                    else:
                        # Try to find similar sections
                        similar_sections = self.search_steel_sections(section_name)
                        if similar_sections:
                            detected_sections.append({
                                'section_name': section_name,
                                'section_type': section_type,
                                'kg_per_meter': similar_sections[0].kg_per_meter,
                                'confidence': 0.7,
                                'text_match': match.group(0),
                                'position': match.span(),
                                'note': f"Similar to {similar_sections[0].section_name}"
                            })
        
        return detected_sections
    
    def calculate_steel_mass(self, section_name: str, length_mm: float) -> Optional[float]:
        """Calculate mass of steel section based on length"""
        section = self.get_steel_section(section_name)
        if section:
            length_m = length_mm / 1000.0  # Convert mm to meters
            mass_kg = section.kg_per_meter * length_m
            return mass_kg
        return None
    
    def detect_steel_elements_in_drawing(self, image_path: str, drawing_id: int) -> List[SteelElement]:
        """Detect steel elements in a drawing"""
        try:
            # Extract text from PDF using PyMuPDF
            import fitz  # PyMuPDF
            doc = fitz.open(image_path)
            text_content = ""
            
            for page in doc:
                text_content += page.get_text()
            
            doc.close()
            
            logger.info(f"Extracted text from drawing {drawing_id}: {len(text_content)} characters")
            
            # Detect steel sections in text
            detected_sections = self.detect_steel_sections_in_text(text_content)
            logger.info(f"Detected {len(detected_sections)} steel sections in text")
            
            steel_elements = []
            for section in detected_sections:
                # For now, use a default length of 6000mm (6m) - this should be improved
                length_mm = 6000.0
                
                # Calculate mass
                mass_kg = self.calculate_steel_mass(section['section_name'], length_mm)
                
                # Create steel element
                steel_element_data = SteelElementCreate(
                    drawing_id=drawing_id,
                    element_type=self._classify_steel_element_type(section['section_type']),
                    section_name=section['section_name'],
                    section_type=section['section_type'],
                    length_mm=length_mm,
                    mass_kg=mass_kg,
                    confidence_score=section['confidence'],
                    bbox=json.dumps([0, 0, 100, 100]),  # Default bbox
                    text_references=json.dumps([section['text_match']]),
                    properties=json.dumps(section)
                )
                
                db_steel_element = SteelElement(**steel_element_data.dict())
                self.db.add(db_steel_element)
                steel_elements.append(db_steel_element)
            
            self.db.commit()
            logger.info(f"Detected {len(steel_elements)} steel elements in drawing {drawing_id}")
            return steel_elements
            
        except Exception as e:
            logger.error(f"Error detecting steel elements in drawing {drawing_id}: {e}")
            return []
    
    def _extract_text_regions(self, image: np.ndarray) -> List[Dict]:
        """Extract text regions from image using OCR or fallback"""
        # This is a simplified version - in production you'd use PaddleOCR
        # For now, we'll return empty list and rely on text passed from other systems
        return []
    
    def _estimate_element_length(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> float:
        """Estimate element length based on visual analysis"""
        # This is a simplified estimation
        # In production, you'd use more sophisticated computer vision
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        # Simple heuristic: assume 1 pixel = 1mm at drawing scale
        # This would need calibration based on drawing scale
        length_pixels = max(width, height)
        length_mm = length_pixels * 1.0  # Scale factor would be determined by drawing scale
        
        return length_mm
    
    def _classify_steel_element_type(self, section_type: str) -> str:
        """Classify steel element type based on section type"""
        type_mapping = {
            'UB': 'beam',
            'UC': 'column',
            'UA': 'bracing',
            'PIPE': 'column',
            'TUBE': 'column',
            'CHS': 'column',  # Circular Hollow Sections are typically used as columns
            'RHS': 'beam',    # Rectangular Hollow Sections are often used as beams
            'SHS': 'column'   # Square Hollow Sections are typically used as columns
        }
        return type_mapping.get(section_type, 'beam')
    
    def import_british_steel_database_from_pdf(self, pdf_path: str) -> Dict:
        """Import British Steel UK sections database from PDF"""
        logger.info(f"Importing British Steel database from PDF: {pdf_path}")
        
        try:
            # Extract text from PDF
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            text_content = ""
            
            for page in doc:
                text_content += page.get_text()
            
            doc.close()
            
            # Parse British Steel sections from text
            imported_sections = self._parse_british_steel_sections_from_text(text_content)
            
            # Add to database
            added_count = 0
            for section_data in imported_sections:
                try:
                    self.add_steel_section(SteelSectionCreate(**section_data))
                    added_count += 1
                except Exception as e:
                    logger.error(f"Failed to add section {section_data.get('section_name', 'unknown')}: {e}")
            
            return {
                "success": True,
                "total_sections_found": len(imported_sections),
                "sections_added": added_count,
                "message": f"Successfully imported {added_count} British Steel sections"
            }
            
        except Exception as e:
            logger.error(f"Failed to import British Steel database: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to import British Steel database"
            }
    
    def _parse_british_steel_sections_from_text(self, text: str) -> List[Dict]:
        """Parse British Steel sections from text content"""
        sections = []
        
        # Split text into lines
        lines = text.split('\n')
        
        current_section_type = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section type headers
            if 'Universal beams (UB)' in line or 'Universal Beams' in line or 'Universal beams' in line:
                current_section_type = 'UB'
                print(f"DEBUG: Found UB section header: {line}")
                continue
            elif 'Universal columns (UC)' in line or 'Universal Columns' in line or 'Universal columns' in line:
                current_section_type = 'UC'
                print(f"DEBUG: Found UC section header: {line}")
                continue
            elif 'Unequal angles (UA)' in line or 'Unequal Angles' in line or 'Unequal angles' in line:
                current_section_type = 'UA'
                print(f"DEBUG: Found UA section header: {line}")
                continue
            
            # Parse section data lines
            if current_section_type:
                section_data = self._parse_british_steel_line(line, current_section_type)
                if section_data:
                    sections.append(section_data)
                    print(f"DEBUG: Parsed section: {section_data['section_name']}")
        
        return sections
    
    def _parse_british_steel_line(self, line: str, section_type: str) -> Optional[Dict]:
        """Parse a single British Steel section line"""
        # British Steel format examples:
        # "127 x 76 x 13 | 13.0 | 127.0 | 76.0 | 4.0 | 7.6 | 7.6 | 96.6 | 5.00 | 24.2 | 473 | 56 | 5.35 | 1.84"
        # "127 x 76 x 13 13.0 127.0 76.0 4.0 7.6 7.6 96.6 5.00 24.2 473 56 5.35 1.84"
        
        # Clean the line and try different parsing approaches
        line = line.strip()
        
        # Approach 1: Look for dimension pattern at start of line
        dimension_match = re.match(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', line)
        if dimension_match:
            depth = int(dimension_match.group(1))
            width = int(dimension_match.group(2))
            thickness = int(dimension_match.group(3))
            
            # Extract kg/m from the line - look for the first reasonable number after dimensions
            kg_per_meter = self._extract_kg_per_meter_from_line(line)
            
            if kg_per_meter is not None:
                section_name = f"{depth} x {width} x {thickness}"
                
                return {
                    'section_name': section_name,
                    'section_type': section_type,
                    'depth_mm': float(depth),
                    'width_mm': float(width),
                    'thickness_mm': float(thickness),
                    'kg_per_meter': kg_per_meter,
                    'description': f"British Steel {self.british_steel_mappings.get(section_type, section_type)}"
                }
        
        # Approach 2: Split by | or spaces and look for patterns
        parts = re.split(r'\s*\|\s*|\s+', line)
        
        if len(parts) >= 4:
            # Look for dimension pattern in first part
            first_part = parts[0]
            dimension_match = re.match(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', first_part)
            
            if dimension_match:
                depth = int(dimension_match.group(1))
                width = int(dimension_match.group(2))
                thickness = int(dimension_match.group(3))
                
                # Look for kg/m in subsequent parts - it's usually the second column
                kg_per_meter = None
                for i, part in enumerate(parts[1:], 1):
                    try:
                        potential_kg = float(part)
                        # kg/m should be a reasonable value (typically 10-1000 kg/m)
                        if 5.0 <= potential_kg <= 1000.0:
                            kg_per_meter = potential_kg
                            break
                    except ValueError:
                        continue
                
                if kg_per_meter is not None:
                    section_name = f"{depth} x {width} x {thickness}"
                    
                    return {
                        'section_name': section_name,
                        'section_type': section_type,
                        'depth_mm': float(depth),
                        'width_mm': float(width),
                        'thickness_mm': float(thickness),
                        'kg_per_meter': kg_per_meter,
                        'description': f"British Steel {self.british_steel_mappings.get(section_type, section_type)}"
                    }
        
        return None
    
    def _extract_kg_per_meter_from_line(self, line: str) -> Optional[float]:
        """Extract kg/m value from a line of text"""
        # Look for kg/m patterns
        kg_patterns = [
            r'(\d+\.?\d*)\s*kg/m',
            r'(\d+\.?\d*)\s*kg/meter',
            r'(\d+\.?\d*)\s*kg/m²',
            r'(\d+\.?\d*)\s*kg/m2',
        ]
        
        for pattern in kg_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match)
                    if 5.0 <= value <= 1000.0:  # Reasonable range for kg/m
                        return value
                except ValueError:
                    continue
        
        # If no explicit kg/m pattern, look for the first reasonable number after dimensions
        # This handles cases where kg/m is just a number in the data
        numbers = re.findall(r'\b(\d+\.?\d*)\b', line)
        for number in numbers:
            try:
                value = float(number)
                if 5.0 <= value <= 1000.0:  # Reasonable range for kg/m
                    return value
            except ValueError:
                continue
        
        return None
    
    def import_steel_database_from_pdf(self, pdf_path: str) -> Dict:
        """Import steel section database from PDF (legacy method)"""
        # Redirect to British Steel specific method
        return self.import_british_steel_database_from_pdf(pdf_path)
    
    def _parse_steel_sections_from_text(self, text: str) -> List[Dict]:
        """Parse steel sections from text content (legacy method)"""
        return self._parse_british_steel_sections_from_text(text)
    
    def _extract_kg_per_meter(self, line: str) -> Optional[float]:
        """Extract kg/m value from text line"""
        # Look for kg/m patterns
        kg_patterns = [
            r'(\d+\.?\d*)\s*kg/m',
            r'(\d+\.?\d*)\s*kg/meter',
            r'(\d+\.?\d*)\s*kg/m²',
            r'(\d+\.?\d*)\s*kg/m2'
        ]
        
        for pattern in kg_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None 