"""
Enhanced Material Detection System
Combines element detection with material text analysis for improved accuracy
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
from material_text_analyzer import MaterialTextAnalyzer, MaterialElement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedElement:
    """Enhanced element with material and confidence information"""
    element_type: str
    material: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    area: float
    aspect_ratio: float
    material_confidence: float
    text_references: List[str]
    properties: Dict

class EnhancedMaterialDetector:
    """Enhanced material detection system for construction drawings"""
    
    def __init__(self):
        self.material_analyzer = MaterialTextAnalyzer()
        
        # Material-specific detection parameters
        self.material_detection_params = {
            'concrete': {
                'color_ranges': [
                    # Gray concrete
                    ([100, 100, 100], [200, 200, 200]),
                    # Light gray
                    ([150, 150, 150], [220, 220, 220]),
                    # Dark gray
                    ([50, 50, 50], [150, 150, 150])
                ],
                'texture_patterns': ['smooth', 'rough', 'aggregate'],
                'element_types': ['beam', 'column', 'slab', 'wall', 'foundation']
            },
            'steel': {
                'color_ranges': [
                    # Metallic gray
                    ([80, 80, 100], [180, 180, 200]),
                    # Dark steel
                    ([40, 40, 60], [120, 120, 140]),
                    # Light steel
                    ([160, 160, 180], [220, 220, 240])
                ],
                'texture_patterns': ['smooth', 'metallic', 'reflective'],
                'element_types': ['beam', 'column', 'truss', 'joist', 'purlin']
            },
            'timber': {
                'color_ranges': [
                    # Wood brown
                    ([80, 60, 40], [180, 160, 140]),
                    # Light wood
                    ([140, 120, 100], [220, 200, 180]),
                    # Dark wood
                    ([40, 30, 20], [120, 100, 80])
                ],
                'texture_patterns': ['grain', 'natural', 'organic'],
                'element_types': ['beam', 'column', 'joist', 'rafter', 'stud', 'truss']
            }
        }
        
        # Element detection parameters
        self.element_detection_params = {
            'beam': {
                'min_aspect_ratio': 2.0,
                'max_aspect_ratio': 8.0,
                'min_area': 1000,
                'max_area': 50000
            },
            'column': {
                'min_aspect_ratio': 0.5,
                'max_aspect_ratio': 2.0,
                'min_area': 2000,
                'max_area': 30000
            },
            'slab': {
                'min_aspect_ratio': 0.8,
                'max_aspect_ratio': 1.5,
                'min_area': 5000,
                'max_area': 100000
            },
            'wall': {
                'min_aspect_ratio': 3.0,
                'max_aspect_ratio': 15.0,
                'min_area': 2000,
                'max_area': 80000
            },
            'foundation': {
                'min_aspect_ratio': 0.5,
                'max_aspect_ratio': 3.0,
                'min_area': 3000,
                'max_area': 60000
            }
        }

    def detect_elements_with_materials(self, image_path: str, discipline: str = "structural") -> List[EnhancedElement]:
        """
        Detect elements with material information
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Analyze materials in the drawing
            material_analysis = self.material_analyzer.analyze_drawing_materials(image_path)
            
            # Detect basic elements
            basic_elements = self._detect_basic_elements(image, discipline)
            
            # Enhance elements with material information
            enhanced_elements = self._enhance_elements_with_materials(
                basic_elements, material_analysis, image
            )
            
            # Apply material-specific refinements
            refined_elements = self._apply_material_refinements(enhanced_elements, image)
            
            logger.info(f"Detected {len(refined_elements)} enhanced elements with materials")
            return refined_elements
            
        except Exception as e:
            logger.error(f"Error in enhanced material detection: {e}")
            return []

    def _detect_basic_elements(self, image: np.ndarray, discipline: str) -> List[Dict]:
        """
        Detect basic elements using geometric properties
        """
        elements = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply preprocessing
        # Remove noise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply edge detection
        edges = cv2.Canny(denoised, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 500:  # Filter out very small contours
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # Classify element type based on geometric properties
            element_type = self._classify_element_type(area, aspect_ratio, w, h, discipline)
            
            if element_type:
                elements.append({
                    'element_type': element_type,
                    'bbox': (x, y, w, h),
                    'area': area,
                    'aspect_ratio': aspect_ratio,
                    'confidence': 0.7  # Base confidence
                })
        
        return elements

    def _classify_element_type(self, area: float, aspect_ratio: float, 
                              width: int, height: int, discipline: str) -> Optional[str]:
        """
        Classify element type based on geometric properties and discipline
        """
        if discipline == "structural":
            # Structural elements
            if 0.5 < aspect_ratio < 2.0 and area > 2000:
                return "column"
            elif aspect_ratio > 2.0 and area > 1000:
                return "beam"
            elif 0.8 < aspect_ratio < 1.5 and area > 5000:
                return "slab"
            elif aspect_ratio > 3.0 and area > 2000:
                return "wall"
            elif 0.5 < aspect_ratio < 3.0 and area > 3000:
                return "foundation"
        
        elif discipline == "architectural":
            # Architectural elements
            if aspect_ratio > 3.0 and area > 500:
                return "wall"
            elif 0.5 < aspect_ratio < 2.0 and 1000 < area < 10000:
                return "door"
            elif 0.5 < aspect_ratio < 2.0 and 500 < area < 5000:
                return "window"
            elif 0.8 < aspect_ratio < 1.2 and area > 2000:
                return "room"
        
        return None

    def _enhance_elements_with_materials(self, basic_elements: List[Dict], 
                                       material_analysis: Dict, 
                                       image: np.ndarray) -> List[EnhancedElement]:
        """
        Enhance basic elements with material information
        """
        enhanced_elements = []
        material_texts = material_analysis.get('material_texts', [])
        
        for element in basic_elements:
            # Find nearby material text
            nearby_materials = self._find_nearby_materials(
                element['bbox'], material_texts
            )
            
            # Determine material based on nearby text and visual analysis
            material_info = self._determine_element_material(
                element, nearby_materials, image
            )
            
            # Create enhanced element
            enhanced_element = EnhancedElement(
                element_type=element['element_type'],
                material=material_info['material'],
                confidence=element['confidence'],
                bbox=element['bbox'],
                area=element['area'],
                aspect_ratio=element['aspect_ratio'],
                material_confidence=material_info['confidence'],
                text_references=material_info['references'],
                properties=material_info['properties']
            )
            
            enhanced_elements.append(enhanced_element)
        
        return enhanced_elements

    def _find_nearby_materials(self, element_bbox: Tuple[int, int, int, int], 
                              material_texts: List) -> List:
        """
        Find material text that is spatially close to the element
        """
        nearby_materials = []
        element_center = (element_bbox[0] + element_bbox[2]//2, 
                         element_bbox[1] + element_bbox[3]//2)
        
        for material_text in material_texts:
            distance = self._calculate_distance(element_center, material_text.position)
            
            # Consider materials within 300 pixels as "nearby"
            if distance < 300:
                nearby_materials.append(material_text)
        
        return nearby_materials

    def _calculate_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def _determine_element_material(self, element: Dict, nearby_materials: List, 
                                   image: np.ndarray) -> Dict:
        """
        Determine material for an element using text analysis and visual features
        """
        element_bbox = element['bbox']
        element_type = element['element_type']
        
        # Extract region for visual analysis
        x, y, w, h = element_bbox
        region = image[y:y+h, x:x+w]
        
        # Analyze visual features
        visual_features = self._analyze_visual_features(region)
        
        # If we have nearby material text, use that as primary
        if nearby_materials:
            closest_material = min(nearby_materials, 
                                 key=lambda m: self._calculate_distance(
                                     (x + w//2, y + h//2), m.position
                                 ))
            
            # Combine text-based and visual-based confidence
            text_confidence = closest_material.confidence
            visual_confidence = self._calculate_visual_material_confidence(
                visual_features, closest_material.material_type
            )
            
            combined_confidence = (text_confidence + visual_confidence) / 2
            
            return {
                'material': closest_material.material_type,
                'confidence': combined_confidence,
                'references': [closest_material.text],
                'properties': visual_features
            }
        
        # Otherwise, use visual analysis and element type defaults
        visual_material = self._determine_material_from_visual(visual_features)
        default_material = self._get_default_material_for_element(element_type)
        
        # Use visual analysis if confidence is high, otherwise use default
        if visual_material['confidence'] > 0.6:
            material = visual_material['material']
            confidence = visual_material['confidence']
        else:
            material = default_material
            confidence = 0.5
        
        return {
            'material': material,
            'confidence': confidence,
            'references': [],
            'properties': visual_features
        }

    def _analyze_visual_features(self, region: np.ndarray) -> Dict:
        """
        Analyze visual features of a region to determine material
        """
        features = {}
        
        # Color analysis
        if len(region.shape) == 3:
            # Convert to different color spaces
            hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(region, cv2.COLOR_BGR2LAB)
            
            # Calculate color statistics
            features['mean_color'] = np.mean(region, axis=(0, 1))
            features['std_color'] = np.std(region, axis=(0, 1))
            features['mean_hue'] = np.mean(hsv[:, :, 0])
            features['mean_saturation'] = np.mean(hsv[:, :, 1])
            features['mean_value'] = np.mean(hsv[:, :, 2])
            features['mean_lightness'] = np.mean(lab[:, :, 0])
        
        # Texture analysis
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if len(region.shape) == 3 else region
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        features['edge_density'] = np.sum(edges > 0) / edges.size
        
        # Local binary pattern (simplified)
        features['texture_variance'] = np.var(gray)
        features['texture_mean'] = np.mean(gray)
        
        # Gradient analysis
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        features['gradient_magnitude'] = np.mean(np.sqrt(grad_x**2 + grad_y**2))
        
        return features

    def _calculate_visual_material_confidence(self, features: Dict, material_type: str) -> float:
        """
        Calculate confidence for material based on visual features
        """
        confidence = 0.0
        
        if material_type == 'concrete':
            # Concrete typically has gray colors and moderate texture
            if 100 < features['mean_color'][0] < 200:
                confidence += 0.3
            if 0.01 < features['edge_density'] < 0.1:
                confidence += 0.2
            if 0.05 < features['texture_variance'] < 0.3:
                confidence += 0.2
        
        elif material_type == 'steel':
            # Steel typically has metallic gray colors and smooth texture
            if 80 < features['mean_color'][0] < 180:
                confidence += 0.3
            if features['edge_density'] < 0.05:
                confidence += 0.2
            if features['texture_variance'] < 0.1:
                confidence += 0.2
        
        elif material_type == 'timber':
            # Timber typically has brown colors and grain texture
            if features['mean_color'][2] > features['mean_color'][0]:  # More red than blue
                confidence += 0.3
            if features['edge_density'] > 0.05:
                confidence += 0.2
            if features['texture_variance'] > 0.1:
                confidence += 0.2
        
        return min(confidence, 1.0)

    def _determine_material_from_visual(self, features: Dict) -> Dict:
        """
        Determine material from visual features alone
        """
        confidences = {
            'concrete': self._calculate_visual_material_confidence(features, 'concrete'),
            'steel': self._calculate_visual_material_confidence(features, 'steel'),
            'timber': self._calculate_visual_material_confidence(features, 'timber')
        }
        
        best_material = max(confidences, key=confidences.get)
        return {
            'material': best_material,
            'confidence': confidences[best_material]
        }

    def _get_default_material_for_element(self, element_type: str) -> str:
        """
        Get default material for element type
        """
        defaults = {
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
        return defaults.get(element_type, 'concrete')

    def _apply_material_refinements(self, elements: List[EnhancedElement], 
                                   image: np.ndarray) -> List[EnhancedElement]:
        """
        Apply material-specific refinements to improve accuracy
        """
        refined_elements = []
        
        for element in elements:
            # Apply material-specific refinements
            refined_element = self._refine_element_material(element, image)
            refined_elements.append(refined_element)
        
        return refined_elements

    def _refine_element_material(self, element: EnhancedElement, 
                                image: np.ndarray) -> EnhancedElement:
        """
        Refine material detection for a specific element
        """
        # Extract element region
        x, y, w, h = element.bbox
        region = image[y:y+h, x:x+w]
        
        # Apply material-specific refinements
        if element.material == 'concrete':
            # Check for reinforcement patterns
            if self._detect_reinforcement_patterns(region):
                element.properties['reinforced'] = True
                element.material_confidence += 0.1
        
        elif element.material == 'steel':
            # Check for steel section patterns
            if self._detect_steel_section_patterns(region):
                element.properties['section_type'] = 'rolled'
                element.material_confidence += 0.1
        
        elif element.material == 'timber':
            # Check for wood grain patterns
            if self._detect_wood_grain_patterns(region):
                element.properties['grain_detected'] = True
                element.material_confidence += 0.1
        
        # Ensure confidence doesn't exceed 1.0
        element.material_confidence = min(element.material_confidence, 1.0)
        
        return element

    def _detect_reinforcement_patterns(self, region: np.ndarray) -> bool:
        """Detect reinforcement patterns in concrete elements"""
        # Simplified reinforcement detection
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if len(region.shape) == 3 else region
        
        # Look for regular grid patterns (rebar)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
        
        return lines is not None and len(lines) > 5

    def _detect_steel_section_patterns(self, region: np.ndarray) -> bool:
        """Detect steel section patterns"""
        # Simplified steel section detection
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if len(region.shape) == 3 else region
        
        # Look for I-beam or H-beam patterns
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check for characteristic steel section shapes
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small contours
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.5 < aspect_ratio < 2.0:  # Typical steel section ratios
                    return True
        
        return False

    def _detect_wood_grain_patterns(self, region: np.ndarray) -> bool:
        """Detect wood grain patterns"""
        # Simplified wood grain detection
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if len(region.shape) == 3 else region
        
        # Look for horizontal grain patterns
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        
        grain_density = np.sum(horizontal_lines > 0) / horizontal_lines.size
        return grain_density > 0.02  # Threshold for grain detection

def test_enhanced_material_detection():
    """Test the enhanced material detection system"""
    detector = EnhancedMaterialDetector()
    
    # Test with a sample image
    test_image_path = "backend/uploads/1/page_1.png"
    
    if Path(test_image_path).exists():
        enhanced_elements = detector.detect_elements_with_materials(test_image_path, "structural")
        
        print("Enhanced Material Detection Results:")
        print(f"Detected {len(enhanced_elements)} elements with materials")
        
        for element in enhanced_elements:
            print(f"Element: {element.element_type}")
            print(f"  Material: {element.material}")
            print(f"  Confidence: {element.confidence:.2f}")
            print(f"  Material Confidence: {element.material_confidence:.2f}")
            print(f"  Area: {element.area:.0f}")
            print(f"  Text References: {element.text_references}")
            print("---")
    else:
        print(f"Test image not found: {test_image_path}")

if __name__ == "__main__":
    test_enhanced_material_detection() 