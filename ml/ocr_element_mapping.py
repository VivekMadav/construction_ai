"""
OCR → Element Mapping System for Construction AI

This module integrates PaddleOCR for text extraction and creates intelligent
mapping between extracted text and visual elements for enhanced classification.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import cv2
from dataclasses import dataclass
from enum import Enum
import re

# Try to import PaddleOCR
try:
    from paddleocr import PaddleOCR
    OCR_AVAILABLE = True
except ImportError:
    logging.warning("PaddleOCR not available. Install with: pip install paddlepaddle paddleocr")
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)

class TextType(Enum):
    """Types of text found in construction drawings."""
    ELEMENT_LABEL = "element_label"      # Labels like "WALL", "DOOR", "WINDOW"
    DIMENSION = "dimension"              # Measurements like "3000", "2.4m"
    ROOM_NAME = "room_name"              # Room names like "BEDROOM", "KITCHEN"
    MATERIAL = "material"                # Materials like "CONCRETE", "STEEL"
    SPECIFICATION = "specification"      # Specs like "FIRE RATED", "INSULATED"
    GENERAL_TEXT = "general_text"        # Other text

@dataclass
class ExtractedText:
    """Represents extracted text with position and metadata."""
    text: str
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float
    text_type: TextType
    properties: Dict[str, Any]

@dataclass
class TextElementMapping:
    """Represents a mapping between text and visual element."""
    text: ExtractedText
    element_bbox: List[int]
    distance: float
    confidence: float
    relationship: str  # "label", "dimension", "property", "nearby"

class OCRProcessor:
    """Handles OCR text extraction from construction drawings."""
    
    def __init__(self, use_gpu: bool = False):
        self.ocr = None
        if OCR_AVAILABLE:
            try:
                # Initialize PaddleOCR with English language
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    use_gpu=use_gpu,
                    show_log=False
                )
                logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                self.ocr = None
        else:
            logger.warning("PaddleOCR not available, using fallback text detection")
    
    def extract_text(self, image: np.ndarray) -> List[ExtractedText]:
        """
        Extract text from image using PaddleOCR.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of extracted text objects
        """
        if self.ocr is None:
            return self._fallback_text_extraction(image)
        
        try:
            # Run OCR
            results = self.ocr.ocr(image, cls=True)
            
            extracted_texts = []
            
            if results and results[0]:
                for line in results[0]:
                    if line and len(line) >= 2:
                        # PaddleOCR returns: [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)]
                        bbox = line[0]  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                        text_info = line[1]  # (text, confidence)
                        
                        if text_info and len(text_info) >= 2:
                            text = text_info[0]
                            confidence = text_info[1]
                            
                            # Convert bbox to [x1, y1, x2, y2] format
                            x_coords = [point[0] for point in bbox]
                            y_coords = [point[1] for point in bbox]
                            bbox_rect = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                            
                            # Classify text type
                            text_type = self._classify_text_type(text)
                            
                            # Create extracted text object
                            extracted_text = ExtractedText(
                                text=text,
                                bbox=bbox_rect,
                                confidence=confidence,
                                text_type=text_type,
                                properties=self._extract_text_properties(text)
                            )
                            
                            extracted_texts.append(extracted_text)
            
            logger.info(f"Extracted {len(extracted_texts)} text elements")
            return extracted_texts
            
        except Exception as e:
            logger.error(f"Error in OCR processing: {e}")
            return self._fallback_text_extraction(image)
    
    def _fallback_text_extraction(self, image: np.ndarray) -> List[ExtractedText]:
        """Fallback text extraction using contour analysis."""
        extracted_texts = []
        
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter for text-like regions (small rectangular areas)
                if 10 < w < 200 and 5 < h < 50:
                    if 0.1 < w/h < 10:  # Reasonable aspect ratio for text
                        # Create a placeholder text
                        text = f"TEXT_{len(extracted_texts):03d}"
                        
                        extracted_text = ExtractedText(
                            text=text,
                            bbox=[x, y, x + w, y + h],
                            confidence=0.5,
                            text_type=TextType.GENERAL_TEXT,
                            properties={"width": w, "height": h, "area": w * h}
                        )
                        
                        extracted_texts.append(extracted_text)
            
            logger.info(f"Fallback extracted {len(extracted_texts)} text regions")
            return extracted_texts
            
        except Exception as e:
            logger.error(f"Error in fallback text extraction: {e}")
            return []
    
    def _classify_text_type(self, text: str) -> TextType:
        """Classify the type of text based on content and patterns."""
        text_upper = text.upper().strip()
        
        # Element labels
        element_keywords = [
            "WALL", "DOOR", "WINDOW", "COLUMN", "BEAM", "SLAB", "FOUNDATION",
            "DUCT", "PIPE", "PANEL", "SWITCH", "OUTLET", "VALVE", "PUMP"
        ]
        
        for keyword in element_keywords:
            if keyword in text_upper:
                return TextType.ELEMENT_LABEL
        
        # Dimensions (numbers with units or just numbers)
        dimension_patterns = [
            r'\d+\.?\d*\s*(MM|CM|M|FT|IN)',  # 3000mm, 2.4m, etc.
            r'\d+\.?\d*',  # Just numbers
        ]
        
        for pattern in dimension_patterns:
            if re.match(pattern, text_upper):
                return TextType.DIMENSION
        
        # Room names
        room_keywords = [
            "BEDROOM", "KITCHEN", "BATHROOM", "LIVING", "DINING", "OFFICE",
            "STORAGE", "UTILITY", "GARAGE", "LOBBY", "CORRIDOR"
        ]
        
        for keyword in room_keywords:
            if keyword in text_upper:
                return TextType.ROOM_NAME
        
        # Materials
        material_keywords = [
            "CONCRETE", "STEEL", "TIMBER", "BRICK", "GLASS", "ALUMINIUM",
            "PLASTIC", "CERAMIC", "INSULATION", "FIRE", "WATERPROOF"
        ]
        
        for keyword in material_keywords:
            if keyword in text_upper:
                return TextType.MATERIAL
        
        # Specifications
        spec_keywords = [
            "FIRE RATED", "INSULATED", "WATERPROOF", "ACOUSTIC", "THERMAL",
            "STRUCTURAL", "NON-LOAD", "REINFORCED", "PRECAST"
        ]
        
        for keyword in spec_keywords:
            if keyword in text_upper:
                return TextType.SPECIFICATION
        
        return TextType.GENERAL_TEXT
    
    def _extract_text_properties(self, text: str) -> Dict[str, Any]:
        """Extract properties from text content."""
        properties = {}
        
        # Extract dimensions
        dimension_match = re.search(r'(\d+\.?\d*)\s*(MM|CM|M|FT|IN)?', text.upper())
        if dimension_match:
            value = float(dimension_match.group(1))
            unit = dimension_match.group(2) or "MM"
            properties["dimension_value"] = value
            properties["dimension_unit"] = unit
        
        # Extract numbers
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            properties["numbers"] = [float(n) for n in numbers]
        
        # Extract keywords
        keywords = re.findall(r'[A-Z]{2,}', text.upper())
        if keywords:
            properties["keywords"] = keywords
        
        return properties

class ElementTextMapper:
    """Maps extracted text to visual elements for enhanced classification."""
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
    
    def map_text_to_elements(self, 
                            elements: List[Dict[str, Any]], 
                            image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Map extracted text to visual elements.
        
        Args:
            elements: List of detected visual elements
            image: Input image
            
        Returns:
            List of elements with enhanced text mapping
        """
        # Extract text from image
        extracted_texts = self.ocr_processor.extract_text(image)
        
        # Create mappings
        mappings = self._create_text_element_mappings(elements, extracted_texts)
        
        # Enhance elements with text information
        enhanced_elements = self._enhance_elements_with_text(elements, mappings)
        
        logger.info(f"Mapped {len(mappings)} text-element relationships")
        return enhanced_elements
    
    def _create_text_element_mappings(self, 
                                     elements: List[Dict[str, Any]], 
                                     texts: List[ExtractedText]) -> List[TextElementMapping]:
        """Create mappings between text and elements based on proximity and content."""
        mappings = []
        
        for text in texts:
            for element in elements:
                element_bbox = element.get('bbox', [0, 0, 0, 0])
                
                # Calculate distance between text and element
                distance = self._calculate_distance(text.bbox, element_bbox)
                
                # Determine relationship based on distance and text type
                relationship = self._determine_relationship(text, element, distance)
                
                if relationship:
                    mapping = TextElementMapping(
                        text=text,
                        element_bbox=element_bbox,
                        distance=distance,
                        confidence=text.confidence,
                        relationship=relationship
                    )
                    mappings.append(mapping)
        
        return mappings
    
    def _calculate_distance(self, text_bbox: List[int], element_bbox: List[int]) -> float:
        """Calculate distance between text and element bounding boxes."""
        # Calculate center points
        text_center_x = (text_bbox[0] + text_bbox[2]) / 2
        text_center_y = (text_bbox[1] + text_bbox[3]) / 2
        
        element_center_x = (element_bbox[0] + element_bbox[2]) / 2
        element_center_y = (element_bbox[1] + element_bbox[3]) / 2
        
        # Euclidean distance
        distance = np.sqrt((text_center_x - element_center_x)**2 + (text_center_y - element_center_y)**2)
        
        return distance
    
    def _determine_relationship(self, 
                               text: ExtractedText, 
                               element: Dict[str, Any], 
                               distance: float) -> Optional[str]:
        """Determine the relationship between text and element."""
        element_type = element.get('type', '')
        
        # Distance threshold (adjust based on image scale)
        distance_threshold = 100  # pixels
        
        if distance > distance_threshold:
            return None
        
        # Element label relationship
        if text.text_type == TextType.ELEMENT_LABEL:
            # Check if text matches element type
            text_upper = text.text.upper()
            if element_type.upper() in text_upper or text_upper in element_type.upper():
                return "label"
        
        # Dimension relationship
        if text.text_type == TextType.DIMENSION:
            return "dimension"
        
        # Material relationship
        if text.text_type == TextType.MATERIAL:
            return "material"
        
        # Specification relationship
        if text.text_type == TextType.SPECIFICATION:
            return "specification"
        
        # Room name relationship (for room elements)
        if text.text_type == TextType.ROOM_NAME and element_type == "room":
            return "room_name"
        
        # General nearby text
        if distance < distance_threshold / 2:
            return "nearby"
        
        return None
    
    def _enhance_elements_with_text(self, 
                                   elements: List[Dict[str, Any]], 
                                   mappings: List[TextElementMapping]) -> List[Dict[str, Any]]:
        """Enhance elements with mapped text information."""
        enhanced_elements = []
        
        for element in elements:
            element_bbox = element.get('bbox', [0, 0, 0, 0])
            
            # Find mappings for this element
            element_mappings = [m for m in mappings if m.element_bbox == element_bbox]
            
            # Create enhanced element
            enhanced_element = element.copy()
            enhanced_element['text_mappings'] = []
            enhanced_element['enhanced_properties'] = element.get('properties', {}).copy()
            
            for mapping in element_mappings:
                text_info = {
                    'text': mapping.text.text,
                    'text_type': mapping.text.text_type.value,
                    'confidence': mapping.text.confidence,
                    'relationship': mapping.relationship,
                    'distance': mapping.distance,
                    'properties': mapping.text.properties
                }
                
                enhanced_element['text_mappings'].append(text_info)
                
                # Enhance element properties based on text
                self._enhance_element_properties(enhanced_element, mapping)
            
            enhanced_elements.append(enhanced_element)
        
        return enhanced_elements
    
    def _enhance_element_properties(self, element: Dict[str, Any], mapping: TextElementMapping):
        """Enhance element properties based on mapped text."""
        properties = element.get('enhanced_properties', {})
        
        if mapping.relationship == "label":
            properties['labeled_type'] = mapping.text.text
            properties['label_confidence'] = mapping.text.confidence
        
        elif mapping.relationship == "dimension":
            if 'dimensions' not in properties:
                properties['dimensions'] = []
            properties['dimensions'].append({
                'value': mapping.text.properties.get('dimension_value'),
                'unit': mapping.text.properties.get('dimension_unit'),
                'text': mapping.text.text
            })
        
        elif mapping.relationship == "material":
            if 'materials' not in properties:
                properties['materials'] = []
            properties['materials'].append(mapping.text.text)
        
        elif mapping.relationship == "specification":
            if 'specifications' not in properties:
                properties['specifications'] = []
            properties['specifications'].append(mapping.text.text)
        
        elif mapping.relationship == "room_name":
            properties['room_name'] = mapping.text.text
        
        element['enhanced_properties'] = properties

