import os
import tempfile
from typing import List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for processing PDF construction drawings"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.max_image_size = (4096, 4096)  # Maximum image dimensions
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[Tuple[np.ndarray, int]]:
        """
        Extract images from PDF pages
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tuples containing (image_array, page_number)
        """
        try:
            images = []
            
            # Use pdf2image for better quality
            pdf_images = convert_from_path(
                pdf_path,
                dpi=300,  # High DPI for better quality
                fmt='PNG',
                size=self.max_image_size
            )
            
            for page_num, pil_image in enumerate(pdf_images):
                # Convert PIL image to OpenCV format
                opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                images.append((opencv_image, page_num + 1))
                
            logger.info(f"Extracted {len(images)} images from PDF: {pdf_path}")
            return images
            
        except Exception as e:
            logger.error(f"Error extracting images from PDF {pdf_path}: {str(e)}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better ML detection
        
        Args:
            image: Input image array
            
        Returns:
            Preprocessed image array
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image
    
    def detect_drawing_elements(self, image: np.ndarray) -> List[dict]:
        """
        Basic element detection using OpenCV
        
        Args:
            image: Preprocessed image array
            
        Returns:
            List of detected elements with bounding boxes
        """
        try:
            elements = []
            
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter contours by area
                area = cv2.contourArea(contour)
                if area < 100:  # Minimum area threshold
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate aspect ratio
                aspect_ratio = w / h if h > 0 else 0
                
                # Basic element classification based on shape and size
                element_type = self._classify_element(area, aspect_ratio, w, h)
                
                if element_type:
                    elements.append({
                        'type': element_type,
                        'confidence': 0.7,  # Basic confidence for MVP
                        'bounding_box': [x, y, x + w, y + h],
                        'area': area,
                        'center': (x + w // 2, y + h // 2)
                    })
            
            logger.info(f"Detected {len(elements)} elements in image")
            return elements
            
        except Exception as e:
            logger.error(f"Error detecting elements: {str(e)}")
            return []
    
    def _classify_element(self, area: float, aspect_ratio: float, width: int, height: int) -> Optional[str]:
        """
        Basic element classification based on geometric properties
        
        Args:
            area: Contour area
            aspect_ratio: Width to height ratio
            width: Bounding box width
            height: Bounding box height
            
        Returns:
            Element type or None if not classified
        """
        # Wall detection (long rectangles)
        if aspect_ratio > 3 or aspect_ratio < 0.33:
            if area > 500:
                return "wall"
        
        # Door detection (medium rectangles)
        if 0.5 < aspect_ratio < 2:
            if 1000 < area < 10000:
                return "door"
        
        # Window detection (small rectangles)
        if 0.5 < aspect_ratio < 2:
            if 500 < area < 5000:
                return "window"
        
        # Column detection (square-ish shapes)
        if 0.8 < aspect_ratio < 1.2:
            if area > 2000:
                return "column"
        
        return None
    
    def extract_text_from_image(self, image: np.ndarray) -> List[str]:
        """
        Extract text from image using OCR
        
        Args:
            image: Input image array
            
        Returns:
            List of extracted text strings
        """
        try:
            # For MVP, we'll use a simple approach
            # In production, this would use PaddleOCR or similar
            text_elements = []
            
            # Convert to PIL Image for text extraction
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Basic text detection using contour analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find text-like regions (small rectangular contours)
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Text-like characteristics
                if 10 < w < 200 and 5 < h < 50:
                    if 0.1 < w/h < 10:  # Reasonable aspect ratio for text
                        text_elements.append(f"Text at ({x}, {y})")
            
            return text_elements
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return []
    
    def calculate_scale_factor(self, image: np.ndarray) -> float:
        """
        Calculate scale factor from drawing (if scale bar is present)
        
        Args:
            image: Input image array
            
        Returns:
            Scale factor (pixels per meter)
        """
        # For MVP, return a default scale factor
        # In production, this would detect scale bars and calculate actual scale
        return 100.0  # 100 pixels per meter (default)
    
    def process_pdf_drawing(self, pdf_path: str) -> dict:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing processing results
        """
        try:
            results = {
                'pdf_path': pdf_path,
                'pages': [],
                'total_elements': 0,
                'processing_time': 0,
                'status': 'completed'
            }
            
            # Extract images from PDF
            images = self.extract_images_from_pdf(pdf_path)
            
            for image, page_num in images:
                page_result = {
                    'page_number': page_num,
                    'elements': [],
                    'text_elements': [],
                    'scale_factor': self.calculate_scale_factor(image)
                }
                
                # Preprocess image
                processed_image = self.preprocess_image(image)
                
                # Detect elements
                elements = self.detect_drawing_elements(processed_image)
                page_result['elements'] = elements
                
                # Extract text
                text_elements = self.extract_text_from_image(image)
                page_result['text_elements'] = text_elements
                
                results['pages'].append(page_result)
                results['total_elements'] += len(elements)
            
            logger.info(f"Processed PDF {pdf_path}: {results['total_elements']} elements found")
            return results
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return {
                'pdf_path': pdf_path,
                'pages': [],
                'total_elements': 0,
                'processing_time': 0,
                'status': 'failed',
                'error': str(e)
            } 