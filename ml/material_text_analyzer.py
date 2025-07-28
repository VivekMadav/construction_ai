"""
Material Text Analyzer for Construction Drawings
Scans drawings for material-related text and associates materials with detected elements
"""

import re
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MaterialText:
    """Represents detected material-related text"""
    text: str
    material_type: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    position: Tuple[int, int]  # center point

@dataclass
class MaterialElement:
    """Represents an element with associated material"""
    element_type: str
    material: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    text_references: List[str]

class MaterialTextAnalyzer:
    """Analyzes construction drawings for material-related text"""
    
    def __init__(self):
        # Material keywords and patterns
        self.material_patterns = {
            'concrete': {
                'keywords': [
                    'concrete', 'conc', 'c', 'rc', 'reinforced', 'precast', 'cast',
                    'c20', 'c25', 'c30', 'c35', 'c40', 'c50', 'c60',  # concrete grades
                    'fcu', 'fck', 'fct',  # concrete strength notations
                    'slab', 'beam', 'column', 'foundation', 'footing', 'pad',
                    'wall', 'shear wall', 'core wall',
                    'grade', 'strength', 'mix', 'proportion'
                ],
                'patterns': [
                    r'C\d+',  # Concrete grades like C25, C30
                    r'fcu\s*\d+',  # Concrete strength like fcu 25
                    r'fck\s*\d+',  # Characteristic strength
                    r'concrete\s+grade\s+\d+',
                    r'reinforced\s+concrete',
                    r'precast\s+concrete'
                ]
            },
            'steel': {
                'keywords': [
                    'steel', 's', 'structural steel', 'mild steel', 'ms',
                    'high yield', 'hy', 'fy', 'tensile', 'yield strength',
                    'i-beam', 'h-beam', 'ub', 'uc', 'rsj', 'rolled steel',
                    'plate', 'angle', 'channel', 'tube', 'pipe', 'hollow',
                    'grade', 's275', 's355', 's420', 's460',  # steel grades
                    'fe', 'fe250', 'fe415', 'fe500', 'fe550'  # Indian steel grades
                ],
                'patterns': [
                    r'S\d+',  # Steel grades like S275, S355
                    r'UB\s*\d+x\d+',  # Universal Beam sizes
                    r'UC\s*\d+x\d+',  # Universal Column sizes
                    r'RSJ\s*\d+x\d+',  # Rolled Steel Joist
                    r'steel\s+grade\s+\d+',
                    r'structural\s+steel',
                    r'mild\s+steel'
                ]
            },
            'timber': {
                'keywords': [
                    'timber', 'wood', 'lumber', 't', 'softwood', 'hardwood',
                    'pine', 'spruce', 'oak', 'mahogany', 'teak', 'cedar',
                    'plywood', 'mdf', 'osb', 'particle board', 'chipboard',
                    'glulam', 'lvl', 'clt', 'cross laminated',
                    'grade', 'strength', 'c16', 'c24', 'c27', 'c30',  # timber grades
                    'truss', 'joist', 'rafter', 'purlin', 'stud'
                ],
                'patterns': [
                    r'C\d+',  # Timber grades like C16, C24
                    r'timber\s+grade\s+\d+',
                    r'wood\s+grade\s+\d+',
                    r'glulam\s+\d+x\d+',
                    r'lvl\s+\d+x\d+',
                    r'clt\s+\d+x\d+'
                ]
            }
        }
        
        # Common construction abbreviations
        self.construction_abbreviations = {
            'conc': 'concrete',
            'rc': 'reinforced concrete',
            'ms': 'mild steel',
            'hy': 'high yield',
            'ub': 'universal beam',
            'uc': 'universal column',
            'rsj': 'rolled steel joist',
            'glulam': 'glued laminated timber',
            'lvl': 'laminated veneer lumber',
            'clt': 'cross laminated timber',
            'mdf': 'medium density fibreboard',
            'osb': 'oriented strand board'
        }
        
        # Element-material associations
        self.element_material_associations = {
            'beam': ['concrete', 'steel', 'timber'],
            'column': ['concrete', 'steel', 'timber'],
            'slab': ['concrete', 'timber'],
            'wall': ['concrete', 'steel', 'timber'],
            'foundation': ['concrete'],
            'truss': ['steel', 'timber'],
            'joist': ['steel', 'timber'],
            'rafter': ['timber'],
            'purlin': ['steel', 'timber'],
            'stud': ['timber', 'steel']
        }

    def extract_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Extract potential text regions from the image using contour detection
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply preprocessing
            # Remove noise
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            min_area = 100  # Minimum area for text regions
            max_area = 10000  # Maximum area for text regions
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    # Filter based on aspect ratio (text is usually rectangular)
                    if 0.1 < aspect_ratio < 10:
                        text_regions.append((x, y, w, h))
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Error extracting text regions: {e}")
            return []

    def detect_material_text(self, image: np.ndarray, text_regions: List[Tuple[int, int, int, int]]) -> List[MaterialText]:
        """
        Detect material-related text in the specified regions
        """
        material_texts = []
        
        for x, y, w, h in text_regions:
            # Extract region
            region = image[y:y+h, x:x+w]
            
            # Simple text detection using edge detection
            if len(region.shape) == 3:
                gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            else:
                gray_region = region
            
            # Apply edge detection
            edges = cv2.Canny(gray_region, 50, 150)
            
            # Count edge pixels (proxy for text density)
            edge_density = np.sum(edges > 0) / (w * h)
            
            if edge_density > 0.01:  # Threshold for text-like regions
                # Analyze region for material keywords
                material_info = self._analyze_region_for_materials(region)
                
                if material_info:
                    material_texts.append(MaterialText(
                        text=material_info['text'],
                        material_type=material_info['material'],
                        confidence=material_info['confidence'],
                        bbox=(x, y, w, h),
                        position=(x + w//2, y + h//2)
                    ))
        
        return material_texts

    def _analyze_region_for_materials(self, region: np.ndarray) -> Optional[Dict]:
        """
        Analyze a region for material-related text
        """
        try:
            # Convert to grayscale for processing
            if len(region.shape) == 3:
                gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            else:
                gray = region
            
            # Apply OCR-like processing (simplified)
            # In a real implementation, you'd use Tesseract or PaddleOCR here
            # For now, we'll use pattern matching on edge features
            
            # Create a simple text representation
            # This is a placeholder - in practice you'd use actual OCR
            text_features = self._extract_text_features(gray)
            
            # Check against material patterns
            best_match = None
            highest_confidence = 0
            
            for material, patterns in self.material_patterns.items():
                confidence = self._calculate_material_confidence(text_features, patterns)
                if confidence > highest_confidence and confidence > 0.3:
                    highest_confidence = confidence
                    best_match = {
                        'text': f"{material}_detected",
                        'material': material,
                        'confidence': confidence
                    }
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error analyzing region for materials: {e}")
            return None

    def _extract_text_features(self, gray_image: np.ndarray) -> Dict:
        """
        Extract features that might indicate text content
        """
        features = {}
        
        # Edge density
        edges = cv2.Canny(gray_image, 50, 150)
        features['edge_density'] = np.sum(edges > 0) / edges.size
        
        # Horizontal and vertical line density
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        horizontal_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, vertical_kernel)
        
        features['horizontal_density'] = np.sum(horizontal_lines > 0) / horizontal_lines.size
        features['vertical_density'] = np.sum(vertical_lines > 0) / vertical_lines.size
        
        # Texture features
        features['texture_variance'] = np.var(gray_image)
        features['texture_mean'] = np.mean(gray_image)
        
        return features

    def _calculate_material_confidence(self, features: Dict, patterns: Dict) -> float:
        """
        Calculate confidence score for material detection
        """
        confidence = 0.0
        
        # Base confidence on edge density (text-like regions)
        if features['edge_density'] > 0.02:
            confidence += 0.3
        
        # Higher confidence for regions with good texture variance
        if 0.1 < features['texture_variance'] < 0.9:
            confidence += 0.2
        
        # Additional confidence for balanced horizontal/vertical features
        if features['horizontal_density'] > 0.01 or features['vertical_density'] > 0.01:
            confidence += 0.2
        
        return min(confidence, 1.0)

    def associate_materials_with_elements(self, 
                                       elements: List[Dict], 
                                       material_texts: List[MaterialText]) -> List[MaterialElement]:
        """
        Associate detected material text with detected elements
        """
        material_elements = []
        
        for element in elements:
            element_bbox = element.get('bbox', (0, 0, 0, 0))
            element_type = element.get('element_type', 'unknown')
            
            # Find nearby material text
            nearby_materials = self._find_nearby_materials(element_bbox, material_texts)
            
            # Determine most likely material
            best_material = self._determine_element_material(
                element_type, nearby_materials, element_bbox
            )
            
            material_elements.append(MaterialElement(
                element_type=element_type,
                material=best_material['material'],
                confidence=best_material['confidence'],
                bbox=element_bbox,
                text_references=best_material['references']
            ))
        
        return material_elements

    def _find_nearby_materials(self, element_bbox: Tuple[int, int, int, int], 
                              material_texts: List[MaterialText]) -> List[MaterialText]:
        """
        Find material text that is spatially close to the element
        """
        nearby_materials = []
        element_center = (element_bbox[0] + element_bbox[2]//2, 
                         element_bbox[1] + element_bbox[3]//2)
        
        for material_text in material_texts:
            distance = self._calculate_distance(element_center, material_text.position)
            
            # Consider materials within 200 pixels as "nearby"
            if distance < 200:
                nearby_materials.append(material_text)
        
        return nearby_materials

    def _calculate_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def _determine_element_material(self, element_type: str, 
                                   nearby_materials: List[MaterialText],
                                   element_bbox: Tuple[int, int, int, int]) -> Dict:
        """
        Determine the most likely material for an element
        """
        # Default materials based on element type
        default_materials = {
            'beam': 'concrete',
            'column': 'concrete', 
            'slab': 'concrete',
            'wall': 'concrete',
            'foundation': 'concrete',
            'truss': 'steel',
            'joist': 'steel',
            'rafter': 'timber',
            'stud': 'timber'
        }
        
        # If we have nearby material text, use that
        if nearby_materials:
            # Find the closest material text
            closest_material = min(nearby_materials, 
                                 key=lambda m: self._calculate_distance(
                                     (element_bbox[0] + element_bbox[2]//2, 
                                      element_bbox[1] + element_bbox[3]//2),
                                     m.position
                                 ))
            
            return {
                'material': closest_material.material_type,
                'confidence': closest_material.confidence,
                'references': [closest_material.text]
            }
        
        # Otherwise use default based on element type
        default_material = default_materials.get(element_type, 'concrete')
        return {
            'material': default_material,
            'confidence': 0.5,  # Lower confidence for default assignment
            'references': []
        }

    def analyze_drawing_materials(self, image_path: str) -> Dict:
        """
        Complete analysis of a drawing for material detection
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Extract text regions
            text_regions = self.extract_text_regions(image)
            logger.info(f"Extracted {len(text_regions)} potential text regions")
            
            # Detect material text
            material_texts = self.detect_material_text(image, text_regions)
            logger.info(f"Detected {len(material_texts)} material-related text regions")
            
            # Analyze material distribution
            material_distribution = self._analyze_material_distribution(material_texts)
            
            return {
                'material_texts': material_texts,
                'text_regions': text_regions,
                'material_distribution': material_distribution,
                'total_regions': len(text_regions),
                'material_regions': len(material_texts)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing drawing materials: {e}")
            return {
                'material_texts': [],
                'text_regions': [],
                'material_distribution': {},
                'total_regions': 0,
                'material_regions': 0,
                'error': str(e)
            }

    def _analyze_material_distribution(self, material_texts: List[MaterialText]) -> Dict:
        """Analyze the distribution of detected materials"""
        distribution = {'concrete': 0, 'steel': 0, 'timber': 0}
        
        for material_text in material_texts:
            if material_text.material_type in distribution:
                distribution[material_text.material_type] += 1
        
        return distribution

def test_material_analyzer():
    """Test the material text analyzer"""
    analyzer = MaterialTextAnalyzer()
    
    # Test with a sample image path
    # You would replace this with an actual drawing path
    test_image_path = "backend/uploads/1/page_1.png"
    
    if Path(test_image_path).exists():
        results = analyzer.analyze_drawing_materials(test_image_path)
        print("Material Analysis Results:")
        print(f"Total text regions: {results['total_regions']}")
        print(f"Material regions: {results['material_regions']}")
        print(f"Material distribution: {results['material_distribution']}")
        
        for material_text in results['material_texts']:
            print(f"Material: {material_text.material_type}, "
                  f"Confidence: {material_text.confidence:.2f}, "
                  f"Position: {material_text.position}")
    else:
        print(f"Test image not found: {test_image_path}")

if __name__ == "__main__":
    test_material_analyzer() 