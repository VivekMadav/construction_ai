"""
Enhanced Inference System for Construction AI

This module combines multi-head inference with OCR text mapping for
significantly improved element detection and classification accuracy.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import cv2
import sys

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from multi_head_inference import MultiHeadInferenceSystem, Discipline
from ocr_element_mapping import OCREnhancedProcessor

logger = logging.getLogger(__name__)

class EnhancedInferenceSystem:
    """Enhanced inference system combining multi-head detection with OCR mapping."""
    
    def __init__(self, models_dir: str = "ml/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.multi_head_system = MultiHeadInferenceSystem(models_dir)
        self.ocr_processor = OCREnhancedProcessor()
        
        logger.info("Enhanced inference system initialized successfully")
    
    def detect_elements_enhanced(self, 
                                image: np.ndarray, 
                                discipline: Discipline,
                                confidence_threshold: float = 0.5,
                                use_ocr: bool = True) -> Dict[str, Any]:
        """
        Detect elements with OCR enhancement.
        
        Args:
            image: Input image
            discipline: Discipline for detection
            confidence_threshold: Minimum confidence for detections
            use_ocr: Whether to use OCR enhancement
            
        Returns:
            Dictionary with enhanced detection results
        """
        try:
            # Step 1: Multi-head inference detection
            logger.info(f"Performing multi-head inference for {discipline.value}")
            detection_results = self.multi_head_system.detect_elements(
                image, discipline, confidence_threshold
            )
            
            # Convert DetectionResult objects to dictionaries
            elements = []
            for result in detection_results:
                element = {
                    "id": f"{result.element_type}_{len(elements):03d}",
                    "type": result.element_type,
                    "bbox": result.bbox,
                    "confidence": result.confidence,
                    "properties": result.properties,
                    "discipline": result.discipline.value
                }
                elements.append(element)
            
            # Step 2: OCR enhancement (if enabled)
            if use_ocr and elements:
                logger.info("Applying OCR enhancement")
                enhanced_results = self.ocr_processor.process_drawing_with_ocr(image, elements)
                
                return {
                    "elements": enhanced_results['elements'],
                    "extracted_texts": enhanced_results['extracted_texts'],
                    "text_analysis": enhanced_results['text_analysis'],
                    "total_elements": enhanced_results['total_elements'],
                    "total_texts": enhanced_results['total_texts'],
                    "discipline": discipline.value,
                    "processing_method": enhanced_results['processing_method'],
                    "enhancement_applied": True
                }
            else:
                # Return basic results without OCR
                return {
                    "elements": elements,
                    "extracted_texts": [],
                    "text_analysis": {},
                    "total_elements": len(elements),
                    "total_texts": 0,
                    "discipline": discipline.value,
                    "processing_method": "multi_head_inference",
                    "enhancement_applied": False
                }
                
        except Exception as e:
            logger.error(f"Error in enhanced inference: {e}")
            return {
                "elements": [],
                "extracted_texts": [],
                "text_analysis": {},
                "total_elements": 0,
                "total_texts": 0,
                "discipline": discipline.value,
                "processing_method": "error",
                "enhancement_applied": False,
                "error": str(e)
            }
    
    def detect_all_disciplines_enhanced(self, 
                                       image: np.ndarray,
                                       confidence_threshold: float = 0.5,
                                       use_ocr: bool = True) -> Dict[str, Any]:
        """
        Detect elements for all disciplines with OCR enhancement.
        
        Args:
            image: Input image
            confidence_threshold: Minimum confidence for detections
            use_ocr: Whether to use OCR enhancement
            
        Returns:
            Dictionary with results for all disciplines
        """
        all_results = {}
        combined_elements = []
        all_texts = []
        combined_text_analysis = {}
        
        for discipline in Discipline:
            logger.info(f"Processing discipline: {discipline.value}")
            results = self.detect_elements_enhanced(
                image, discipline, confidence_threshold, use_ocr
            )
            
            all_results[discipline.value] = results
            combined_elements.extend(results['elements'])
            all_texts.extend(results['extracted_texts'])
            
            # Merge text analysis
            for key, value in results['text_analysis'].items():
                if key not in combined_text_analysis:
                    combined_text_analysis[key] = value
                elif isinstance(value, dict):
                    # Merge dictionaries
                    for sub_key, sub_value in value.items():
                        if sub_key not in combined_text_analysis[key]:
                            combined_text_analysis[key][sub_key] = sub_value
                        elif isinstance(sub_value, (int, float)):
                            combined_text_analysis[key][sub_key] += sub_value
                        elif isinstance(sub_value, list):
                            combined_text_analysis[key][sub_key].extend(sub_value)
                elif isinstance(value, list):
                    combined_text_analysis[key].extend(value)
        
        return {
            "discipline_results": all_results,
            "combined_elements": combined_elements,
            "combined_texts": all_texts,
            "combined_text_analysis": combined_text_analysis,
            "total_elements": len(combined_elements),
            "total_texts": len(all_texts),
            "processing_method": "enhanced_multi_discipline",
            "enhancement_applied": use_ocr
        }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        stats = {
            "multi_head_system": self.multi_head_system.get_discipline_statistics(),
            "ocr_available": hasattr(self.ocr_processor.ocr_processor, 'ocr') and self.ocr_processor.ocr_processor.ocr is not None,
            "enhancement_capabilities": {
                "text_extraction": True,
                "text_element_mapping": True,
                "element_classification_enhancement": True,
                "confidence_boosting": True
            }
        }
        
        return stats
    
    def save_enhanced_results(self, 
                             results: Dict[str, Any], 
                             output_path: str):
        """Save enhanced detection results to JSON file."""
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Enhanced results saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving enhanced results: {e}")
    
    def analyze_drawing_content(self, 
                               image: np.ndarray, 
                               discipline: Discipline) -> Dict[str, Any]:
        """
        Perform comprehensive drawing content analysis.
        
        Args:
            image: Input image
            discipline: Discipline for analysis
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        try:
            # Get enhanced detection results
            results = self.detect_elements_enhanced(image, discipline, use_ocr=True)
            
            # Perform additional analysis
            analysis = {
                "element_distribution": self._analyze_element_distribution(results['elements']),
                "text_patterns": results['text_analysis'],
                "spatial_analysis": self._analyze_spatial_distribution(results['elements']),
                "confidence_analysis": self._analyze_confidence_distribution(results['elements']),
                "enhancement_impact": self._analyze_enhancement_impact(results)
            }
            
            return {
                "detection_results": results,
                "content_analysis": analysis,
                "summary": self._generate_analysis_summary(results, analysis)
            }
            
        except Exception as e:
            logger.error(f"Error in drawing content analysis: {e}")
            return {
                "error": str(e),
                "detection_results": {},
                "content_analysis": {},
                "summary": "Analysis failed"
            }
    
    def _analyze_element_distribution(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of element types."""
        distribution = {}
        
        for element in elements:
            element_type = element.get('type', 'unknown')
            distribution[element_type] = distribution.get(element_type, 0) + 1
        
        return {
            "element_counts": distribution,
            "total_elements": len(elements),
            "unique_types": len(distribution)
        }
    
    def _analyze_spatial_distribution(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze spatial distribution of elements."""
        if not elements:
            return {"error": "No elements to analyze"}
        
        # Calculate bounding box of all elements
        all_x1 = [elem.get('bbox', [0, 0, 0, 0])[0] for elem in elements]
        all_y1 = [elem.get('bbox', [0, 0, 0, 0])[1] for elem in elements]
        all_x2 = [elem.get('bbox', [0, 0, 0, 0])[2] for elem in elements]
        all_y2 = [elem.get('bbox', [0, 0, 0, 0])[3] for elem in elements]
        
        return {
            "bounding_box": [min(all_x1), min(all_y1), max(all_x2), max(all_y2)],
            "center_of_mass": [
                sum(all_x1 + all_x2) / (2 * len(elements)),
                sum(all_y1 + all_y2) / (2 * len(elements))
            ],
            "spread": {
                "width": max(all_x2) - min(all_x1),
                "height": max(all_y2) - min(all_y1)
            }
        }
    
    def _analyze_confidence_distribution(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze confidence distribution of elements."""
        if not elements:
            return {"error": "No elements to analyze"}
        
        confidences = [elem.get('confidence', 0) for elem in elements]
        
        return {
            "mean_confidence": np.mean(confidences),
            "median_confidence": np.median(confidences),
            "std_confidence": np.std(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "high_confidence_count": len([c for c in confidences if c > 0.8]),
            "medium_confidence_count": len([c for c in confidences if 0.5 <= c <= 0.8]),
            "low_confidence_count": len([c for c in confidences if c < 0.5])
        }
    
    def _analyze_enhancement_impact(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the impact of OCR enhancement."""
        elements = results.get('elements', [])
        texts = results.get('extracted_texts', [])
        
        enhanced_elements = [elem for elem in elements if elem.get('text_mappings')]
        
        return {
            "elements_with_text": len(enhanced_elements),
            "total_elements": len(elements),
            "enhancement_ratio": len(enhanced_elements) / len(elements) if elements else 0,
            "total_texts": len(texts),
            "text_element_ratio": len(texts) / len(elements) if elements else 0
        }
    
    def _generate_analysis_summary(self, 
                                  results: Dict[str, Any], 
                                  analysis: Dict[str, Any]) -> str:
        """Generate a human-readable analysis summary."""
        total_elements = results.get('total_elements', 0)
        total_texts = results.get('total_texts', 0)
        discipline = results.get('discipline', 'unknown')
        
        element_dist = analysis.get('element_distribution', {})
        unique_types = element_dist.get('unique_types', 0)
        
        confidence_analysis = analysis.get('confidence_analysis', {})
        mean_confidence = confidence_analysis.get('mean_confidence', 0)
        
        enhancement_impact = analysis.get('enhancement_impact', {})
        enhancement_ratio = enhancement_impact.get('enhancement_ratio', 0)
        
        summary = f"""
Drawing Analysis Summary:
- Discipline: {discipline}
- Total Elements Detected: {total_elements}
- Unique Element Types: {unique_types}
- Text Elements Extracted: {total_texts}
- Average Confidence: {mean_confidence:.2f}
- OCR Enhancement Applied: {enhancement_ratio:.1%} of elements
- Processing Method: {results.get('processing_method', 'unknown')}
        """.strip()
        
        return summary

def main():
    """Example usage of the enhanced inference system."""
    # Initialize system
    enhanced_system = EnhancedInferenceSystem()
    
    # Get system statistics
    stats = enhanced_system.get_system_statistics()
    print("Enhanced Inference System Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Example: Process an image
    # image = cv2.imread("sample_drawing.jpg")
    # results = enhanced_system.detect_elements_enhanced(image, Discipline.ARCHITECTURAL)
    # enhanced_system.save_enhanced_results(results, "enhanced_results.json")

if __name__ == "__main__":
    main() 