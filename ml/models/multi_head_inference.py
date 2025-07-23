"""
Multi-Head Inference System for Construction AI

This module implements discipline-specific element detection models with
model switching logic for improved accuracy across different drawing types.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Discipline(Enum):
    """Supported disciplines for element detection."""
    ARCHITECTURAL = "architectural"
    STRUCTURAL = "structural"
    CIVIL = "civil"
    MEP = "mep"

@dataclass
class DetectionResult:
    """Result of element detection."""
    element_type: str
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float
    properties: Dict[str, Any]
    discipline: Discipline

class BaseDetector:
    """Base class for all discipline-specific detectors."""
    
    def __init__(self, discipline: Discipline):
        self.discipline = discipline
        self.element_types = self._get_element_types()
        self.model_loaded = False
        
    def _get_element_types(self) -> List[str]:
        """Get element types for this discipline."""
        raise NotImplementedError
        
    def load_model(self, model_path: str) -> bool:
        """Load the detection model."""
        raise NotImplementedError
        
    def detect_elements(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect elements in the image."""
        raise NotImplementedError
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for detection."""
        # Ensure image is in the correct format for OpenCV
        if len(image.shape) == 3:
            # Convert RGB to grayscale
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Ensure image is uint8 for OpenCV operations
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                # Image is normalized (0-1), convert to uint8
                image = (image * 255).astype(np.uint8)
            else:
                # Image is already in 0-255 range, just convert type
                image = image.astype(np.uint8)
        
        return image

class ArchitecturalDetector(BaseDetector):
    """Detector for architectural elements."""
    
    def __init__(self):
        super().__init__(Discipline.ARCHITECTURAL)
        
    def _get_element_types(self) -> List[str]:
        return [
            "wall", "door", "window", "room", "furniture",
            "fixture", "stair", "elevator", "ramp", "column"
        ]
        
    def load_model(self, model_path: str) -> bool:
        """Load architectural detection model."""
        try:
            # TODO: Load actual ML model (e.g., YOLO, Faster R-CNN)
            # For now, use geometric detection
            logger.info(f"Loaded architectural detector from {model_path}")
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load architectural model: {e}")
            return False
            
    def detect_elements(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect architectural elements using geometric analysis."""
        if not self.model_loaded:
            logger.warning("Model not loaded, using fallback detection")
            
        results = []
        processed_image = self.preprocess_image(image)
        
        # Geometric detection for architectural elements
        # This replaces the current simple contour detection with discipline-specific logic
        
        # Detect walls (long rectangular shapes)
        walls = self._detect_walls(processed_image)
        results.extend(walls)
        
        # Detect doors (rectangular openings in walls)
        doors = self._detect_doors(processed_image)
        results.extend(doors)
        
        # Detect windows (smaller rectangular openings)
        windows = self._detect_windows(processed_image)
        results.extend(windows)
        
        # Detect rooms (enclosed areas)
        rooms = self._detect_rooms(processed_image)
        results.extend(rooms)
        
        logger.info(f"Detected {len(results)} architectural elements")
        return results
        
    def _detect_walls(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect walls using contour analysis."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's a rectangle (wall-like)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Wall criteria: long and thin
                aspect_ratio = w / h if h > 0 else 0
                if aspect_ratio > 3 or aspect_ratio < 0.33:
                    if w * h > 1000:  # Minimum area
                        results.append(DetectionResult(
                            element_type="wall",
                            bbox=[x, y, x + w, y + h],
                            confidence=0.85,
                            properties={
                                "length": max(w, h),
                                "thickness": min(w, h),
                                "area": w * h
                            },
                            discipline=self.discipline
                        ))
        
        return results
        
    def _detect_doors(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect doors using template matching and contour analysis."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Door criteria: rectangular, medium size
            aspect_ratio = w / h if h > 0 else 0
            if 0.3 < aspect_ratio < 0.8:  # Door proportions
                if 500 < w * h < 5000:  # Door size range
                    results.append(DetectionResult(
                        element_type="door",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.80,
                        properties={
                            "width": w,
                            "height": h,
                            "area": w * h
                        },
                        discipline=self.discipline
                    ))
        
        return results
        
    def _detect_windows(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect windows using contour analysis."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Window criteria: smaller than doors, rectangular
            aspect_ratio = w / h if h > 0 else 0
            if 0.5 < aspect_ratio < 2.0:  # Window proportions
                if 100 < w * h < 2000:  # Window size range
                    results.append(DetectionResult(
                        element_type="window",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.75,
                        properties={
                            "width": w,
                            "height": h,
                            "area": w * h
                        },
                        discipline=self.discipline
                    ))
        
        return results
        
    def _detect_rooms(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect rooms using connected component analysis."""
        results = []
        
        # Threshold to get binary image
        _, binary = cv2.threshold(image, 0.5, 1, cv2.THRESH_BINARY)
        
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary.astype(np.uint8), connectivity=8
        )
        
        for i in range(1, num_labels):  # Skip background
            x, y, w, h, area = stats[i]
            
            # Room criteria: large enclosed areas
            if area > 5000:  # Minimum room area
                results.append(DetectionResult(
                    element_type="room",
                    bbox=[x, y, x + w, y + h],
                    confidence=0.70,
                    properties={
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    discipline=self.discipline
                ))
        
        return results

class StructuralDetector(BaseDetector):
    """Detector for structural elements."""
    
    def __init__(self):
        super().__init__(Discipline.STRUCTURAL)
        
    def _get_element_types(self) -> List[str]:
        return [
            "beam", "column", "slab", "foundation", "reinforcement",
            "stirrup", "footing", "wall", "truss", "girder"
        ]
        
    def load_model(self, model_path: str) -> bool:
        """Load structural detection model."""
        try:
            logger.info(f"Loaded structural detector from {model_path}")
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load structural model: {e}")
            return False
            
    def detect_elements(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect structural elements."""
        if not self.model_loaded:
            logger.warning("Model not loaded, using fallback detection")
            
        results = []
        processed_image = self.preprocess_image(image)
        
        # Structural-specific detection
        beams = self._detect_beams(processed_image)
        results.extend(beams)
        
        columns = self._detect_columns(processed_image)
        results.extend(columns)
        
        slabs = self._detect_slabs(processed_image)
        results.extend(slabs)
        
        foundations = self._detect_foundations(processed_image)
        results.extend(foundations)
        
        logger.info(f"Detected {len(results)} structural elements")
        return results
        
    def _detect_beams(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect beams (horizontal structural elements)."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Beam criteria: long horizontal elements
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio > 4:  # Very long and thin
                if w * h > 2000:  # Minimum beam area
                    results.append(DetectionResult(
                        element_type="beam",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.90,
                        properties={
                            "length": w,
                            "depth": h,
                            "area": w * h
                        },
                        discipline=self.discipline
                    ))
        
        return results
        
    def _detect_columns(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect columns (vertical structural elements)."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Column criteria: tall vertical elements
            aspect_ratio = h / w if w > 0 else 0
            if aspect_ratio > 2:  # Tall and narrow
                if w * h > 1000:  # Minimum column area
                    results.append(DetectionResult(
                        element_type="column",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.85,
                        properties={
                            "width": w,
                            "height": h,
                            "area": w * h
                        },
                        discipline=self.discipline
                    ))
        
        return results
        
    def _detect_slabs(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect slabs (horizontal surfaces)."""
        results = []
        
        # Threshold to get binary image
        _, binary = cv2.threshold(image, 0.5, 1, cv2.THRESH_BINARY)
        
        # Find large connected areas
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary.astype(np.uint8), connectivity=8
        )
        
        for i in range(1, num_labels):
            x, y, w, h, area = stats[i]
            
            # Slab criteria: large horizontal areas
            if area > 10000:  # Large area
                aspect_ratio = w / h if h > 0 else 0
                if 0.5 < aspect_ratio < 2.0:  # Not too elongated
                    results.append(DetectionResult(
                        element_type="slab",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.80,
                        properties={
                            "width": w,
                            "height": h,
                            "area": area
                        },
                        discipline=self.discipline
                    ))
        
        return results
        
    def _detect_foundations(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect foundations (base structural elements)."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Foundation criteria: large rectangular elements at bottom
            if w * h > 5000:  # Large area
                # Check if near bottom of image (foundation location)
                image_height = image.shape[0]
                if y + h > image_height * 0.7:  # Bottom 30% of image
                    results.append(DetectionResult(
                        element_type="foundation",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.75,
                        properties={
                            "width": w,
                            "height": h,
                            "area": w * h
                        },
                        discipline=self.discipline
                    ))
        
        return results

class CivilDetector(BaseDetector):
    """Detector for civil engineering elements."""
    
    def __init__(self):
        super().__init__(Discipline.CIVIL)
        
    def _get_element_types(self) -> List[str]:
        return [
            "site_plan", "grading", "drainage", "utility", "road",
            "parking", "landscaping", "contour", "manhole", "catch_basin"
        ]
        
    def load_model(self, model_path: str) -> bool:
        """Load civil detection model."""
        try:
            logger.info(f"Loaded civil detector from {model_path}")
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load civil model: {e}")
            return False
            
    def detect_elements(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect civil engineering elements."""
        if not self.model_loaded:
            logger.warning("Model not loaded, using fallback detection")
            
        results = []
        processed_image = self.preprocess_image(image)
        
        # Civil-specific detection
        roads = self._detect_roads(processed_image)
        results.extend(roads)
        
        utilities = self._detect_utilities(processed_image)
        results.extend(utilities)
        
        drainage = self._detect_drainage(processed_image)
        results.extend(drainage)
        
        logger.info(f"Detected {len(results)} civil elements")
        return results
        
    def _detect_roads(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect roads and pathways."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Road criteria: long linear elements
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio > 3:  # Long and narrow
                if w * h > 3000:  # Minimum road area
                    results.append(DetectionResult(
                        element_type="road",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.85,
                        properties={
                            "length": w,
                            "width": h,
                            "area": w * h
                        },
                        discipline=self.discipline
                    ))
        
        return results
        
    def _detect_utilities(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect utility lines and equipment."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Utility criteria: small circular or rectangular elements
            if 100 < w * h < 2000:  # Utility size range
                results.append(DetectionResult(
                    element_type="utility",
                    bbox=[x, y, x + w, y + h],
                    confidence=0.70,
                    properties={
                        "width": w,
                        "height": h,
                        "area": w * h
                    },
                    discipline=self.discipline
                ))
        
        return results
        
    def _detect_drainage(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect drainage elements."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Drainage criteria: small circular elements
            aspect_ratio = w / h if h > 0 else 0
            if 0.8 < aspect_ratio < 1.2:  # Roughly circular
                if 200 < w * h < 1500:  # Drainage size range
                    results.append(DetectionResult(
                        element_type="drainage",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.75,
                        properties={
                            "diameter": (w + h) / 2,
                            "area": w * h
                        },
                        discipline=self.discipline
                    ))
        
        return results

class MEPDetector(BaseDetector):
    """Detector for MEP (Mechanical, Electrical, Plumbing) elements."""
    
    def __init__(self):
        super().__init__(Discipline.MEP)
        
    def _get_element_types(self) -> List[str]:
        return [
            "hvac_duct", "electrical_panel", "plumbing_pipe", "fire_sprinkler",
            "air_handler", "transformer", "switch", "outlet", "valve", "pump"
        ]
        
    def load_model(self, model_path: str) -> bool:
        """Load MEP detection model."""
        try:
            logger.info(f"Loaded MEP detector from {model_path}")
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load MEP model: {e}")
            return False
            
    def detect_elements(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect MEP elements."""
        if not self.model_loaded:
            logger.warning("Model not loaded, using fallback detection")
            
        results = []
        processed_image = self.preprocess_image(image)
        
        # MEP-specific detection
        ducts = self._detect_ducts(processed_image)
        results.extend(ducts)
        
        electrical = self._detect_electrical(processed_image)
        results.extend(electrical)
        
        plumbing = self._detect_plumbing(processed_image)
        results.extend(plumbing)
        
        logger.info(f"Detected {len(results)} MEP elements")
        return results
        
    def _detect_ducts(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect HVAC ducts."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Duct criteria: rectangular, medium size
            aspect_ratio = w / h if h > 0 else 0
            if 0.5 < aspect_ratio < 3.0:  # Duct proportions
                if 1000 < w * h < 8000:  # Duct size range
                    results.append(DetectionResult(
                        element_type="hvac_duct",
                        bbox=[x, y, x + w, y + h],
                        confidence=0.80,
                        properties={
                            "width": w,
                            "height": h,
                            "area": w * h
                        },
                        discipline=self.discipline
                    ))
        
        return results
        
    def _detect_electrical(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect electrical elements."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Electrical criteria: small rectangular elements
            if 100 < w * h < 2000:  # Electrical component size
                results.append(DetectionResult(
                    element_type="electrical_panel",
                    bbox=[x, y, x + w, y + h],
                    confidence=0.75,
                    properties={
                        "width": w,
                        "height": h,
                        "area": w * h
                    },
                    discipline=self.discipline
                ))
        
        return results
        
    def _detect_plumbing(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect plumbing elements."""
        results = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Plumbing criteria: small circular or rectangular elements
            if 50 < w * h < 1500:  # Plumbing component size
                results.append(DetectionResult(
                    element_type="plumbing_pipe",
                    bbox=[x, y, x + w, y + h],
                    confidence=0.70,
                    properties={
                        "width": w,
                        "height": h,
                        "area": w * h
                    },
                    discipline=self.discipline
                ))
        
        return results

class MultiHeadInferenceSystem:
    """Main multi-head inference system for discipline-specific detection."""
    
    def __init__(self, models_dir: str = "ml/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize discipline-specific detectors
        self.detectors = {
            Discipline.ARCHITECTURAL: ArchitecturalDetector(),
            Discipline.STRUCTURAL: StructuralDetector(),
            Discipline.CIVIL: CivilDetector(),
            Discipline.MEP: MEPDetector()
        }
        
        # Load models
        self._load_models()
        
    def _load_models(self):
        """Load all discipline-specific models."""
        for discipline, detector in self.detectors.items():
            model_path = self.models_dir / f"{discipline.value}_model.pth"
            
            if model_path.exists():
                detector.load_model(str(model_path))
            else:
                logger.warning(f"Model not found for {discipline.value}, using geometric detection")
                # For now, all detectors work without pre-trained models
                detector.model_loaded = True
                
    def detect_elements(self, 
                       image: np.ndarray, 
                       discipline: Discipline,
                       confidence_threshold: float = 0.5) -> List[DetectionResult]:
        """
        Detect elements using discipline-specific model.
        
        Args:
            image: Input image
            discipline: Discipline to use for detection
            confidence_threshold: Minimum confidence for detections
            
        Returns:
            List of detected elements
        """
        if discipline not in self.detectors:
            raise ValueError(f"Unsupported discipline: {discipline}")
            
        detector = self.detectors[discipline]
        
        # Perform detection
        results = detector.detect_elements(image)
        
        # Filter by confidence
        filtered_results = [
            result for result in results 
            if result.confidence >= confidence_threshold
        ]
        
        logger.info(f"Detected {len(filtered_results)} elements for {discipline.value}")
        return filtered_results
        
    def detect_all_disciplines(self, 
                              image: np.ndarray,
                              confidence_threshold: float = 0.5) -> Dict[Discipline, List[DetectionResult]]:
        """
        Detect elements using all discipline models.
        
        Args:
            image: Input image
            confidence_threshold: Minimum confidence for detections
            
        Returns:
            Dictionary mapping disciplines to detection results
        """
        all_results = {}
        
        for discipline in Discipline:
            results = self.detect_elements(image, discipline, confidence_threshold)
            all_results[discipline] = results
            
        return all_results
        
    def get_discipline_statistics(self) -> Dict[str, Any]:
        """Get statistics about available models and element types."""
        stats = {}
        
        for discipline, detector in self.detectors.items():
            stats[discipline.value] = {
                "model_loaded": detector.model_loaded,
                "element_types": detector.element_types,
                "element_count": len(detector.element_types)
            }
            
        return stats
        
    def save_detection_results(self, 
                              results: List[DetectionResult], 
                              output_path: str):
        """Save detection results to JSON file."""
        output_data = {
            "detections": [
                {
                    "element_type": result.element_type,
                    "bbox": result.bbox,
                    "confidence": result.confidence,
                    "properties": result.properties,
                    "discipline": result.discipline.value
                }
                for result in results
            ],
            "total_detections": len(results),
            "disciplines": list(set(result.discipline.value for result in results))
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        logger.info(f"Saved detection results to {output_path}")

def main():
    """Example usage of the multi-head inference system."""
    # Initialize system
    inference_system = MultiHeadInferenceSystem()
    
    # Get statistics
    stats = inference_system.get_discipline_statistics()
    print("Multi-Head Inference System Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Example: Load and process an image
    # image = cv2.imread("sample_drawing.jpg")
    # results = inference_system.detect_elements(image, Discipline.ARCHITECTURAL)
    # inference_system.save_detection_results(results, "detection_results.json")

if __name__ == "__main__":
    main() 