"""
Enhanced Element Measurement with Cross-Drawing References

This module provides enhanced element measurement capabilities by analyzing
cross-drawing references to improve accuracy and completeness of measurements.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from drawing_reference_analyzer import DrawingReferenceAnalyzer, CrossDrawingElement, DrawingReference

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeasurementType(Enum):
    """Types of measurements."""
    LENGTH = "length"
    WIDTH = "width"
    HEIGHT = "height"
    DEPTH = "depth"
    AREA = "area"
    VOLUME = "volume"
    ANGLE = "angle"
    DIAMETER = "diameter"
    THICKNESS = "thickness"

@dataclass
class EnhancedMeasurement:
    """Enhanced measurement with cross-drawing validation."""
    measurement_type: MeasurementType
    value: float
    unit: str
    confidence: float
    source_drawings: List[str]
    cross_reference_confidence: float
    measurement_method: str  # "direct", "calculated", "inferred", "cross_reference"
    notes: Optional[str] = None

@dataclass
class EnhancedElement:
    """Enhanced element with cross-drawing measurements."""
    element_id: str
    element_type: str
    primary_drawing_id: str
    reference_drawings: List[str]
    measurements: Dict[MeasurementType, EnhancedMeasurement]
    overall_confidence: float
    cross_reference_confidence: float
    measurement_completeness: float

class EnhancedElementMeasurement:
    """Enhanced element measurement system using cross-drawing references."""
    
    def __init__(self, base_path: str = "ml/data"):
        self.base_path = Path(base_path)
        self.reference_analyzer = DrawingReferenceAnalyzer(base_path)
        
        # Measurement validation rules
        self.validation_rules = {
            "tolerance": 0.05,  # 5% tolerance for cross-reference validation
            "min_confidence": 0.6,
            "min_cross_reference_confidence": 0.7
        }
        
        # Element measurement templates
        self.measurement_templates = {
            "wall": [MeasurementType.LENGTH, MeasurementType.HEIGHT, MeasurementType.THICKNESS],
            "beam": [MeasurementType.LENGTH, MeasurementType.WIDTH, MeasurementType.HEIGHT],
            "column": [MeasurementType.LENGTH, MeasurementType.WIDTH, MeasurementType.HEIGHT],
            "slab": [MeasurementType.LENGTH, MeasurementType.WIDTH, MeasurementType.THICKNESS],
            "foundation": [MeasurementType.LENGTH, MeasurementType.WIDTH, MeasurementType.DEPTH],
            "door": [MeasurementType.LENGTH, MeasurementType.HEIGHT, MeasurementType.THICKNESS],
            "window": [MeasurementType.LENGTH, MeasurementType.HEIGHT, MeasurementType.THICKNESS],
            "pipe": [MeasurementType.LENGTH, MeasurementType.DIAMETER],
            "duct": [MeasurementType.LENGTH, MeasurementType.WIDTH, MeasurementType.HEIGHT]
        }
    
    def measure_element_with_cross_references(self, 
                                            primary_drawing_id: str,
                                            element_data: Dict,
                                            reference_drawing_ids: List[str] = None) -> EnhancedElement:
        """
        Measure element using cross-drawing references for improved accuracy.
        
        Args:
            primary_drawing_id: ID of the primary drawing
            element_data: Element data from primary drawing
            reference_drawing_ids: List of reference drawing IDs
            
        Returns:
            Enhanced element with cross-drawing measurements
        """
        try:
            # Get reference drawings if not provided
            if reference_drawing_ids is None:
                reference_drawing_ids = self._get_reference_drawings(primary_drawing_id)
            
            # Analyze cross-drawing references
            cross_elements = self.reference_analyzer.analyze_cross_drawing_elements(
                primary_drawing_id, reference_drawing_ids
            )
            
            # Find matching cross-element
            matching_cross_element = self._find_matching_cross_element(
                element_data, cross_elements
            )
            
            # Perform enhanced measurements
            enhanced_measurements = self._perform_enhanced_measurements(
                element_data, matching_cross_element, reference_drawing_ids
            )
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(enhanced_measurements)
            cross_reference_confidence = self._calculate_cross_reference_confidence(enhanced_measurements)
            measurement_completeness = self._calculate_measurement_completeness(enhanced_measurements, element_data)
            
            # Create enhanced element
            enhanced_element = EnhancedElement(
                element_id=element_data.get('id', f"{primary_drawing_id}_element"),
                element_type=element_data.get('type', 'unknown'),
                primary_drawing_id=primary_drawing_id,
                reference_drawings=reference_drawing_ids,
                measurements=enhanced_measurements,
                overall_confidence=overall_confidence,
                cross_reference_confidence=cross_reference_confidence,
                measurement_completeness=measurement_completeness
            )
            
            logger.info(f"Enhanced measurement completed for element {enhanced_element.element_id}")
            return enhanced_element
            
        except Exception as e:
            logger.error(f"Error in enhanced element measurement: {e}")
            # Return basic element if enhanced measurement fails
            return self._create_basic_element(element_data, primary_drawing_id)
    
    def _get_reference_drawings(self, primary_drawing_id: str) -> List[str]:
        """Get reference drawings for a primary drawing."""
        try:
            # Get references from the reference analyzer
            references = self.reference_analyzer.reference_database.get(primary_drawing_id, [])
            
            # Extract unique target drawing IDs
            reference_drawings = list(set([ref.target_drawing_id for ref in references]))
            
            # Filter out unknown or invalid references
            valid_references = [ref for ref in reference_drawings if ref != "unknown"]
            
            return valid_references
            
        except Exception as e:
            logger.error(f"Error getting reference drawings: {e}")
            return []
    
    def _find_matching_cross_element(self, 
                                   element_data: Dict, 
                                   cross_elements: List[CrossDrawingElement]) -> Optional[CrossDrawingElement]:
        """Find matching cross-element for the given element."""
        for cross_elem in cross_elements:
            if self._elements_match(element_data, cross_elem):
                return cross_elem
        
        return None
    
    def _elements_match(self, element_data: Dict, cross_element: CrossDrawingElement) -> bool:
        """Check if elements match across drawings."""
        # Compare element types
        if element_data.get('type') != cross_element.element_type:
            return False
        
        # Compare positions (normalized)
        if 'bbox' in element_data and hasattr(cross_element, 'bbox'):
            position_similarity = self._calculate_position_similarity(
                element_data['bbox'], cross_element.bbox
            )
            if position_similarity < 0.7:
                return False
        
        return True
    
    def _calculate_position_similarity(self, bbox1: List[int], bbox2: List[int]) -> float:
        """Calculate position similarity between bounding boxes."""
        if len(bbox1) != 4 or len(bbox2) != 4:
            return 0.0
        
        # Calculate center points
        center1 = [(bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2]
        center2 = [(bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2]
        
        # Calculate distance
        distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        # Normalize distance (assuming image size of 1000x1000)
        normalized_distance = distance / 1000.0
        
        # Convert to similarity (1.0 = perfect match, 0.0 = no match)
        similarity = max(0.0, 1.0 - normalized_distance)
        
        return similarity
    
    def _perform_enhanced_measurements(self, 
                                     element_data: Dict,
                                     cross_element: Optional[CrossDrawingElement],
                                     reference_drawings: List[str]) -> Dict[MeasurementType, EnhancedMeasurement]:
        """Perform enhanced measurements using cross-drawing information."""
        enhanced_measurements = {}
        
        # Get measurement template for element type
        element_type = element_data.get('type', 'unknown')
        measurement_template = self.measurement_templates.get(element_type, [])
        
        # Perform measurements for each required type
        for measurement_type in measurement_template:
            enhanced_measurement = self._measure_single_dimension(
                element_data, cross_element, measurement_type, reference_drawings
            )
            
            if enhanced_measurement:
                enhanced_measurements[measurement_type] = enhanced_measurement
        
        return enhanced_measurements
    
    def _measure_single_dimension(self, 
                                element_data: Dict,
                                cross_element: Optional[CrossDrawingElement],
                                measurement_type: MeasurementType,
                                reference_drawings: List[str]) -> Optional[EnhancedMeasurement]:
        """Measure a single dimension with cross-drawing validation."""
        
        # Get primary measurement
        primary_value = self._extract_primary_measurement(element_data, measurement_type)
        
        if primary_value is None:
            return None
        
        # Get cross-reference measurements
        cross_reference_values = []
        if cross_element and cross_element.measurements:
            cross_value = self._extract_cross_reference_measurement(
                cross_element.measurements, measurement_type
            )
            if cross_value is not None:
                cross_reference_values.append(cross_value)
        
        # Validate and combine measurements
        validated_value, confidence, cross_ref_confidence = self._validate_and_combine_measurements(
            primary_value, cross_reference_values
        )
        
        # Determine measurement method
        measurement_method = self._determine_measurement_method(
            primary_value, cross_reference_values
        )
        
        # Create enhanced measurement
        enhanced_measurement = EnhancedMeasurement(
            measurement_type=measurement_type,
            value=validated_value,
            unit=primary_value.get('unit', 'm'),
            confidence=confidence,
            source_drawings=[element_data.get('drawing_id', 'primary')] + reference_drawings,
            cross_reference_confidence=cross_ref_confidence,
            measurement_method=measurement_method,
            notes=self._generate_measurement_notes(primary_value, cross_reference_values)
        )
        
        return enhanced_measurement
    
    def _extract_primary_measurement(self, element_data: Dict, measurement_type: MeasurementType) -> Optional[Dict]:
        """Extract primary measurement from element data."""
        measurements = element_data.get('measurements', {})
        
        # Look for measurement in various formats
        measurement_key = measurement_type.value
        
        if measurement_key in measurements:
            return {
                'value': measurements[measurement_key],
                'unit': measurements.get(f'{measurement_key}_unit', 'm'),
                'confidence': measurements.get(f'{measurement_key}_confidence', 0.8)
            }
        
        # Try alternative keys
        alternative_keys = {
            MeasurementType.LENGTH: ['length', 'l', 'long'],
            MeasurementType.WIDTH: ['width', 'w', 'wide'],
            MeasurementType.HEIGHT: ['height', 'h', 'high'],
            MeasurementType.DEPTH: ['depth', 'd', 'deep'],
            MeasurementType.AREA: ['area', 'a'],
            MeasurementType.VOLUME: ['volume', 'v'],
            MeasurementType.THICKNESS: ['thickness', 't', 'thick']
        }
        
        for alt_key in alternative_keys.get(measurement_type, []):
            if alt_key in measurements:
                return {
                    'value': measurements[alt_key],
                    'unit': measurements.get(f'{alt_key}_unit', 'm'),
                    'confidence': measurements.get(f'{alt_key}_confidence', 0.8)
                }
        
        return None
    
    def _extract_cross_reference_measurement(self, 
                                           cross_measurements: Dict[str, Any], 
                                           measurement_type: MeasurementType) -> Optional[Dict]:
        """Extract measurement from cross-reference data."""
        measurement_key = measurement_type.value
        
        if measurement_key in cross_measurements:
            return {
                'value': cross_measurements[measurement_key],
                'unit': cross_measurements.get(f'{measurement_key}_unit', 'm'),
                'confidence': cross_measurements.get(f'{measurement_key}_confidence', 0.8)
            }
        
        return None
    
    def _validate_and_combine_measurements(self, 
                                         primary_value: Dict,
                                         cross_reference_values: List[Dict]) -> Tuple[float, float, float]:
        """Validate and combine measurements from multiple sources."""
        
        if not cross_reference_values:
            # No cross-references, use primary value
            return primary_value['value'], primary_value['confidence'], 0.0
        
        # Check if measurements are consistent
        all_values = [primary_value['value']] + [ref['value'] for ref in cross_reference_values]
        
        # Calculate mean and standard deviation
        mean_value = np.mean(all_values)
        std_value = np.std(all_values)
        
        # Check tolerance
        tolerance = self.validation_rules['tolerance']
        max_deviation = mean_value * tolerance
        
        if std_value <= max_deviation:
            # Measurements are consistent
            validated_value = mean_value
            confidence = min(1.0, primary_value['confidence'] + 0.1)  # Boost confidence
            cross_ref_confidence = 0.9
        else:
            # Measurements are inconsistent, use primary value
            validated_value = primary_value['value']
            confidence = primary_value['confidence']
            cross_ref_confidence = 0.3
        
        return validated_value, confidence, cross_ref_confidence
    
    def _determine_measurement_method(self, 
                                    primary_value: Dict,
                                    cross_reference_values: List[Dict]) -> str:
        """Determine the measurement method used."""
        if not cross_reference_values:
            return "direct"
        elif len(cross_reference_values) == 1:
            return "cross_reference"
        else:
            return "calculated"
    
    def _generate_measurement_notes(self, 
                                  primary_value: Dict,
                                  cross_reference_values: List[Dict]) -> str:
        """Generate notes about the measurement."""
        notes = []
        
        if cross_reference_values:
            notes.append(f"Cross-referenced with {len(cross_reference_values)} additional drawings")
            
            # Check for consistency
            all_values = [primary_value['value']] + [ref['value'] for ref in cross_reference_values]
            std_value = np.std(all_values)
            
            if std_value < primary_value['value'] * 0.05:
                notes.append("Measurements are highly consistent across drawings")
            elif std_value < primary_value['value'] * 0.1:
                notes.append("Measurements are consistent across drawings")
            else:
                notes.append("Measurements show some variation across drawings")
        else:
            notes.append("Measurement from primary drawing only")
        
        return "; ".join(notes)
    
    def _calculate_overall_confidence(self, measurements: Dict[MeasurementType, EnhancedMeasurement]) -> float:
        """Calculate overall confidence for the element."""
        if not measurements:
            return 0.0
        
        confidences = [measurement.confidence for measurement in measurements.values()]
        return np.mean(confidences)
    
    def _calculate_cross_reference_confidence(self, measurements: Dict[MeasurementType, EnhancedMeasurement]) -> float:
        """Calculate cross-reference confidence for the element."""
        if not measurements:
            return 0.0
        
        cross_ref_confidences = [measurement.cross_reference_confidence for measurement in measurements.values()]
        return np.mean(cross_ref_confidences)
    
    def _calculate_measurement_completeness(self, 
                                          measurements: Dict[MeasurementType, EnhancedMeasurement],
                                          element_data: Dict) -> float:
        """Calculate measurement completeness for the element."""
        element_type = element_data.get('type', 'unknown')
        required_measurements = self.measurement_templates.get(element_type, [])
        
        if not required_measurements:
            return 1.0  # No template, assume complete
        
        # Calculate completeness
        measured_types = set(measurements.keys())
        required_types = set(required_measurements)
        
        completeness = len(measured_types.intersection(required_types)) / len(required_types)
        return completeness
    
    def _create_basic_element(self, element_data: Dict, primary_drawing_id: str) -> EnhancedElement:
        """Create basic element when enhanced measurement fails."""
        basic_measurements = {}
        
        # Convert existing measurements to enhanced format
        if 'measurements' in element_data:
            for key, value in element_data['measurements'].items():
                try:
                    measurement_type = MeasurementType(key)
                    basic_measurements[measurement_type] = EnhancedMeasurement(
                        measurement_type=measurement_type,
                        value=value,
                        unit=element_data['measurements'].get(f'{key}_unit', 'm'),
                        confidence=element_data['measurements'].get(f'{key}_confidence', 0.6),
                        source_drawings=[primary_drawing_id],
                        cross_reference_confidence=0.0,
                        measurement_method="direct"
                    )
                except ValueError:
                    # Skip invalid measurement types
                    continue
        
        return EnhancedElement(
            element_id=element_data.get('id', f"{primary_drawing_id}_element"),
            element_type=element_data.get('type', 'unknown'),
            primary_drawing_id=primary_drawing_id,
            reference_drawings=[],
            measurements=basic_measurements,
            overall_confidence=element_data.get('confidence', 0.6),
            cross_reference_confidence=0.0,
            measurement_completeness=self._calculate_measurement_completeness(basic_measurements, element_data)
        )
    
    def generate_enhanced_report(self, enhanced_element: EnhancedElement) -> Dict[str, Any]:
        """Generate enhanced measurement report."""
        report = {
            "element_id": enhanced_element.element_id,
            "element_type": enhanced_element.element_type,
            "primary_drawing": enhanced_element.primary_drawing_id,
            "reference_drawings": enhanced_element.reference_drawings,
            "overall_confidence": enhanced_element.overall_confidence,
            "cross_reference_confidence": enhanced_element.cross_reference_confidence,
            "measurement_completeness": enhanced_element.measurement_completeness,
            "measurements": {},
            "summary": {}
        }
        
        # Add detailed measurements
        for measurement_type, measurement in enhanced_element.measurements.items():
            report["measurements"][measurement_type.value] = {
                "value": measurement.value,
                "unit": measurement.unit,
                "confidence": measurement.confidence,
                "cross_reference_confidence": measurement.cross_reference_confidence,
                "measurement_method": measurement.measurement_method,
                "source_drawings": measurement.source_drawings,
                "notes": measurement.notes
            }
        
        # Generate summary
        report["summary"] = {
            "total_measurements": len(enhanced_element.measurements),
            "high_confidence_measurements": len([
                m for m in enhanced_element.measurements.values() 
                if m.confidence >= 0.8
            ]),
            "cross_referenced_measurements": len([
                m for m in enhanced_element.measurements.values() 
                if m.cross_reference_confidence > 0.5
            ]),
            "recommendations": self._generate_recommendations(enhanced_element)
        }
        
        return report
    
    def _generate_recommendations(self, enhanced_element: EnhancedElement) -> List[str]:
        """Generate recommendations based on measurement analysis."""
        recommendations = []
        
        # Check measurement completeness
        if enhanced_element.measurement_completeness < 0.8:
            recommendations.append("Consider additional drawings for complete measurements")
        
        # Check cross-reference confidence
        if enhanced_element.cross_reference_confidence < 0.5:
            recommendations.append("Cross-reference validation could improve accuracy")
        
        # Check individual measurement confidence
        low_confidence_measurements = [
            m for m in enhanced_element.measurements.values() 
            if m.confidence < 0.7
        ]
        
        if low_confidence_measurements:
            recommendations.append(f"Review {len(low_confidence_measurements)} low-confidence measurements")
        
        # Check for missing critical measurements
        element_type = enhanced_element.element_type
        required_measurements = self.measurement_templates.get(element_type, [])
        measured_types = set(enhanced_element.measurements.keys())
        missing_measurements = set(required_measurements) - measured_types
        
        if missing_measurements:
            recommendations.append(f"Missing measurements: {[m.value for m in missing_measurements]}")
        
        return recommendations

def main():
    """Main function for testing enhanced element measurement."""
    measurer = EnhancedElementMeasurement()
    
    # Example usage
    print("Enhanced Element Measurement system initialized")
    
    # Example element data
    element_data = {
        "id": "wall_001",
        "type": "wall",
        "drawing_id": "drawing_001",
        "confidence": 0.8,
        "measurements": {
            "length": 5.0,
            "length_unit": "m",
            "length_confidence": 0.8,
            "height": 3.0,
            "height_unit": "m",
            "height_confidence": 0.7
        }
    }
    
    # Measure element with cross-references
    # enhanced_element = measurer.measure_element_with_cross_references(
    #     "drawing_001", element_data, ["drawing_002", "drawing_003"]
    # )
    
    # Generate report
    # report = measurer.generate_enhanced_report(enhanced_element)
    # print(f"Enhanced measurement report: {json.dumps(report, indent=2)}")

if __name__ == "__main__":
    main() 