class OCREnhancedProcessor:
    """Main processor that combines OCR and element detection for enhanced results."""
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.text_mapper = ElementTextMapper()
    
    def process_drawing_with_ocr(self, 
                                image: np.ndarray, 
                                elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process drawing with OCR enhancement.
        
        Args:
            image: Input image
            elements: List of detected elements
            
        Returns:
            Dictionary with enhanced processing results
        """
        try:
            # Extract text
            extracted_texts = self.ocr_processor.extract_text(image)
            
            # Map text to elements
            enhanced_elements = self.text_mapper.map_text_to_elements(elements, image)
            
            # Analyze text patterns
            text_analysis = self._analyze_text_patterns(extracted_texts)
            
            # Enhance element classification
            final_elements = self._enhance_element_classification(enhanced_elements, text_analysis)
            
            return {
                'elements': final_elements,
                'extracted_texts': [self._text_to_dict(t) for t in extracted_texts],
                'text_analysis': text_analysis,
                'total_elements': len(final_elements),
                'total_texts': len(extracted_texts),
                'processing_method': 'ocr_enhanced'
            }
            
        except Exception as e:
            logger.error(f"Error in OCR-enhanced processing: {e}")
            return {
                'elements': elements,
                'extracted_texts': [],
                'text_analysis': {},
                'total_elements': len(elements),
                'total_texts': 0,
                'processing_method': 'fallback',
                'error': str(e)
            }
    
    def _analyze_text_patterns(self, texts: List[ExtractedText]) -> Dict[str, Any]:
        """Analyze patterns in extracted text."""
        analysis = {
            'text_types': {},
            'common_keywords': {},
            'dimensions': [],
            'materials': [],
            'specifications': []
        }
        
        for text in texts:
            # Count text types
            text_type = text.text_type.value
            analysis['text_types'][text_type] = analysis['text_types'].get(text_type, 0) + 1
            
            # Collect keywords
            keywords = text.properties.get('keywords', [])
            for keyword in keywords:
                analysis['common_keywords'][keyword] = analysis['common_keywords'].get(keyword, 0) + 1
            
            # Collect dimensions
            if text.text_type == TextType.DIMENSION:
                analysis['dimensions'].append({
                    'text': text.text,
                    'value': text.properties.get('dimension_value'),
                    'unit': text.properties.get('dimension_unit')
                })
            
            # Collect materials
            if text.text_type == TextType.MATERIAL:
                analysis['materials'].append(text.text)
            
            # Collect specifications
            if text.text_type == TextType.SPECIFICATION:
                analysis['specifications'].append(text.text)
        
        return analysis
    
    def _enhance_element_classification(self, 
                                       elements: List[Dict[str, Any]], 
                                       text_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance element classification based on text analysis."""
        enhanced_elements = []
        
        for element in elements:
            enhanced_element = element.copy()
            
            # Enhance confidence based on text mappings
            text_mappings = element.get('text_mappings', [])
            if text_mappings:
                # Increase confidence if element has relevant text
                base_confidence = element.get('confidence', 0.5)
                text_confidence_boost = min(0.2, len(text_mappings) * 0.05)
                enhanced_element['confidence'] = min(1.0, base_confidence + text_confidence_boost)
                
                # Enhance element type based on text labels
                for mapping in text_mappings:
                    if mapping['relationship'] == 'label':
                        enhanced_element['enhanced_type'] = mapping['text']
                        break
            
            enhanced_elements.append(enhanced_element)
        
        return enhanced_elements
    
    def _text_to_dict(self, text: ExtractedText) -> Dict[str, Any]:
        """Convert ExtractedText to dictionary for JSON serialization."""
        return {
            'text': text.text,
            'bbox': text.bbox,
            'confidence': text.confidence,
            'text_type': text.text_type.value,
            'properties': text.properties
        }

def main():
    """Example usage of the OCR-enhanced processing system."""
    # Initialize processor
    processor = OCREnhancedProcessor()
    
    print("OCR → Element Mapping System")
    print("=" * 50)
    
    # Test with a sample image (if available)
    # image = cv2.imread("sample_drawing.jpg")
    # elements = [...]  # Sample elements
    # results = processor.process_drawing_with_ocr(image, elements)
    # print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main() 