"""
PDF Processing Service for Construction AI

This module handles PDF drawing processing and element detection using
discipline-specific multi-head inference models.
"""

import os
import cv2
import numpy as np
import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import sys

# Add the ML models directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "ml" / "models"))

try:
    from multi_head_inference import MultiHeadInferenceSystem, Discipline
    ML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Multi-head inference not available: {e}")
    ML_AVAILABLE = False

# Add the ML directory to the path for enhanced inference
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "ml"))

try:
    from models.enhanced_inference import EnhancedInferenceSystem
    ENHANCED_ML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Enhanced inference not available: {e}")
    ENHANCED_ML_AVAILABLE = False

# Add the ML directory to the path for cost estimation
try:
    from enhanced_cost_estimation import EnhancedCostEstimator
    COST_ESTIMATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Cost estimation not available: {e}")
    COST_ESTIMATION_AVAILABLE = False

# Add the ML directory to the path for carbon footprint analysis
try:
    from carbon_footprint import CarbonFootprintCalculator
    CARBON_ANALYSIS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Carbon footprint analysis not available: {e}")
    CARBON_ANALYSIS_AVAILABLE = False

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "ml"))

# Temporarily disable enhanced material detection to fix backend
# from enhanced_material_detection import EnhancedMaterialDetector

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Processes PDF drawings and extracts elements using AI models."""
    
    def __init__(self):
        # Initialize enhanced inference system if available
        self.enhanced_system = None
        if ENHANCED_ML_AVAILABLE:
            try:
                models_dir = str(Path(__file__).parent.parent.parent.parent / "ml" / "models")
                self.enhanced_system = EnhancedInferenceSystem(models_dir)
                logger.info("Enhanced inference system initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize enhanced inference system: {e}")
                self.enhanced_system = None
        
        # Initialize multi-head inference system as fallback
        self.inference_system = None
        if ML_AVAILABLE and self.enhanced_system is None:
            try:
                self.inference_system = MultiHeadInferenceSystem()
                logger.info("Multi-head inference system initialized as fallback")
            except Exception as e:
                logger.error(f"Failed to initialize inference system: {e}")
                self.inference_system = None
        
        # Initialize cost estimation system if available
        self.cost_estimator = None
        if COST_ESTIMATION_AVAILABLE:
            try:
                self.cost_estimator = EnhancedCostEstimator(self.enhanced_system)
                logger.info("Cost estimation system initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize cost estimation system: {e}")
                self.cost_estimator = None
        
        # Initialize carbon footprint analysis system if available
        self.carbon_calculator = None
        if CARBON_ANALYSIS_AVAILABLE:
            try:
                self.carbon_calculator = CarbonFootprintCalculator()
                logger.info("Carbon footprint analysis system initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize carbon footprint analysis system: {e}")
                self.carbon_calculator = None
        
        # Temporarily disable enhanced material detector
        # self.enhanced_material_detector = None
        # try:
        #     self.enhanced_material_detector = EnhancedMaterialDetector()
        #     logger.info("Enhanced material detection system initialized successfully")
        # except Exception as e:
        #     logger.error(f"Failed to initialize enhanced material detection system: {e}")
        #     self.enhanced_material_detector = None
        

    
    def process_pdf_drawing(self, 
                           pdf_path: str, 
                           discipline: str = "architectural",
                           output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a PDF drawing and extract elements with enhanced material detection.
        
        Args:
            pdf_path: Path to the PDF file
            discipline: Discipline category (architectural, structural, civil, mep)
            output_dir: Optional output directory for extracted images
            
        Returns:
            Dictionary containing processing results
        """
        logger.info(f"Processing PDF: {pdf_path}")
        logger.info(f"Discipline: {discipline}")
        
        try:
            # Extract images from PDF
            images = self._extract_images_from_pdf(pdf_path, output_dir)
            logger.info(f"Extracted {len(images)} images from PDF: {pdf_path}")
            
            all_elements = []
            processing_method = "geometric_fallback"
            
            # Temporarily disable enhanced material detection
            # if self.enhanced_material_detector:
            #     logger.info("Using enhanced material detection system")
            #     processing_method = "enhanced_material_detection"
            #     
            #     for i, image_path in enumerate(images):
            #         logger.info(f"Processing image {i+1}/{len(images)}: {image_path}")
            #         
            #         # Use enhanced material detection
            #         enhanced_elements = self.enhanced_material_detector.detect_elements_with_materials(
            #             image_path, discipline
            #         )
            #         
            #         # Convert enhanced elements to standard format
            #         elements = []
            #         for enhanced_element in enhanced_elements:
            #             element = {
            #                 'element_type': enhanced_element.element_type,
            #                 'material': enhanced_element.material,
            #                 'quantity': 1,
            #                 'unit': 'item',
            #                 'area': enhanced_element.area,
            #                 'confidence_score': enhanced_element.confidence,
            #                 'material_confidence': enhanced_element.material_confidence,
            #                 'bbox': enhanced_element.bbox,
            #                 'properties': enhanced_element.properties,
            #                 'text_references': enhanced_element.text_references,
            #                 'image_index': i,
            #                 'image_path': image_path
            #             }
            #             elements.append(element)
            #         
            #         all_elements.extend(elements)
            #         
            #         # Save detected elements to database
            #         self._save_elements_to_database(elements, pdf_path, discipline)
            # else:
            # Fallback to original detection method
            logger.info("Using fallback detection method")
            
            for i, image_path in enumerate(images):
                logger.info(f"Processing image {i+1}/{len(images)}: {image_path}")
                
                # Load image
                image = cv2.imread(image_path)
                if image is None:
                    logger.error(f"Failed to load image: {image_path}")
                    continue
                
                logger.info(f"Loaded image: {image_path}, shape: {image.shape}, dtype: {image.dtype}")
                
                # Convert BGR to RGB and ensure proper format
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Ensure image is in uint8 format
                if image_rgb.dtype != np.uint8:
                    image_rgb = image_rgb.astype(np.uint8)
                
                # Detect elements using multi-head inference
                elements = self._detect_elements(image_rgb, discipline)
                
                # Add image information to elements
                for element in elements:
                    element['image_index'] = i
                    element['image_path'] = image_path
                
                all_elements.extend(elements)
            
            # Convert to the expected format
            formatted_elements = self._format_elements(all_elements)
            
            logger.info(f"Processed PDF {pdf_path}: {len(formatted_elements)} elements found")
            logger.debug(f"Successfully processed {len(formatted_elements)} elements using {processing_method} method")
            
            return {
                "elements": formatted_elements,
                "total_elements": len(formatted_elements),
                "images_processed": len(images),
                "discipline": discipline,
                "processing_method": processing_method
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return {
                "elements": [],
                "total_elements": 0,
                "images_processed": 0,
                "discipline": discipline,
                "error": str(e),
                "processing_method": "error"
            }
    
    def estimate_costs(self, 
                      pdf_path: str, 
                      discipline: str = "architectural",
                      project_scale: str = "medium") -> Dict[str, Any]:
        """
        Estimate costs for a PDF drawing.
        
        Args:
            pdf_path: Path to the PDF file
            discipline: Discipline category
            project_scale: Project scale (small, medium, large)
            
        Returns:
            Dictionary containing cost estimation results
        """
        logger.info(f"Estimating costs for PDF: {pdf_path}")
        logger.info(f"Discipline: {discipline}, Scale: {project_scale}")
        
        if not self.cost_estimator:
            logger.warning("Cost estimation not available")
            return {
                "error": "Cost estimation system not available",
                "total_cost": 0.0,
                "currency": "USD"
            }
        
        try:
            # Extract first image from PDF for cost analysis
            images = self._extract_images_from_pdf(pdf_path)
            if not images:
                return {
                    "error": "No images extracted from PDF",
                    "total_cost": 0.0,
                    "currency": "USD"
                }
            
            # Load first image
            image = cv2.imread(images[0])
            if image is None:
                return {
                    "error": "Failed to load image for cost analysis",
                    "total_cost": 0.0,
                    "currency": "USD"
                }
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Map discipline string to enum
            discipline_map = {
                "architectural": Discipline.ARCHITECTURAL,
                "structural": Discipline.STRUCTURAL,
                "civil": Discipline.CIVIL,
                "mep": Discipline.MEP
            }
            
            discipline_enum = discipline_map.get(discipline.lower(), Discipline.ARCHITECTURAL)
            
            # Perform cost analysis
            cost_analysis = self.cost_estimator.analyze_drawing_costs(
                image_rgb, discipline_enum, project_scale
            )
            
            # Generate comprehensive report
            report = self.cost_estimator.generate_comprehensive_report(
                cost_analysis, f"PDF_{os.path.basename(pdf_path)}"
            )
            
            logger.info(f"Cost estimation completed: ${cost_analysis.project_summary.total_cost:,.2f}")
            
            return {
                "cost_analysis": report,
                "total_cost": cost_analysis.project_summary.total_cost,
                "currency": cost_analysis.project_summary.currency,
                "element_count": cost_analysis.project_summary.element_count,
                "confidence_score": cost_analysis.confidence_score,
                "recommendations": cost_analysis.recommendations,
                "discipline": discipline,
                "project_scale": project_scale,
                "processing_method": "enhanced_cost_estimation"
            }
            
        except Exception as e:
            logger.error(f"Error in cost estimation: {e}")
            return {
                "error": str(e),
                "total_cost": 0.0,
                "currency": "USD",
                "discipline": discipline,
                "project_scale": project_scale,
                "processing_method": "error"
            }
    
    def analyze_carbon_footprint(self, 
                                pdf_path: str, 
                                discipline: str = "architectural",
                                project_type: str = "commercial") -> Dict[str, Any]:
        """
        Analyze carbon footprint from PDF drawings.
        
        Args:
            pdf_path: Path to the PDF file
            discipline: Discipline category (architectural, structural, civil, mep)
            project_type: Project type for carbon benchmarks (residential, commercial, industrial)
            
        Returns:
            Dictionary containing carbon footprint analysis results
        """
        logger.info(f"Analyzing carbon footprint for PDF: {pdf_path}")
        logger.info(f"Discipline: {discipline}, Project Type: {project_type}")
        
        if not self.carbon_calculator:
            return {
                'status': 'error',
                'message': 'Carbon footprint analysis system not available',
                'timestamp': '2024-01-01T00:00:00'
            }
        
        try:
            # Process PDF to get elements
            processing_results = self.process_pdf_drawing(pdf_path, discipline)
            
            if processing_results['status'] != 'success':
                return {
                    'status': 'error',
                    'message': f'Failed to process PDF: {processing_results.get("message", "Unknown error")}',
                    'timestamp': '2024-01-01T00:00:00'
                }
            
            # Extract elements for carbon analysis
            elements = processing_results.get('elements', [])
            
            if not elements:
                return {
                    'status': 'success',
                    'message': 'No elements detected for carbon analysis',
                    'total_carbon': 0.0,
                    'carbon_intensity': 0.0,
                    'sustainability_score': 0.0,
                    'material_breakdown': {},
                    'optimization_recommendations': ['No elements detected for carbon analysis'],
                    'compliance_status': {
                        'within_benchmark': True,
                        'low_carbon_compliant': True,
                        'sustainable_compliant': True,
                        'passive_house_compliant': True,
                        'intensity_acceptable': True
                    },
                    'project_type': project_type,
                    'discipline': discipline,
                    'timestamp': '2024-01-01T00:00:00'
                }
            
            # Convert elements to carbon analysis format
            elements_for_carbon = []
            for element in elements:
                # Assign material based on element type
                material = self._assign_material_to_element(element.get('type', 'unknown'))
                
                # Calculate quantity based on area/volume
                quantity = element.get('quantity', 0)
                unit = element.get('unit', 'kg')
                
                # Convert area to weight for carbon calculation
                if unit == 'm2' and quantity > 0:
                    # Convert area to weight based on typical material densities
                    density_kg_per_m2 = self._get_material_density(material)
                    quantity = quantity * density_kg_per_m2
                    unit = 'kg'
                
                carbon_element = {
                    'type': element.get('type', 'unknown'),
                    'material': material,
                    'quantity': quantity,
                    'unit': unit,
                    'specifications': element.get('specifications', ['standard']),
                    'transportation': 'regional',  # Default transportation
                    'confidence': element.get('confidence', 0.5)
                }
                elements_for_carbon.append(carbon_element)
            
            # Perform carbon footprint analysis
            carbon_analysis = self.carbon_calculator.analyze_carbon_footprint(elements_for_carbon, project_type)
            
            if not carbon_analysis:
                return {
                    'status': 'error',
                    'message': 'Carbon footprint analysis failed',
                    'timestamp': '2024-01-01T00:00:00'
                }
            
            # Generate carbon report
            carbon_report = self.carbon_calculator.generate_carbon_report(carbon_analysis)
            
            # Add processing metadata
            result = {
                'status': 'success',
                'message': f'Carbon footprint analysis completed for {pdf_path}',
                'total_carbon_kg_co2e': carbon_analysis.total_carbon,
                'carbon_intensity_kg_co2e_per_unit': carbon_analysis.carbon_intensity,
                'sustainability_score': carbon_analysis.sustainability_score,
                'carbon_savings_potential_kg_co2e': carbon_analysis.carbon_savings_potential,
                'material_breakdown': carbon_analysis.material_breakdown,
                'high_impact_elements': carbon_analysis.high_impact_elements,
                'optimization_recommendations': carbon_analysis.optimization_recommendations,
                'compliance_status': carbon_analysis.compliance_status,
                'project_type': project_type,
                'discipline': discipline,
                'element_count': len(elements),
                'timestamp': '2024-01-01T00:00:00'
            }
            
            logger.info(f"Carbon footprint analysis completed: {carbon_analysis.total_carbon:.2f} kg CO2e")
            return result
            
        except Exception as e:
            logger.error(f"Error in carbon footprint analysis: {e}")
            return {
                'status': 'error',
                'message': f'Carbon footprint analysis failed: {str(e)}',
                'timestamp': '2024-01-01T00:00:00'
            }
    
    def _extract_images_from_pdf(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """Extract images from PDF file."""
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        image_paths = []
        
        try:
            # Process each page
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # Scale factor for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Save image
                image_filename = f"page_{page_num + 1}.png"
                image_path = os.path.join(output_dir, image_filename)
                pix.save(image_path)
                
                image_paths.append(image_path)
                
        finally:
            pdf_document.close()
        
        return image_paths
    
    def _detect_elements(self, image: np.ndarray, discipline: str) -> List[Dict[str, Any]]:
        """
        Detect elements in image using discipline-specific models.
        
        Args:
            image: Input image as numpy array
            discipline: Discipline category
            
        Returns:
            List of detected elements
        """
        # Map discipline string to enum
        discipline_map = {
            "architectural": Discipline.ARCHITECTURAL,
            "structural": Discipline.STRUCTURAL,
            "civil": Discipline.CIVIL,
            "mep": Discipline.MEP
        }
        
        discipline_enum = discipline_map.get(discipline.lower(), Discipline.ARCHITECTURAL)
        
        # Use enhanced inference if available
        if self.enhanced_system:
            logger.info(f"Using enhanced inference for discipline: {discipline}")
            enhanced_results = self.enhanced_system.detect_elements_enhanced(
                image, discipline_enum, use_ocr=True
            )
            return enhanced_results.get('elements', [])
        
        # Use multi-head inference as fallback
        elif self.inference_system:
            logger.info(f"Using multi-head inference for discipline: {discipline}")
            detection_results = self.inference_system.detect_elements(
                image, discipline_enum, confidence_threshold=0.5
            )
            
            # Convert DetectionResult objects to dictionaries
            elements = []
            for result in detection_results:
                element = {
                    "type": result.element_type,
                    "bbox": result.bbox,
                    "confidence": result.confidence,
                    "properties": result.properties,
                    "discipline": result.discipline.value
                }
                elements.append(element)
            
            return elements
        else:
            # Fallback to geometric detection
            logger.info(f"Using geometric fallback detection for discipline: {discipline}")
            return self._geometric_detection(image, discipline)
    
    def _geometric_detection(self, image: np.ndarray, discipline: str) -> List[Dict[str, Any]]:
        """
        Fallback geometric detection method.
        
        Args:
            image: Input image
            discipline: Discipline category
            
        Returns:
            List of detected elements
        """
        elements = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Discipline-specific element detection
        if discipline.lower() == "architectural":
            elements = self._detect_architectural_elements(contours)
        elif discipline.lower() == "structural":
            elements = self._detect_structural_elements(contours)
        elif discipline.lower() == "civil":
            elements = self._detect_civil_elements(contours)
        elif discipline.lower() == "mep":
            elements = self._detect_mep_elements(contours)
        else:
            # Generic detection
            elements = self._detect_generic_elements(contours)
        
        return elements
    
    def _detect_architectural_elements(self, contours: List) -> List[Dict[str, Any]]:
        """Detect architectural elements using geometric analysis."""
        elements = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Wall detection (long rectangular shapes)
            aspect_ratio = w / h if h > 0 else 0
            if (aspect_ratio > 3 or aspect_ratio < 0.33) and area > 1000:
                elements.append({
                    "type": "wall",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.85,
                    "properties": {
                        "length": max(w, h),
                        "thickness": min(w, h),
                        "area": area
                    },
                    "discipline": "architectural"
                })
            
            # Door detection (medium rectangular openings)
            elif 0.3 < aspect_ratio < 0.8 and 500 < area < 5000:
                elements.append({
                    "type": "door",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.80,
                    "properties": {
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    "discipline": "architectural"
                })
            
            # Window detection (smaller rectangular openings)
            elif 0.5 < aspect_ratio < 2.0 and 100 < area < 2000:
                elements.append({
                    "type": "window",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.75,
                    "properties": {
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    "discipline": "architectural"
                })
        
        return elements
    
    def _detect_structural_elements(self, contours: List) -> List[Dict[str, Any]]:
        """Detect structural elements using geometric analysis."""
        elements = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Beam detection (long horizontal elements)
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio > 4 and area > 2000:
                elements.append({
                    "type": "beam",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.90,
                    "properties": {
                        "length": w,
                        "depth": h,
                        "area": area
                    },
                    "discipline": "structural"
                })
            
            # Column detection (tall vertical elements)
            elif aspect_ratio < 0.5 and area > 1000:
                elements.append({
                    "type": "column",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.85,
                    "properties": {
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    "discipline": "structural"
                })
            
            # Foundation detection (large rectangular elements)
            elif area > 5000:
                elements.append({
                    "type": "foundation",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.75,
                    "properties": {
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    "discipline": "structural"
                })
        
        return elements
    
    def _detect_civil_elements(self, contours: List) -> List[Dict[str, Any]]:
        """Detect civil engineering elements using geometric analysis."""
        elements = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Road detection (long linear elements)
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio > 3 and area > 3000:
                elements.append({
                    "type": "road",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.85,
                    "properties": {
                        "length": w,
                        "width": h,
                        "area": area
                    },
                    "discipline": "civil"
                })
            
            # Utility detection (small elements)
            elif 100 < area < 2000:
                elements.append({
                    "type": "utility",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.70,
                    "properties": {
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    "discipline": "civil"
                })
        
        return elements
    
    def _detect_mep_elements(self, contours: List) -> List[Dict[str, Any]]:
        """Detect MEP elements using geometric analysis."""
        elements = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # HVAC duct detection (rectangular, medium size)
            aspect_ratio = w / h if h > 0 else 0
            if 0.5 < aspect_ratio < 3.0 and 1000 < area < 8000:
                elements.append({
                    "type": "hvac_duct",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.80,
                    "properties": {
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    "discipline": "mep"
                })
            
            # Electrical panel detection (small rectangular elements)
            elif 100 < area < 2000:
                elements.append({
                    "type": "electrical_panel",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.75,
                    "properties": {
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    "discipline": "mep"
                })
        
        return elements
    
    def _detect_generic_elements(self, contours: List) -> List[Dict[str, Any]]:
        """Generic element detection for unknown disciplines."""
        elements = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if area > 500:  # Minimum area threshold
                elements.append({
                    "type": "element",
                    "bbox": [x, y, x + w, y + h],
                    "confidence": 0.60,
                    "properties": {
                        "width": w,
                        "height": h,
                        "area": area
                    },
                    "discipline": "generic"
                })
        
        return elements
    
    def _format_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format elements to match the expected output format."""
        formatted_elements = []
        
        for element in elements:
            formatted_element = {
                "id": f"{element.get('type', 'element')}_{len(formatted_elements):03d}",
                "type": element.get("type", "element"),
                "bbox": element.get("bbox", [0, 0, 0, 0]),
                "confidence": element.get("confidence", 0.5),
                "properties": element.get("properties", {}),
                "discipline": element.get("discipline", "generic")
            }
            formatted_elements.append(formatted_element)
        
        return formatted_elements
    
    def _assign_material_to_element(self, element_type: str) -> str:
        """Assign default material based on element type"""
        material_mapping = {
            # Structural elements
            'beam': 'steel',
            'column': 'concrete',
            'slab': 'concrete',
            'foundation': 'concrete',
            'wall': 'concrete',
            'floor': 'concrete',
            'roof': 'concrete',
            
            # Architectural elements
            'room': 'concrete',
            'door': 'wood',
            'window': 'glass',
            'partition': 'gypsum',
            
            # Civil elements
            'road': 'asphalt',
            'utility': 'concrete',
            
            # MEP elements
            'hvac_duct': 'steel',
            'electrical_panel': 'steel',
            
            # Default
            'unknown': 'concrete',
            'element': 'concrete'
        }
        return material_mapping.get(element_type.lower(), 'concrete')
    
    def _get_material_density(self, material: str) -> float:
        """Get material density in kg per m² for area to weight conversion"""
        density_mapping = {
            'concrete': 2400.0,  # kg/m³, typical thickness 0.2m = 480 kg/m²
            'steel': 7850.0,     # kg/m³, typical thickness 0.01m = 78.5 kg/m²
            'wood': 600.0,       # kg/m³, typical thickness 0.05m = 30 kg/m²
            'glass': 2500.0,     # kg/m³, typical thickness 0.01m = 25 kg/m²
            'gypsum': 1200.0,    # kg/m³, typical thickness 0.02m = 24 kg/m²
            'asphalt': 2300.0,   # kg/m³, typical thickness 0.1m = 230 kg/m²
            'brick': 1800.0,     # kg/m³, typical thickness 0.2m = 360 kg/m²
            'stone': 2700.0,     # kg/m³, typical thickness 0.2m = 540 kg/m²
            'tile': 2000.0,      # kg/m³, typical thickness 0.02m = 40 kg/m²
            'plastic': 1200.0,   # kg/m³, typical thickness 0.01m = 12 kg/m²
            'aluminum': 2700.0,  # kg/m³, typical thickness 0.01m = 27 kg/m²
            'copper': 8960.0,    # kg/m³, typical thickness 0.01m = 89.6 kg/m²
            'zinc': 7140.0,      # kg/m³, typical thickness 0.01m = 71.4 kg/m²
            'lead': 11340.0,     # kg/m³, typical thickness 0.01m = 113.4 kg/m²
            'tin': 7310.0,       # kg/m³, typical thickness 0.01m = 73.1 kg/m²
            'fiberglass': 1800.0, # kg/m³, typical thickness 0.05m = 90 kg/m²
            'mineral_wool': 100.0, # kg/m³, typical thickness 0.1m = 10 kg/m²
            'cellulose': 50.0,   # kg/m³, typical thickness 0.1m = 5 kg/m²
            'spray_foam': 30.0,  # kg/m³, typical thickness 0.1m = 3 kg/m²
            'paint': 1200.0,     # kg/m³, typical thickness 0.001m = 1.2 kg/m²
            'carpet': 2000.0,    # kg/m³, typical thickness 0.01m = 20 kg/m²
            'precast': 2400.0,   # kg/m³, typical thickness 0.2m = 480 kg/m²
            'cast_in_place': 2400.0, # kg/m³, typical thickness 0.2m = 480 kg/m²
            'modular': 2400.0,   # kg/m³, typical thickness 0.2m = 480 kg/m²
            'prefabricated': 2400.0, # kg/m³, typical thickness 0.2m = 480 kg/m²
            'default': 2400.0    # kg/m³, typical thickness 0.2m = 480 kg/m²
        }
        
        # Return density per m² (density * typical thickness)
        base_density = density_mapping.get(material, 2400.0)
        typical_thickness = {
            'concrete': 0.2, 'steel': 0.01, 'wood': 0.05, 'glass': 0.01,
            'gypsum': 0.02, 'asphalt': 0.1, 'brick': 0.2, 'stone': 0.2,
            'tile': 0.02, 'plastic': 0.01, 'aluminum': 0.01, 'copper': 0.01,
            'zinc': 0.01, 'lead': 0.01, 'tin': 0.01, 'fiberglass': 0.05,
            'mineral_wool': 0.1, 'cellulose': 0.1, 'spray_foam': 0.1,
            'paint': 0.001, 'carpet': 0.01, 'precast': 0.2, 'cast_in_place': 0.2,
            'modular': 0.2, 'prefabricated': 0.2, 'default': 0.2
        }
        
        thickness = typical_thickness.get(material, 0.2)
        return base_density * thickness

    def _save_elements_to_database(self, elements: List[Dict], pdf_path: str, discipline: str):
        """
        Save enhanced elements to database with material information
        """
        try:
            from app.models.models import Element
            from app.database import get_db
            
            db = next(get_db())
            
            for element_data in elements:
                element = Element(
                    element_type=element_data['element_type'],
                    material=element_data.get('material', 'unknown'),
                    quantity=element_data['quantity'],
                    unit=element_data['unit'],
                    area=element_data.get('area', 0),
                    confidence_score=element_data['confidence_score'],
                    material_confidence=element_data.get('material_confidence', 0.0),
                    bbox=str(element_data['bbox']),
                    properties=str(element_data.get('properties', {})),
                    text_references=str(element_data.get('text_references', [])),
                    drawing_id=self._get_drawing_id_from_path(pdf_path)
                )
                db.add(element)
            
            db.commit()
            logger.info(f"Saved {len(elements)} enhanced elements to database")
            
        except Exception as e:
            logger.error(f"Error saving elements to database: {e}")

    def _get_drawing_id_from_path(self, pdf_path: str) -> int:
        """
        Extract drawing ID from PDF path
        """
        try:
            # Extract project ID from path like "uploads/1/filename.pdf"
            path_parts = pdf_path.split('/')
            if len(path_parts) >= 2:
                return int(path_parts[1])  # Project ID
            return 1  # Default fallback
        except:
            return 1

# Global instance
pdf_processor = PDFProcessor() 