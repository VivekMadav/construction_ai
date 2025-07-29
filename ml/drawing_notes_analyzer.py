"""
Drawing Notes Analyzer for Construction AI

This module analyzes drawing notes, title blocks, and specifications to extract
critical information like concrete strength, steel grades, and construction details.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
import logging
from datetime import datetime
import re
from dataclasses import dataclass
from enum import Enum
import fitz  # PyMuPDF
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NoteType(Enum):
    """Types of drawing notes."""
    TITLE_BLOCK = "title_block"
    GENERAL_NOTES = "general_notes"
    SPECIFICATIONS = "specifications"
    MATERIAL_NOTES = "material_notes"
    CONSTRUCTION_NOTES = "construction_notes"
    DIMENSION_NOTES = "dimension_notes"
    REVISION_NOTES = "revision_notes"
    ADDITIONAL_NOTES = "additional_notes"

class MaterialType(Enum):
    """Types of materials mentioned in notes."""
    CONCRETE = "concrete"
    STEEL = "steel"
    TIMBER = "timber"
    MASONRY = "masonry"
    INSULATION = "insulation"
    FINISHES = "finishes"
    MEP = "mep"

@dataclass
class DrawingNote:
    """Represents a note found in a drawing."""
    note_type: NoteType
    text: str
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float
    location: str  # "title_block", "top", "bottom", "side", "center"
    extracted_info: Dict[str, Any]
    importance_score: float

@dataclass
class MaterialSpecification:
    """Represents material specifications extracted from notes."""
    material_type: MaterialType
    grade: str
    strength: Optional[str] = None
    specification: Optional[str] = None
    notes: Optional[str] = None
    confidence: float = 0.0

@dataclass
class DrawingSpecifications:
    """Comprehensive drawing specifications extracted from notes."""
    concrete_specs: List[MaterialSpecification]
    steel_specs: List[MaterialSpecification]
    other_materials: List[MaterialSpecification]
    general_notes: List[str]
    construction_notes: List[str]
    dimension_notes: List[str]
    revision_notes: List[str]
    critical_info: Dict[str, Any]

class DrawingNotesAnalyzer:
    """Analyzes drawing notes and extracts critical specifications."""
    
    def __init__(self):
        # Note detection patterns
        self.note_patterns = {
            NoteType.TITLE_BLOCK: [
                r'PROJECT\s*:.*',
                r'DRAWING\s*:.*',
                r'SCALE\s*:.*',
                r'DATE\s*:.*',
                r'REVISION\s*:.*',
                r'DRAWN\s*BY\s*:.*',
                r'CHECKED\s*BY\s*:.*'
            ],
            NoteType.SPECIFICATIONS: [
                r'CONCRETE\s*:.*',
                r'STEEL\s*:.*',
                r'GRADE\s*:.*',
                r'STRENGTH\s*:.*',
                r'SPECIFICATION\s*:.*',
                r'MATERIAL\s*:.*'
            ],
            NoteType.CONSTRUCTION_NOTES: [
                r'CONSTRUCTION\s*:.*',
                r'INSTALLATION\s*:.*',
                r'ERECTION\s*:.*',
                r'ANCHORAGE\s*:.*',
                r'CONNECTION\s*:.*',
                r'DETAIL\s*:.*'
            ],
            NoteType.DIMENSION_NOTES: [
                r'DIMENSIONS\s*:.*',
                r'ALL\s*DIMENSIONS\s*:.*',
                r'UNITS\s*:.*',
                r'SCALE\s*:.*',
                r'NOTES\s*:.*'
            ]
        }
        
        # Material specification patterns
        self.material_patterns = {
            MaterialType.CONCRETE: [
                r'CONCRETE\s*(?:GRADE|CLASS|STRENGTH)?\s*:?\s*([A-Z0-9/]+)',
                r'C([0-9]+)\s*(?:CONCRETE|GRADE)',
                r'CONCRETE\s*([A-Z0-9\s/]+)',
                r'STRENGTH\s*:?\s*([0-9]+)\s*(?:N/mm²|MPa|PSI)',
                r'F([0-9]+)\s*(?:CONCRETE|GRADE)'
            ],
            MaterialType.STEEL: [
                r'STEEL\s*(?:GRADE|TYPE)?\s*:?\s*([A-Z0-9]+)',
                r'S([0-9]+)\s*(?:STEEL|GRADE)',
                r'STEEL\s*([A-Z0-9\s]+)',
                r'GRADE\s*:?\s*([A-Z0-9]+)',
                r'REINFORCEMENT\s*:?\s*([A-Z0-9]+)'
            ],
            MaterialType.TIMBER: [
                r'TIMBER\s*(?:GRADE|TYPE)?\s*:?\s*([A-Z0-9]+)',
                r'WOOD\s*(?:GRADE|TYPE)?\s*:?\s*([A-Z0-9]+)',
                r'TR([0-9]+)\s*(?:TIMBER|GRADE)'
            ]
        }
        
        # Critical information patterns
        self.critical_patterns = {
            "concrete_strength": [
                r'CONCRETE\s*STRENGTH\s*:?\s*([0-9]+)\s*(?:N/mm²|MPa)',
                r'C([0-9]+)\s*CONCRETE',
                r'F([0-9]+)\s*CONCRETE'
            ],
            "steel_grade": [
                r'STEEL\s*GRADE\s*:?\s*([A-Z0-9]+)',
                r'S([0-9]+)\s*STEEL',
                r'REINFORCEMENT\s*GRADE\s*:?\s*([A-Z0-9]+)'
            ],
            "fire_rating": [
                r'FIRE\s*RATING\s*:?\s*([0-9]+)\s*(?:HOURS?|HR)',
                r'FIRE\s*RESISTANCE\s*:?\s*([0-9]+)\s*(?:HOURS?|HR)'
            ],
            "load_rating": [
                r'LOAD\s*RATING\s*:?\s*([0-9]+)\s*(?:KN|TONNES?)',
                r'CAPACITY\s*:?\s*([0-9]+)\s*(?:KN|TONNES?)'
            ],
            "dimensions": [
                r'ALL\s*DIMENSIONS\s*IN\s*([A-Z]+)',
                r'UNITS\s*:?\s*([A-Z]+)',
                r'SCALE\s*:?\s*([0-9:]+)'
            ]
        }
        
        # Common drawing note keywords
        self.note_keywords = {
            "critical": ["IMPORTANT", "CRITICAL", "ESSENTIAL", "MUST", "REQUIRED"],
            "material": ["CONCRETE", "STEEL", "TIMBER", "MASONRY", "MATERIAL"],
            "specification": ["GRADE", "STRENGTH", "TYPE", "SPECIFICATION"],
            "construction": ["CONSTRUCTION", "INSTALLATION", "ERECTION", "ANCHORAGE"],
            "dimension": ["DIMENSION", "SCALE", "UNITS", "MEASUREMENT"]
        }
    
    def analyze_drawing_notes(self, drawing_path: str) -> DrawingSpecifications:
        """
        Analyze drawing notes and extract specifications.
        
        Args:
            drawing_path: Path to the drawing file
            
        Returns:
            Comprehensive drawing specifications
        """
        try:
            logger.info(f"Analyzing drawing notes: {drawing_path}")
            
            # Extract text content from drawing
            text_content = self._extract_text_content(drawing_path)
            
            # Analyze different note types
            title_block_notes = self._analyze_title_block(text_content)
            general_notes = self._analyze_general_notes(text_content)
            material_notes = self._analyze_material_notes(text_content)
            construction_notes = self._analyze_construction_notes(text_content)
            dimension_notes = self._analyze_dimension_notes(text_content)
            revision_notes = self._analyze_revision_notes(text_content)
            
            # Extract material specifications
            concrete_specs = self._extract_concrete_specifications(text_content)
            steel_specs = self._extract_steel_specifications(text_content)
            other_materials = self._extract_other_material_specifications(text_content)
            
            # Extract critical information
            critical_info = self._extract_critical_information(text_content)
            
            # Create comprehensive specifications
            specifications = DrawingSpecifications(
                concrete_specs=concrete_specs,
                steel_specs=steel_specs,
                other_materials=other_materials,
                general_notes=general_notes,
                construction_notes=construction_notes,
                dimension_notes=dimension_notes,
                revision_notes=revision_notes,
                critical_info=critical_info
            )
            
            logger.info(f"Drawing notes analysis completed: {len(concrete_specs)} concrete specs, {len(steel_specs)} steel specs")
            return specifications
            
        except Exception as e:
            logger.error(f"Error analyzing drawing notes: {e}")
            return DrawingSpecifications([], [], [], [], [], [], [], {})
    
    def _extract_text_content(self, drawing_path: str) -> str:
        """Extract text content from drawing."""
        try:
            if drawing_path.lower().endswith('.pdf'):
                pdf_document = fitz.open(drawing_path)
                text_content = ""
                
                for page in pdf_document:
                    text_content += page.get_text()
                
                pdf_document.close()
                return text_content
            else:
                # For image files, use OCR
                # TODO: Implement OCR text extraction
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""
    
    def _analyze_title_block(self, text_content: str) -> List[DrawingNote]:
        """Analyze title block information."""
        notes = []
        
        # Common title block patterns
        title_patterns = [
            r'PROJECT\s*:?\s*([^\n]+)',
            r'DRAWING\s*:?\s*([^\n]+)',
            r'SCALE\s*:?\s*([^\n]+)',
            r'DATE\s*:?\s*([^\n]+)',
            r'REVISION\s*:?\s*([^\n]+)',
            r'DRAWN\s*BY\s*:?\s*([^\n]+)',
            r'CHECKED\s*BY\s*:?\s*([^\n]+)'
        ]
        
        for pattern in title_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                note = DrawingNote(
                    note_type=NoteType.TITLE_BLOCK,
                    text=match.group(0),
                    bbox=[0, 0, 0, 0],  # Will be updated with actual position
                    confidence=0.9,
                    location="title_block",
                    extracted_info={"field": match.group(1).strip()},
                    importance_score=0.8
                )
                notes.append(note)
        
        return notes
    
    def _analyze_general_notes(self, text_content: str) -> List[str]:
        """Analyze general notes in the drawing."""
        notes = []
        
        # Look for general note patterns
        general_patterns = [
            r'GENERAL\s*NOTES?\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'NOTES?\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'SPECIAL\s*NOTES?\s*:?\s*([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in general_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                note_text = match.group(1).strip()
                if note_text:
                    notes.append(note_text)
        
        return notes
    
    def _analyze_material_notes(self, text_content: str) -> List[DrawingNote]:
        """Analyze material-related notes."""
        notes = []
        
        # Look for material note patterns
        material_patterns = [
            r'MATERIAL\s*:?\s*([^\n]+)',
            r'CONCRETE\s*:?\s*([^\n]+)',
            r'STEEL\s*:?\s*([^\n]+)',
            r'GRADE\s*:?\s*([^\n]+)',
            r'STRENGTH\s*:?\s*([^\n]+)'
        ]
        
        for pattern in material_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                note = DrawingNote(
                    note_type=NoteType.MATERIAL_NOTES,
                    text=match.group(0),
                    bbox=[0, 0, 0, 0],
                    confidence=0.85,
                    location="general",
                    extracted_info={"material_info": match.group(1).strip()},
                    importance_score=0.9
                )
                notes.append(note)
        
        return notes
    
    def _analyze_construction_notes(self, text_content: str) -> List[str]:
        """Analyze construction-related notes."""
        notes = []
        
        # Look for construction note patterns
        construction_patterns = [
            r'CONSTRUCTION\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'INSTALLATION\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'ERECTION\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'ANCHORAGE\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'CONNECTION\s*:?\s*([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in construction_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                note_text = match.group(1).strip()
                if note_text:
                    notes.append(note_text)
        
        return notes
    
    def _analyze_dimension_notes(self, text_content: str) -> List[str]:
        """Analyze dimension-related notes."""
        notes = []
        
        # Look for dimension note patterns
        dimension_patterns = [
            r'DIMENSIONS?\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'ALL\s*DIMENSIONS?\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'UNITS?\s*:?\s*([^\n]+)',
            r'SCALE\s*:?\s*([^\n]+)'
        ]
        
        for pattern in dimension_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                note_text = match.group(1).strip()
                if note_text:
                    notes.append(note_text)
        
        return notes
    
    def _analyze_revision_notes(self, text_content: str) -> List[str]:
        """Analyze revision-related notes."""
        notes = []
        
        # Look for revision note patterns
        revision_patterns = [
            r'REVISION\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'CHANGE\s*:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'UPDATE\s*:?\s*([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in revision_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                note_text = match.group(1).strip()
                if note_text:
                    notes.append(note_text)
        
        return notes
    
    def _extract_concrete_specifications(self, text_content: str) -> List[MaterialSpecification]:
        """Extract concrete specifications from text."""
        specs = []
        
        for pattern in self.material_patterns[MaterialType.CONCRETE]:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                grade = match.group(1).strip()
                
                # Extract strength if available
                strength = None
                strength_match = re.search(r'([0-9]+)\s*(?:N/mm²|MPa|PSI)', grade)
                if strength_match:
                    strength = strength_match.group(1)
                
                spec = MaterialSpecification(
                    material_type=MaterialType.CONCRETE,
                    grade=grade,
                    strength=strength,
                    confidence=0.85
                )
                specs.append(spec)
        
        return specs
    
    def _extract_steel_specifications(self, text_content: str) -> List[MaterialSpecification]:
        """Extract steel specifications from text."""
        specs = []
        
        for pattern in self.material_patterns[MaterialType.STEEL]:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                grade = match.group(1).strip()
                
                spec = MaterialSpecification(
                    material_type=MaterialType.STEEL,
                    grade=grade,
                    confidence=0.85
                )
                specs.append(spec)
        
        return specs
    
    def _extract_other_material_specifications(self, text_content: str) -> List[MaterialSpecification]:
        """Extract other material specifications from text."""
        specs = []
        
        for material_type, patterns in self.material_patterns.items():
            if material_type not in [MaterialType.CONCRETE, MaterialType.STEEL]:
                for pattern in patterns:
                    matches = re.finditer(pattern, text_content, re.IGNORECASE)
                    for match in matches:
                        grade = match.group(1).strip()
                        
                        spec = MaterialSpecification(
                            material_type=material_type,
                            grade=grade,
                            confidence=0.8
                        )
                        specs.append(spec)
        
        return specs
    
    def _extract_critical_information(self, text_content: str) -> Dict[str, Any]:
        """Extract critical information from drawing notes."""
        critical_info = {}
        
        for info_type, patterns in self.critical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).strip()
                    critical_info[info_type] = value
                    break  # Take first match for each type
        
        # Extract additional critical information
        critical_info.update(self._extract_additional_critical_info(text_content))
        
        return critical_info
    
    def _extract_additional_critical_info(self, text_content: str) -> Dict[str, Any]:
        """Extract additional critical information."""
        additional_info = {}
        
        # Look for fire rating
        fire_match = re.search(r'FIRE\s*RATING\s*:?\s*([0-9]+)\s*(?:HOURS?|HR)', text_content, re.IGNORECASE)
        if fire_match:
            additional_info["fire_rating_hours"] = fire_match.group(1)
        
        # Look for load capacity
        load_match = re.search(r'LOAD\s*CAPACITY\s*:?\s*([0-9]+)\s*(?:KN|TONNES?)', text_content, re.IGNORECASE)
        if load_match:
            additional_info["load_capacity"] = load_match.group(1)
        
        # Look for seismic requirements
        seismic_match = re.search(r'SEISMIC\s*:?\s*([^\n]+)', text_content, re.IGNORECASE)
        if seismic_match:
            additional_info["seismic_requirements"] = seismic_match.group(1).strip()
        
        # Look for environmental requirements
        env_match = re.search(r'ENVIRONMENTAL\s*:?\s*([^\n]+)', text_content, re.IGNORECASE)
        if env_match:
            additional_info["environmental_requirements"] = env_match.group(1).strip()
        
        return additional_info
    
    def apply_notes_to_elements(self, 
                               elements: List[Dict], 
                               specifications: DrawingSpecifications) -> List[Dict]:
        """
        Apply drawing notes and specifications to detected elements.
        
        Args:
            elements: List of detected elements
            specifications: Drawing specifications from notes
            
        Returns:
            Enhanced elements with applied specifications
        """
        enhanced_elements = []
        
        for element in elements:
            enhanced_element = element.copy()
            
            # Apply concrete specifications
            if element.get('type') in ['wall', 'slab', 'foundation', 'column']:
                enhanced_element = self._apply_concrete_specs(enhanced_element, specifications)
            
            # Apply steel specifications
            if element.get('type') in ['beam', 'column', 'truss', 'connection']:
                enhanced_element = self._apply_steel_specs(enhanced_element, specifications)
            
            # Apply general specifications
            enhanced_element = self._apply_general_specs(enhanced_element, specifications)
            
            # Add notes information
            enhanced_element['drawing_notes'] = {
                'concrete_specs': [spec.grade for spec in specifications.concrete_specs],
                'steel_specs': [spec.grade for spec in specifications.steel_specs],
                'critical_info': specifications.critical_info,
                'general_notes': specifications.general_notes,
                'construction_notes': specifications.construction_notes
            }
            
            enhanced_elements.append(enhanced_element)
        
        return enhanced_elements
    
    def _apply_concrete_specs(self, element: Dict, specifications: DrawingSpecifications) -> Dict:
        """Apply concrete specifications to element."""
        if specifications.concrete_specs:
            # Use the first concrete specification found
            concrete_spec = specifications.concrete_specs[0]
            
            element['material'] = 'concrete'
            element['concrete_grade'] = concrete_spec.grade
            if concrete_spec.strength:
                element['concrete_strength'] = concrete_spec.strength
            
            # Update confidence based on specification availability
            element['confidence'] = min(1.0, element.get('confidence', 0.7) + 0.1)
        
        return element
    
    def _apply_steel_specs(self, element: Dict, specifications: DrawingSpecifications) -> Dict:
        """Apply steel specifications to element."""
        if specifications.steel_specs:
            # Use the first steel specification found
            steel_spec = specifications.steel_specs[0]
            
            element['material'] = 'steel'
            element['steel_grade'] = steel_spec.grade
            
            # Update confidence based on specification availability
            element['confidence'] = min(1.0, element.get('confidence', 0.7) + 0.1)
        
        return element
    
    def _apply_general_specs(self, element: Dict, specifications: DrawingSpecifications) -> Dict:
        """Apply general specifications to element."""
        # Apply critical information
        if specifications.critical_info:
            element['critical_info'] = specifications.critical_info
        
        # Apply construction notes if relevant
        if specifications.construction_notes and element.get('type') in ['connection', 'anchor']:
            element['construction_notes'] = specifications.construction_notes
        
        return element
    
    def generate_notes_report(self, specifications: DrawingSpecifications) -> Dict[str, Any]:
        """Generate a comprehensive report of drawing notes analysis."""
        report = {
            "analysis_summary": {
                "concrete_specifications": len(specifications.concrete_specs),
                "steel_specifications": len(specifications.steel_specs),
                "other_materials": len(specifications.other_materials),
                "general_notes": len(specifications.general_notes),
                "construction_notes": len(specifications.construction_notes),
                "dimension_notes": len(specifications.dimension_notes),
                "revision_notes": len(specifications.revision_notes)
            },
            "material_specifications": {
                "concrete": [spec.grade for spec in specifications.concrete_specs],
                "steel": [spec.grade for spec in specifications.steel_specs],
                "other": [f"{spec.material_type.value}: {spec.grade}" for spec in specifications.other_materials]
            },
            "critical_information": specifications.critical_info,
            "notes_content": {
                "general_notes": specifications.general_notes,
                "construction_notes": specifications.construction_notes,
                "dimension_notes": specifications.dimension_notes,
                "revision_notes": specifications.revision_notes
            }
        }
        
        return report

def main():
    """Main function for testing drawing notes analyzer."""
    analyzer = DrawingNotesAnalyzer()
    
    # Example usage
    print("Drawing Notes Analyzer initialized")
    
    # Test with a sample drawing
    test_drawing_path = "uploads/1/20250723_153938_4977_S_DW06 - WATER TANK LAYOUT - 2.pdf"
    
    if os.path.exists(test_drawing_path):
        specifications = analyzer.analyze_drawing_notes(test_drawing_path)
        
        print(f"\nDrawing Notes Analysis Results:")
        print(f"  Concrete specs: {len(specifications.concrete_specs)}")
        print(f"  Steel specs: {len(specifications.steel_specs)}")
        print(f"  General notes: {len(specifications.general_notes)}")
        print(f"  Critical info: {len(specifications.critical_info)}")
        
        # Generate report
        report = analyzer.generate_notes_report(specifications)
        print(f"\nReport generated with {len(report['analysis_summary'])} categories")
    else:
        print("Test drawing not found")

if __name__ == "__main__":
    main() 