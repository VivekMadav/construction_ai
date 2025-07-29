"""
Drawing Reference Analyzer for Cross-Drawing Analysis

This module handles drawing references, cross-references, and multi-drawing
analysis to improve element measurement accuracy by combining information
from multiple related drawings.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReferenceType(Enum):
    """Types of drawing references."""
    SECTION = "section"
    DETAIL = "detail"
    ELEVATION = "elevation"
    PLAN = "plan"
    SCHEDULE = "schedule"
    SPECIFICATION = "specification"
    NOTE = "note"

@dataclass
class DrawingReference:
    """Represents a reference between drawings."""
    source_drawing_id: str
    target_drawing_id: str
    reference_type: ReferenceType
    reference_mark: str  # e.g., "A-A", "DETAIL 1", "SECTION B"
    bbox: List[int]  # [x1, y1, x2, y2] in source drawing
    confidence: float
    description: Optional[str] = None
    scale_factor: Optional[float] = None

@dataclass
class CrossDrawingElement:
    """Element information from multiple drawings."""
    element_id: str
    element_type: str
    primary_drawing_id: str
    reference_drawings: List[str]
    measurements: Dict[str, Any]
    confidence: float
    cross_reference_confidence: float

class DrawingReferenceAnalyzer:
    """Analyzes drawing references and cross-references for improved accuracy."""
    
    def __init__(self, base_path: str = "ml/data"):
        self.base_path = Path(base_path)
        
        # Reference patterns for different drawing types
        self.reference_patterns = {
            ReferenceType.SECTION: [
                r'([A-Z])-([A-Z])',  # A-A, B-B, etc.
                r'SECTION\s+([A-Z])',  # SECTION A
                r'([A-Z])\s*-\s*([A-Z])',  # A - A
            ],
            ReferenceType.DETAIL: [
                r'DETAIL\s+(\d+)',  # DETAIL 1, DETAIL 2
                r'DET\s+(\d+)',  # DET 1
                r'(\d+)',  # Just numbers
            ],
            ReferenceType.ELEVATION: [
                r'ELEVATION\s+([A-Z])',  # ELEVATION A
                r'ELEV\s+([A-Z])',  # ELEV A
                r'([A-Z])',  # Just letters
            ],
            ReferenceType.PLAN: [
                r'PLAN\s+(\d+)',  # PLAN 1
                r'LEVEL\s+(\d+)',  # LEVEL 1
                r'FLOOR\s+(\d+)',  # FLOOR 1
            ]
        }
        
        # Common reference symbols and their meanings
        self.reference_symbols = {
            "section_mark": ["◄►", "►◄", "◄", "►", "→", "←"],
            "detail_mark": ["○", "●", "□", "■", "△", "▲"],
            "elevation_mark": ["↑", "↓", "↗", "↘", "↖", "↙"],
            "plan_mark": ["▢", "▣", "▤", "▥", "▦", "▧"]
        }
        
        # Initialize reference database
        self.reference_database = {}
        self.cross_reference_graph = {}
    
    def analyze_drawing_references(self, drawing_id: str, drawing_path: str) -> List[DrawingReference]:
        """
        Analyze a drawing for references to other drawings.
        
        Args:
            drawing_id: Unique drawing identifier
            drawing_path: Path to the drawing file
            
        Returns:
            List of drawing references found
        """
        references = []
        
        try:
            # Load drawing image
            image = self._load_drawing_image(drawing_path)
            if image is None:
                return references
            
            # Extract text content
            text_content = self._extract_text_content(drawing_path)
            
            # Find reference marks in text
            text_references = self._find_text_references(text_content, drawing_id)
            references.extend(text_references)
            
            # Find reference symbols in image
            symbol_references = self._find_symbol_references(image, drawing_id)
            references.extend(symbol_references)
            
            # Find reference lines and arrows
            line_references = self._find_line_references(image, drawing_id)
            references.extend(line_references)
            
            # Validate and filter references
            valid_references = self._validate_references(references)
            
            # Store in database
            self._store_references(drawing_id, valid_references)
            
            logger.info(f"Found {len(valid_references)} references in drawing {drawing_id}")
            return valid_references
            
        except Exception as e:
            logger.error(f"Error analyzing drawing references: {e}")
            return references
    
    def _load_drawing_image(self, drawing_path: str) -> Optional[np.ndarray]:
        """Load drawing image for analysis."""
        try:
            if drawing_path.lower().endswith('.pdf'):
                import fitz
                pdf_document = fitz.open(drawing_path)
                page = pdf_document[0]
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(img_data))
                return np.array(img)
            else:
                return cv2.imread(drawing_path)
        except Exception as e:
            logger.error(f"Error loading drawing image: {e}")
            return None
    
    def _extract_text_content(self, drawing_path: str) -> str:
        """Extract text content from drawing."""
        try:
            if drawing_path.lower().endswith('.pdf'):
                import fitz
                pdf_document = fitz.open(drawing_path)
                text_content = ""
                for page in pdf_document:
                    text_content += page.get_text()
                return text_content
            else:
                # For image files, use OCR
                # TODO: Implement OCR text extraction
                return ""
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""
    
    def _find_text_references(self, text_content: str, drawing_id: str) -> List[DrawingReference]:
        """Find references in text content."""
        references = []
        
        for ref_type, patterns in self.reference_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                
                for match in matches:
                    reference_mark = match.group(0)
                    
                    # Create reference object
                    reference = DrawingReference(
                        source_drawing_id=drawing_id,
                        target_drawing_id=self._resolve_reference_target(reference_mark, ref_type),
                        reference_type=ref_type,
                        reference_mark=reference_mark,
                        bbox=[0, 0, 0, 0],  # Will be updated with actual position
                        confidence=0.8,
                        description=f"{ref_type.value.title()} reference: {reference_mark}"
                    )
                    
                    references.append(reference)
        
        return references
    
    def _find_symbol_references(self, image: np.ndarray, drawing_id: str) -> List[DrawingReference]:
        """Find reference symbols in image."""
        references = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Template matching for reference symbols
        for symbol_type, symbols in self.reference_symbols.items():
            for symbol in symbols:
                # Create template for symbol
                template = self._create_symbol_template(symbol)
                
                # Find matches
                matches = self._find_template_matches(gray, template)
                
                for match in matches:
                    bbox = match['bbox']
                    confidence = match['confidence']
                    
                    # Determine reference type from symbol
                    ref_type = self._get_reference_type_from_symbol(symbol_type)
                    
                    reference = DrawingReference(
                        source_drawing_id=drawing_id,
                        target_drawing_id="unknown",  # Will be resolved later
                        reference_type=ref_type,
                        reference_mark=symbol,
                        bbox=bbox,
                        confidence=confidence,
                        description=f"Symbol reference: {symbol}"
                    )
                    
                    references.append(reference)
        
        return references
    
    def _find_line_references(self, image: np.ndarray, drawing_id: str) -> List[DrawingReference]:
        """Find reference lines and arrows."""
        references = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Edge detection for lines
        edges = cv2.Canny(gray, 50, 150)
        
        # Line detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                               minLineLength=30, maxLineGap=10)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Check if line has arrow or reference mark
                if self._is_reference_line(x1, y1, x2, y2, image):
                    bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                    
                    reference = DrawingReference(
                        source_drawing_id=drawing_id,
                        target_drawing_id="unknown",
                        reference_type=ReferenceType.SECTION,
                        reference_mark="LINE_REF",
                        bbox=bbox,
                        confidence=0.6,
                        description="Line reference"
                    )
                    
                    references.append(reference)
        
        return references
    
    def _create_symbol_template(self, symbol: str) -> np.ndarray:
        """Create template for symbol matching."""
        # Create a simple template based on symbol
        template_size = 20
        template = np.zeros((template_size, template_size), dtype=np.uint8)
        
        # Draw symbol in template
        if symbol in ["◄►", "►◄"]:
            # Draw arrow pair
            cv2.arrowedLine(template, (5, 10), (15, 10), 255, 2)
            cv2.arrowedLine(template, (15, 10), (5, 10), 255, 2)
        elif symbol in ["○", "●"]:
            # Draw circle
            cv2.circle(template, (10, 10), 8, 255, 2)
        elif symbol in ["□", "■"]:
            # Draw square
            cv2.rectangle(template, (2, 2), (18, 18), 255, 2)
        elif symbol in ["↑", "↓"]:
            # Draw arrow
            cv2.arrowedLine(template, (10, 15), (10, 5), 255, 2)
        
        return template
    
    def _find_template_matches(self, image: np.ndarray, template: np.ndarray) -> List[Dict]:
        """Find template matches in image."""
        matches = []
        
        # Template matching
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= 0.7)  # Threshold
        
        for pt in zip(*locations[::-1]):
            x, y = pt
            confidence = result[y, x]
            
            matches.append({
                'bbox': [x, y, x + template.shape[1], y + template.shape[0]],
                'confidence': confidence
            })
        
        return matches
    
    def _get_reference_type_from_symbol(self, symbol_type: str) -> ReferenceType:
        """Get reference type from symbol type."""
        mapping = {
            "section_mark": ReferenceType.SECTION,
            "detail_mark": ReferenceType.DETAIL,
            "elevation_mark": ReferenceType.ELEVATION,
            "plan_mark": ReferenceType.PLAN
        }
        return mapping.get(symbol_type, ReferenceType.SECTION)
    
    def _is_reference_line(self, x1: int, y1: int, x2: int, y2: int, image: np.ndarray) -> bool:
        """Check if line is a reference line."""
        # Check for arrow heads or reference marks near line endpoints
        # This is a simplified check - in practice, you'd use more sophisticated detection
        
        # Check if line has arrow-like features
        line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Reference lines are typically longer than regular lines
        if line_length > 50:
            return True
        
        return False
    
    def _resolve_reference_target(self, reference_mark: str, ref_type: ReferenceType) -> str:
        """Resolve reference mark to target drawing ID."""
        # This would typically involve looking up in a drawing index
        # For now, return a placeholder
        return f"target_{ref_type.value}_{reference_mark}"
    
    def _validate_references(self, references: List[DrawingReference]) -> List[DrawingReference]:
        """Validate and filter references."""
        valid_references = []
        
        for ref in references:
            # Basic validation
            if ref.confidence > 0.5 and ref.bbox != [0, 0, 0, 0]:
                valid_references.append(ref)
        
        return valid_references
    
    def _store_references(self, drawing_id: str, references: List[DrawingReference]):
        """Store references in database."""
        self.reference_database[drawing_id] = references
        
        # Build cross-reference graph
        for ref in references:
            if ref.target_drawing_id not in self.cross_reference_graph:
                self.cross_reference_graph[ref.target_drawing_id] = []
            
            self.cross_reference_graph[ref.target_drawing_id].append({
                'source_drawing_id': drawing_id,
                'reference': ref
            })
    
    def analyze_cross_drawing_elements(self, 
                                     primary_drawing_id: str,
                                     reference_drawing_ids: List[str]) -> List[CrossDrawingElement]:
        """
        Analyze elements across multiple related drawings.
        
        Args:
            primary_drawing_id: Main drawing ID
            reference_drawing_ids: List of reference drawing IDs
            
        Returns:
            List of cross-drawing elements with enhanced information
        """
        cross_elements = []
        
        try:
            # Get primary drawing elements
            primary_elements = self._get_drawing_elements(primary_drawing_id)
            
            # Get reference drawing elements
            reference_elements = {}
            for ref_id in reference_drawing_ids:
                reference_elements[ref_id] = self._get_drawing_elements(ref_id)
            
            # Match elements across drawings
            for primary_elem in primary_elements:
                matched_elements = self._match_elements_across_drawings(
                    primary_elem, reference_elements
                )
                
                if matched_elements:
                    # Create cross-drawing element
                    cross_elem = self._create_cross_drawing_element(
                        primary_elem, matched_elements, primary_drawing_id, reference_drawing_ids
                    )
                    cross_elements.append(cross_elem)
            
            logger.info(f"Created {len(cross_elements)} cross-drawing elements")
            return cross_elements
            
        except Exception as e:
            logger.error(f"Error analyzing cross-drawing elements: {e}")
            return cross_elements
    
    def _get_drawing_elements(self, drawing_id: str) -> List[Dict]:
        """Get elements from a drawing."""
        # This would typically load from your existing element detection system
        # For now, return placeholder data
        return []
    
    def _match_elements_across_drawings(self, 
                                       primary_elem: Dict, 
                                       reference_elements: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Match elements across different drawings."""
        matched_elements = {}
        
        for ref_drawing_id, ref_elements in reference_elements.items():
            best_match = None
            best_score = 0
            
            for ref_elem in ref_elements:
                # Calculate similarity score
                score = self._calculate_element_similarity(primary_elem, ref_elem)
                
                if score > best_score and score > 0.7:  # Threshold
                    best_score = score
                    best_match = ref_elem
            
            if best_match:
                matched_elements[ref_drawing_id] = best_match
        
        return matched_elements
    
    def _calculate_element_similarity(self, elem1: Dict, elem2: Dict) -> float:
        """Calculate similarity between two elements."""
        # Compare element types
        type_similarity = 1.0 if elem1.get('type') == elem2.get('type') else 0.0
        
        # Compare positions (normalized)
        pos_similarity = self._calculate_position_similarity(elem1, elem2)
        
        # Compare properties
        prop_similarity = self._calculate_property_similarity(elem1, elem2)
        
        # Weighted average
        similarity = (type_similarity * 0.4 + pos_similarity * 0.4 + prop_similarity * 0.2)
        
        return similarity
    
    def _calculate_position_similarity(self, elem1: Dict, elem2: Dict) -> float:
        """Calculate position similarity between elements."""
        # This would compare normalized positions
        # For now, return placeholder
        return 0.8
    
    def _calculate_property_similarity(self, elem1: Dict, elem2: Dict) -> float:
        """Calculate property similarity between elements."""
        # Compare properties like dimensions, materials, etc.
        # For now, return placeholder
        return 0.7
    
    def _create_cross_drawing_element(self, 
                                    primary_elem: Dict,
                                    matched_elements: Dict[str, Dict],
                                    primary_drawing_id: str,
                                    reference_drawing_ids: List[str]) -> CrossDrawingElement:
        """Create cross-drawing element with enhanced information."""
        
        # Combine measurements from all drawings
        combined_measurements = self._combine_measurements(primary_elem, matched_elements)
        
        # Calculate cross-reference confidence
        cross_ref_confidence = self._calculate_cross_reference_confidence(matched_elements)
        
        # Create cross-drawing element
        cross_elem = CrossDrawingElement(
            element_id=f"{primary_drawing_id}_{primary_elem.get('id', 'unknown')}",
            element_type=primary_elem.get('type', 'unknown'),
            primary_drawing_id=primary_drawing_id,
            reference_drawings=list(matched_elements.keys()),
            measurements=combined_measurements,
            confidence=primary_elem.get('confidence', 0.5),
            cross_reference_confidence=cross_ref_confidence
        )
        
        return cross_elem
    
    def _combine_measurements(self, primary_elem: Dict, matched_elements: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine measurements from multiple drawings."""
        combined = {}
        
        # Start with primary element measurements
        if 'measurements' in primary_elem:
            combined.update(primary_elem['measurements'])
        
        # Add measurements from reference drawings
        for ref_drawing_id, ref_elem in matched_elements.items():
            if 'measurements' in ref_elem:
                for key, value in ref_elem['measurements'].items():
                    if key not in combined:
                        combined[key] = value
                    else:
                        # Average or use the more detailed measurement
                        if isinstance(value, (int, float)) and isinstance(combined[key], (int, float)):
                            combined[key] = (combined[key] + value) / 2
                        elif isinstance(value, dict) and isinstance(combined[key], dict):
                            # Merge detailed measurements
                            combined[key].update(value)
        
        return combined
    
    def _calculate_cross_reference_confidence(self, matched_elements: Dict[str, Dict]) -> float:
        """Calculate confidence based on cross-references."""
        if not matched_elements:
            return 0.0
        
        # Average confidence of matched elements
        confidences = [elem.get('confidence', 0.5) for elem in matched_elements.values()]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Boost confidence based on number of references
        reference_boost = min(len(matched_elements) * 0.1, 0.3)
        
        return min(avg_confidence + reference_boost, 1.0)
    
    def get_reference_statistics(self) -> Dict[str, Any]:
        """Get statistics about drawing references."""
        stats = {
            "total_drawings": len(self.reference_database),
            "total_references": sum(len(refs) for refs in self.reference_database.values()),
            "reference_types": {},
            "cross_reference_graph_size": len(self.cross_reference_graph)
        }
        
        # Count reference types
        for drawing_refs in self.reference_database.values():
            for ref in drawing_refs:
                ref_type = ref.reference_type.value
                stats["reference_types"][ref_type] = stats["reference_types"].get(ref_type, 0) + 1
        
        return stats
    
    def export_reference_database(self, output_path: str):
        """Export reference database to file."""
        try:
            # Convert dataclasses to dictionaries for JSON serialization
            export_data = {}
            
            for drawing_id, references in self.reference_database.items():
                export_data[drawing_id] = []
                for ref in references:
                    export_data[drawing_id].append({
                        'source_drawing_id': ref.source_drawing_id,
                        'target_drawing_id': ref.target_drawing_id,
                        'reference_type': ref.reference_type.value,
                        'reference_mark': ref.reference_mark,
                        'bbox': ref.bbox,
                        'confidence': ref.confidence,
                        'description': ref.description,
                        'scale_factor': ref.scale_factor
                    })
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported reference database to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting reference database: {e}")

def main():
    """Main function for testing drawing reference analyzer."""
    analyzer = DrawingReferenceAnalyzer()
    
    # Example usage
    print("Drawing Reference Analyzer initialized")
    
    # Analyze a drawing for references
    # references = analyzer.analyze_drawing_references("drawing_001", "path/to/drawing.pdf")
    
    # Get statistics
    stats = analyzer.get_reference_statistics()
    print(f"\nReference Statistics: {stats}")

if __name__ == "__main__":
    main() 