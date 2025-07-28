"""
Concrete Processing Service for Construction AI

This module handles concrete element detection and volume measurement from drawings.
It extracts text descriptions of dimensions and calculates concrete volumes in m³.
"""

import os
import cv2
import numpy as np
import fitz  # PyMuPDF
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConcreteDimension:
    """Represents a concrete element with 3D dimensions"""
    length: float  # in meters
    width: float   # in meters  
    depth: float   # in meters
    volume: float  # in cubic meters
    confidence: float
    text_reference: str

@dataclass
class ConcreteElement:
    """Represents a detected concrete element"""
    element_type: str  # foundation, slab, wall, column, beam, etc.
    dimensions: ConcreteDimension
    material: str = "concrete"
    grade: str = "C25"  # default concrete grade
    location: Optional[str] = None
    description: Optional[str] = None

class ConcreteProcessor:
    """Processes drawings to detect and measure concrete elements"""
    
    def __init__(self):
        self.dimension_patterns = {
            # Common dimension patterns in construction drawings
            'thickness': [
                r'(\d+(?:\.\d+)?)\s*(?:mm|m)\s*(?:thick|thickness|t\.?)',
                r'thickness[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
                r't[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
            ],
            'depth': [
                r'(\d+(?:\.\d+)?)\s*(?:mm|m)\s*(?:deep|depth|d\.?)',
                r'depth[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
                r'd[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
            ],
            'height': [
                r'(\d+(?:\.\d+)?)\s*(?:mm|m)\s*(?:high|height|h\.?)',
                r'height[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
                r'h[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
            ],
            'width': [
                r'(\d+(?:\.\d+)?)\s*(?:mm|m)\s*(?:wide|width|w\.?)',
                r'width[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
                r'w[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
            ],
            'length': [
                r'(\d+(?:\.\d+)?)\s*(?:mm|m)\s*(?:long|length|l\.?)',
                r'length[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
                r'l[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|m)',
            ]
        }
        
        # Concrete element type patterns
        self.concrete_patterns = {
            'foundation': [
                r'foundation',
                r'footing',
                r'pad\s*foundation',
                r'strip\s*foundation',
                r'raft\s*foundation'
            ],
            'slab': [
                r'slab',
                r'floor\s*slab',
                r'ground\s*slab',
                r'suspended\s*slab',
                r'roof\s*slab'
            ],
            'wall': [
                r'wall',
                r'retaining\s*wall',
                r'shear\s*wall',
                r'core\s*wall'
            ],
            'column': [
                r'column',
                r'pillar',
                r'concrete\s*column'
            ],
            'beam': [
                r'beam',
                r'concrete\s*beam',
                r'lintel',
                r'ring\s*beam'
            ],
            'stair': [
                r'stair',
                r'staircase',
                r'steps',
                r'concrete\s*stair'
            ]
        }
        
        # Concrete grade patterns
        self.grade_patterns = [
            r'C(\d{2,3})',  # C25, C30, C40, etc.
            r'grade\s*(\d{2,3})',
            r'concrete\s*(\d{2,3})'
        ]

    def process_drawing_for_concrete(self, pdf_path: str) -> List[ConcreteElement]:
        """Process a drawing to detect concrete elements and their dimensions"""
        try:
            # Extract text from PDF
            extracted_text = self._extract_text_from_pdf(pdf_path)
            
            # Extract images from PDF for geometric detection
            images = self._extract_images_from_pdf(pdf_path)
            
            concrete_elements = []
            
            # Process text for dimension information
            text_elements = self._extract_concrete_from_text(extracted_text)
            concrete_elements.extend(text_elements)
            
            # Process images for geometric detection
            for image_path in images:
                image_elements = self._detect_concrete_in_image(image_path)
                concrete_elements.extend(image_elements)
            
            # Merge and deduplicate elements
            merged_elements = self._merge_concrete_elements(concrete_elements)
            
            logger.info(f"Detected {len(merged_elements)} concrete elements")
            return merged_elements
            
        except Exception as e:
            logger.error(f"Error processing drawing for concrete: {e}")
            return []

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from PDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def _extract_images_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract images from PDF for processing"""
        try:
            doc = fitz.open(pdf_path)
            images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        img_path = f"temp_page_{page_num}_img_{img_index}.png"
                        
                        with open(img_path, "wb") as f:
                            f.write(img_data)
                        images.append(img_path)
                    
                    pix = None
            
            doc.close()
            return images
            
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {e}")
            return []

    def _extract_concrete_from_text(self, text: str) -> List[ConcreteElement]:
        """Extract concrete elements and dimensions from text"""
        elements = []
        
        # Split text into sentences/paragraphs for processing
        text_blocks = re.split(r'[.!?\n]+', text)
        
        for block in text_blocks:
            block = block.strip()
            if not block:
                continue
                
            # Check for concrete element types
            element_type = self._identify_concrete_element_type(block)
            if not element_type:
                continue
                
            # Extract dimensions
            dimensions = self._extract_dimensions_from_text(block)
            if not dimensions:
                continue
                
            # Extract concrete grade
            grade = self._extract_concrete_grade(block)
            
            # Create concrete element
            element = ConcreteElement(
                element_type=element_type,
                dimensions=dimensions,
                grade=grade,
                description=block[:100]  # First 100 chars as description
            )
            
            elements.append(element)
        
        return elements

    def _identify_concrete_element_type(self, text: str) -> Optional[str]:
        """Identify concrete element type from text"""
        text_lower = text.lower()
        
        for element_type, patterns in self.concrete_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return element_type
        
        return None

    def _extract_dimensions_from_text(self, text: str) -> Optional[ConcreteDimension]:
        """Extract 3D dimensions from text"""
        dimensions = {}
        
        for dim_type, patterns in self.dimension_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = float(match.group(1))
                    # Convert mm to m if needed
                    if 'mm' in text[match.start():match.start()+20]:
                        value = value / 1000
                    dimensions[dim_type] = value
                    break
        
        # Need at least 2 dimensions to calculate volume
        if len(dimensions) < 2:
            return None
            
        # Calculate missing dimensions based on element type
        # For now, use reasonable defaults
        length = dimensions.get('length', dimensions.get('width', 1.0))
        width = dimensions.get('width', dimensions.get('length', 1.0))
        depth = dimensions.get('depth', dimensions.get('thickness', dimensions.get('height', 0.2)))
        
        volume = length * width * depth
        
        return ConcreteDimension(
            length=length,
            width=width,
            depth=depth,
            volume=volume,
            confidence=0.8,  # High confidence for text-based detection
            text_reference=text[:50]  # First 50 chars as reference
        )

    def _extract_concrete_grade(self, text: str) -> str:
        """Extract concrete grade from text"""
        text_lower = text.lower()
        
        for pattern in self.grade_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return f"C{match.group(1)}"
        
        return "C25"  # Default grade

    def _detect_concrete_in_image(self, image_path: str) -> List[ConcreteElement]:
        """Detect concrete elements in image using computer vision"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect contours (potential concrete elements)
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            elements = []
            
            for contour in contours:
                # Filter contours by size (remove noise)
                area = cv2.contourArea(contour)
                if area < 1000:  # Minimum area threshold
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Estimate dimensions (this is approximate)
                # In a real system, you'd need scale information from the drawing
                length = w / 100  # Approximate scale
                width = h / 100   # Approximate scale
                depth = 0.2       # Default depth for concrete elements
                
                volume = length * width * depth
                
                # Determine element type based on shape
                aspect_ratio = w / h
                if aspect_ratio > 5:
                    element_type = "beam"
                elif aspect_ratio < 0.2:
                    element_type = "wall"
                elif area > 50000:
                    element_type = "slab"
                else:
                    element_type = "foundation"
                
                dimension = ConcreteDimension(
                    length=length,
                    width=width,
                    depth=depth,
                    volume=volume,
                    confidence=0.6,  # Lower confidence for geometric detection
                    text_reference="Geometric detection"
                )
                
                element = ConcreteElement(
                    element_type=element_type,
                    dimensions=dimension,
                    grade="C25"  # Default grade
                )
                
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Error detecting concrete in image: {e}")
            return []

    def _merge_concrete_elements(self, elements: List[ConcreteElement]) -> List[ConcreteElement]:
        """Merge and deduplicate concrete elements"""
        if not elements:
            return []
        
        # Group elements by type and similar dimensions
        grouped = {}
        
        for element in elements:
            key = f"{element.element_type}_{element.grade}"
            
            if key not in grouped:
                grouped[key] = []
            
            grouped[key].append(element)
        
        # Merge similar elements
        merged = []
        
        for key, group in grouped.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                # Merge elements with similar dimensions
                total_volume = sum(e.dimensions.volume for e in group)
                avg_confidence = sum(e.dimensions.confidence for e in group) / len(group)
                
                # Use the first element as template
                template = group[0]
                merged_dimension = ConcreteDimension(
                    length=template.dimensions.length,
                    width=template.dimensions.width,
                    depth=template.dimensions.depth,
                    volume=total_volume,
                    confidence=avg_confidence,
                    text_reference=f"Merged {len(group)} elements"
                )
                
                merged_element = ConcreteElement(
                    element_type=template.element_type,
                    dimensions=merged_dimension,
                    grade=template.grade,
                    description=f"Combined {len(group)} similar elements"
                )
                
                merged.append(merged_element)
        
        return merged

    def calculate_total_concrete_volume(self, elements: List[ConcreteElement]) -> float:
        """Calculate total concrete volume in m³"""
        return sum(element.dimensions.volume for element in elements)

    def generate_concrete_report(self, elements: List[ConcreteElement]) -> Dict[str, Any]:
        """Generate a comprehensive concrete measurement report"""
        if not elements:
            return {"error": "No concrete elements detected"}
        
        # Group by element type
        by_type = {}
        for element in elements:
            if element.element_type not in by_type:
                by_type[element.element_type] = []
            by_type[element.element_type].append(element)
        
        # Calculate totals
        total_volume = self.calculate_total_concrete_volume(elements)
        
        # Calculate by grade
        by_grade = {}
        for element in elements:
            if element.grade not in by_grade:
                by_grade[element.grade] = []
            by_grade[element.grade].append(element)
        
        report = {
            "total_volume_m3": total_volume,
            "element_count": len(elements),
            "by_type": {},
            "by_grade": {},
            "elements": []
        }
        
        # Add breakdown by type
        for element_type, type_elements in by_type.items():
            volume = sum(e.dimensions.volume for e in type_elements)
            report["by_type"][element_type] = {
                "count": len(type_elements),
                "volume_m3": volume,
                "percentage": (volume / total_volume) * 100
            }
        
        # Add breakdown by grade
        for grade, grade_elements in by_grade.items():
            volume = sum(e.dimensions.volume for e in grade_elements)
            report["by_grade"][grade] = {
                "count": len(grade_elements),
                "volume_m3": volume,
                "percentage": (volume / total_volume) * 100
            }
        
        # Add detailed element list
        for element in elements:
            report["elements"].append({
                "type": element.element_type,
                "grade": element.grade,
                "volume_m3": element.dimensions.volume,
                "dimensions": {
                    "length_m": element.dimensions.length,
                    "width_m": element.dimensions.width,
                    "depth_m": element.dimensions.depth
                },
                "confidence": element.dimensions.confidence,
                "description": element.description
            })
        
        return report 