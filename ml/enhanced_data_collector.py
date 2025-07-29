"""
Enhanced Data Collector for Drawing Reading Improvement

This module provides advanced data collection capabilities to improve
model drawing reading capabilities through better training data.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import hashlib
import fitz  # PyMuPDF
from PIL import Image
import matplotlib.pyplot as plt
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDataCollector:
    """Enhanced data collector with comprehensive metadata and quality analysis."""
    
    def __init__(self, base_path: str = "ml/data"):
        self.base_path = Path(base_path)
        self.disciplines = ["architectural", "structural", "civil", "mep"]
        
        # Enhanced annotation templates with detailed element types
        self.annotation_templates = {
            "architectural": {
                "elements": ["wall", "door", "window", "room", "column", "stair", "elevator", "ramp", "furniture", "fixture"],
                "properties": ["dimensions", "materials", "finishes", "openings", "accessibility"],
                "standards": ["BS", "ISO", "ASME", "ANSI"]
            },
            "structural": {
                "elements": ["beam", "column", "slab", "foundation", "truss", "brace", "connection", "reinforcement", "precast", "steel"],
                "properties": ["loads", "materials", "connections", "reinforcement", "fire_rating"],
                "standards": ["BS", "Eurocode", "AISC", "ACI"]
            },
            "civil": {
                "elements": ["road", "drainage", "utility", "pavement", "bridge", "retaining_wall", "culvert", "signage", "lighting"],
                "properties": ["gradients", "materials", "drainage", "utilities", "traffic"],
                "standards": ["BS", "Highway_Code", "DMRB", "AASHTO"]
            },
            "mep": {
                "elements": ["duct", "pipe", "electrical", "fixture", "equipment", "ventilation", "heating", "cooling", "plumbing", "fire_protection"],
                "properties": ["capacity", "materials", "connections", "controls", "efficiency"],
                "standards": ["BS", "ASHRAE", "NEC", "IPC"]
            }
        }
        
        # Drawing quality metrics
        self.quality_metrics = {
            "resolution": ["low", "medium", "high", "ultra_high"],
            "clarity": ["poor", "fair", "good", "excellent"],
            "completeness": ["incomplete", "partial", "complete", "comprehensive"],
            "complexity": ["simple", "moderate", "complex", "very_complex"]
        }
        
        # Create enhanced directory structure
        self._create_enhanced_directory_structure()
    
    def _create_enhanced_directory_structure(self):
        """Create enhanced directory structure for better data organization."""
        directories = [
            "raw", "processed", "annotations", "metadata", "datasets",
            "quality_analysis", "augmented", "validation", "testing"
        ]
        
        for discipline in self.disciplines:
            for directory in directories:
                path = self.base_path / directory / discipline
                path.mkdir(parents=True, exist_ok=True)
                
                # Create subdirectories for better organization
                if directory == "annotations":
                    (path / "bbox").mkdir(exist_ok=True)
                    (path / "segmentation").mkdir(exist_ok=True)
                    (path / "text").mkdir(exist_ok=True)
                    (path / "symbols").mkdir(exist_ok=True)
                
                if directory == "metadata":
                    (path / "quality").mkdir(exist_ok=True)
                    (path / "standards").mkdir(exist_ok=True)
                    (path / "scales").mkdir(exist_ok=True)
                
                logger.info(f"Created enhanced directory: {path}")
    
    def collect_drawing_with_enhanced_metadata(self, 
                                             file_path: str, 
                                             discipline: str, 
                                             metadata: Optional[Dict] = None) -> str:
        """
        Collect a drawing with comprehensive metadata for improved training.
        
        Args:
            file_path: Path to the drawing file
            discipline: Discipline category
            metadata: Optional metadata about the drawing
            
        Returns:
            Unique drawing ID
        """
        if discipline not in self.disciplines:
            raise ValueError(f"Invalid discipline: {discipline}")
        
        # Generate unique drawing ID
        drawing_id = self._generate_enhanced_drawing_id(file_path, discipline)
        
        # Analyze drawing quality and characteristics
        quality_analysis = self._analyze_drawing_quality(file_path)
        scale_analysis = self._analyze_drawing_scale(file_path)
        content_analysis = self._analyze_drawing_content(file_path, discipline)
        
        # Enhanced metadata collection
        enhanced_metadata = {
            "drawing_id": drawing_id,
            "discipline": discipline,
            "original_path": str(file_path),
            "collected_at": datetime.now().isoformat(),
            "file_size": os.path.getsize(file_path),
            "file_format": Path(file_path).suffix.lower(),
            
            # Quality metrics
            "quality_analysis": quality_analysis,
            "scale_analysis": scale_analysis,
            "content_analysis": content_analysis,
            
            # Drawing characteristics
            "dimensions": self._get_drawing_dimensions(file_path),
            "color_mode": self._get_color_mode(file_path),
            "text_density": self._estimate_text_density(file_path),
            "symbol_density": self._estimate_symbol_density(file_path),
            
            # Standards and compliance
            "drawing_standards": self._detect_drawing_standards(file_path),
            "units": self._detect_units(file_path),
            "scale_factor": scale_analysis.get("detected_scale"),
            
            # Training metadata
            "training_priority": self._calculate_training_priority(quality_analysis, content_analysis),
            "augmentation_suggestions": self._suggest_augmentations(quality_analysis),
            "validation_status": "pending"
        }
        
        # Merge with provided metadata
        if metadata:
            enhanced_metadata.update(metadata)
        
        # Copy file to raw data directory
        raw_path = self.base_path / "raw" / discipline / f"{drawing_id}{Path(file_path).suffix}"
        self._copy_file_with_validation(file_path, raw_path)
        
        # Save comprehensive metadata
        metadata_path = self.base_path / "metadata" / discipline / f"{drawing_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(enhanced_metadata, f, indent=2)
        
        # Save quality analysis separately
        quality_path = self.base_path / "metadata" / "quality" / discipline / f"{drawing_id}_quality.json"
        with open(quality_path, 'w') as f:
            json.dump(quality_analysis, f, indent=2)
        
        logger.info(f"Collected drawing {drawing_id} with enhanced metadata for discipline {discipline}")
        return drawing_id
    
    def _analyze_drawing_quality(self, file_path: str) -> Dict[str, Any]:
        """Analyze drawing quality for training prioritization."""
        try:
            # Load image
            if file_path.lower().endswith('.pdf'):
                image = self._pdf_to_image(file_path)
            else:
                image = cv2.imread(file_path)
            
            if image is None:
                return {"error": "Could not load image"}
            
            # Convert to grayscale for analysis
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Quality metrics
            quality_metrics = {
                "resolution": self._analyze_resolution(gray),
                "clarity": self._analyze_clarity(gray),
                "noise_level": self._analyze_noise(gray),
                "contrast": self._analyze_contrast(gray),
                "sharpness": self._analyze_sharpness(gray),
                "completeness": self._analyze_completeness(gray),
                "complexity": self._analyze_complexity(gray)
            }
            
            # Overall quality score
            quality_score = self._calculate_quality_score(quality_metrics)
            quality_metrics["overall_score"] = quality_score
            quality_metrics["quality_level"] = self._get_quality_level(quality_score)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing drawing quality: {e}")
            return {"error": str(e)}
    
    def _analyze_drawing_scale(self, file_path: str) -> Dict[str, Any]:
        """Analyze drawing scale and units."""
        try:
            # Extract text from drawing
            text_content = self._extract_text_content(file_path)
            
            # Scale detection
            scale_info = {
                "detected_scale": self._detect_scale_from_text(text_content),
                "units": self._detect_units_from_text(text_content),
                "scale_bar_present": self._detect_scale_bar(file_path),
                "dimension_texts": self._extract_dimension_texts(text_content)
            }
            
            return scale_info
            
        except Exception as e:
            logger.error(f"Error analyzing drawing scale: {e}")
            return {"error": str(e)}
    
    def _analyze_drawing_content(self, file_path: str, discipline: str) -> Dict[str, Any]:
        """Analyze drawing content and element density."""
        try:
            # Load image
            if file_path.lower().endswith('.pdf'):
                image = self._pdf_to_image(file_path)
            else:
                image = cv2.imread(file_path)
            
            if image is None:
                return {"error": "Could not load image"}
            
            # Content analysis
            content_analysis = {
                "element_density": self._calculate_element_density(image, discipline),
                "text_density": self._calculate_text_density(image),
                "symbol_density": self._calculate_symbol_density(image),
                "line_density": self._calculate_line_density(image),
                "area_coverage": self._calculate_area_coverage(image),
                "complexity_score": self._calculate_complexity_score(image)
            }
            
            return content_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing drawing content: {e}")
            return {"error": str(e)}
    
    def _pdf_to_image(self, pdf_path: str) -> np.ndarray:
        """Convert PDF to image for analysis."""
        try:
            pdf_document = fitz.open(pdf_path)
            page = pdf_document[0]  # First page
            
            # Convert to image with high resolution
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to numpy array
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            return np.array(img)
            
        except Exception as e:
            logger.error(f"Error converting PDF to image: {e}")
            return None
    
    def _extract_text_content(self, file_path: str) -> str:
        """Extract text content from drawing."""
        try:
            if file_path.lower().endswith('.pdf'):
                pdf_document = fitz.open(file_path)
                text_content = ""
                for page in pdf_document:
                    text_content += page.get_text()
                return text_content
            else:
                # For image files, use OCR
                image = cv2.imread(file_path)
                # TODO: Implement OCR text extraction
                return ""
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""
    
    def _analyze_resolution(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Analyze image resolution quality."""
        height, width = gray_image.shape
        total_pixels = height * width
        
        return {
            "width": width,
            "height": height,
            "total_pixels": total_pixels,
            "resolution_level": "high" if total_pixels > 1000000 else "medium" if total_pixels > 500000 else "low"
        }
    
    def _analyze_clarity(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Analyze image clarity using edge detection."""
        # Apply edge detection
        edges = cv2.Canny(gray_image, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return {
            "edge_density": edge_density,
            "clarity_score": min(edge_density * 10, 1.0),
            "clarity_level": "excellent" if edge_density > 0.1 else "good" if edge_density > 0.05 else "fair"
        }
    
    def _analyze_noise(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Analyze image noise level."""
        # Simple noise estimation using Laplacian variance
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        return {
            "noise_level": laplacian_var,
            "noise_rating": "low" if laplacian_var < 100 else "medium" if laplacian_var < 500 else "high"
        }
    
    def _analyze_contrast(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Analyze image contrast."""
        # Calculate contrast using standard deviation
        contrast = np.std(gray_image)
        
        return {
            "contrast_value": contrast,
            "contrast_level": "high" if contrast > 50 else "medium" if contrast > 25 else "low"
        }
    
    def _analyze_sharpness(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Analyze image sharpness."""
        # Use Laplacian variance as sharpness measure
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        sharpness = laplacian.var()
        
        return {
            "sharpness_value": sharpness,
            "sharpness_level": "high" if sharpness > 500 else "medium" if sharpness > 100 else "low"
        }
    
    def _analyze_completeness(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Analyze drawing completeness."""
        # Calculate non-empty area percentage
        non_zero_pixels = np.count_nonzero(gray_image)
        total_pixels = gray_image.size
        completeness_ratio = non_zero_pixels / total_pixels
        
        return {
            "completeness_ratio": completeness_ratio,
            "completeness_level": "comprehensive" if completeness_ratio > 0.3 else "complete" if completeness_ratio > 0.15 else "partial"
        }
    
    def _analyze_complexity(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Analyze drawing complexity."""
        # Use edge density and texture as complexity measures
        edges = cv2.Canny(gray_image, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Calculate texture complexity
        gray_float = gray_image.astype(np.float32)
        texture_complexity = np.std(cv2.Laplacian(gray_float, cv2.CV_64F))
        
        complexity_score = (edge_density * 0.6) + (texture_complexity / 1000 * 0.4)
        
        return {
            "complexity_score": complexity_score,
            "complexity_level": "very_complex" if complexity_score > 0.1 else "complex" if complexity_score > 0.05 else "moderate" if complexity_score > 0.02 else "simple"
        }
    
    def _calculate_quality_score(self, quality_metrics: Dict) -> float:
        """Calculate overall quality score."""
        scores = []
        
        # Resolution score
        if quality_metrics["resolution"]["resolution_level"] == "high":
            scores.append(1.0)
        elif quality_metrics["resolution"]["resolution_level"] == "medium":
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # Clarity score
        scores.append(quality_metrics["clarity"]["clarity_score"])
        
        # Contrast score
        contrast_level = quality_metrics["contrast"]["contrast_level"]
        if contrast_level == "high":
            scores.append(1.0)
        elif contrast_level == "medium":
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # Sharpness score
        sharpness_level = quality_metrics["sharpness"]["sharpness_level"]
        if sharpness_level == "high":
            scores.append(1.0)
        elif sharpness_level == "medium":
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        return np.mean(scores)
    
    def _get_quality_level(self, quality_score: float) -> str:
        """Get quality level based on score."""
        if quality_score >= 0.8:
            return "excellent"
        elif quality_score >= 0.6:
            return "good"
        elif quality_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _detect_scale_from_text(self, text_content: str) -> Optional[str]:
        """Detect scale from text content."""
        # Common scale patterns
        scale_patterns = [
            r'1:(\d+)',  # 1:50, 1:100, etc.
            r'scale\s*(\d+):(\d+)',  # scale 1:50
            r'(\d+)\s*to\s*(\d+)',  # 1 to 50
        ]
        
        for pattern in scale_patterns:
            import re
            matches = re.findall(pattern, text_content.lower())
            if matches:
                return f"1:{matches[0]}" if len(matches[0]) == 1 else f"{matches[0][0]}:{matches[0][1]}"
        
        return None
    
    def _detect_units_from_text(self, text_content: str) -> str:
        """Detect units from text content."""
        text_lower = text_content.lower()
        
        if any(unit in text_lower for unit in ['mm', 'millimeter', 'millimetre']):
            return "mm"
        elif any(unit in text_lower for unit in ['cm', 'centimeter', 'centimetre']):
            return "cm"
        elif any(unit in text_lower for unit in ['m', 'meter', 'metre']):
            return "m"
        elif any(unit in text_lower for unit in ['ft', 'feet', 'foot']):
            return "ft"
        elif any(unit in text_lower for unit in ['in', 'inch', 'inches']):
            return "in"
        else:
            return "unknown"
    
    def _detect_scale_bar(self, file_path: str) -> bool:
        """Detect presence of scale bar in drawing."""
        # TODO: Implement scale bar detection using computer vision
        return False
    
    def _extract_dimension_texts(self, text_content: str) -> List[str]:
        """Extract dimension texts from content."""
        import re
        # Pattern for dimension texts (numbers with units)
        dimension_pattern = r'\d+(?:\.\d+)?\s*(?:mm|cm|m|ft|in)'
        return re.findall(dimension_pattern, text_content)
    
    def _calculate_element_density(self, image: np.ndarray, discipline: str) -> float:
        """Calculate element density based on discipline."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Use edge density as proxy for element density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Adjust based on discipline
        discipline_factors = {
            "architectural": 1.0,
            "structural": 1.2,  # More complex elements
            "civil": 0.8,       # Larger, simpler elements
            "mep": 1.1          # Medium complexity
        }
        
        return edge_density * discipline_factors.get(discipline, 1.0)
    
    def _calculate_text_density(self, image: np.ndarray) -> float:
        """Calculate text density in drawing."""
        # TODO: Implement OCR-based text density calculation
        return 0.1  # Placeholder
    
    def _calculate_symbol_density(self, image: np.ndarray) -> float:
        """Calculate symbol density in drawing."""
        # TODO: Implement symbol detection-based density calculation
        return 0.05  # Placeholder
    
    def _calculate_line_density(self, image: np.ndarray) -> float:
        """Calculate line density in drawing."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Use edge detection for line density
        edges = cv2.Canny(gray, 50, 150)
        line_density = np.sum(edges > 0) / edges.size
        
        return line_density
    
    def _calculate_area_coverage(self, image: np.ndarray) -> float:
        """Calculate area coverage by drawing elements."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate non-empty area
        non_zero_pixels = np.count_nonzero(gray)
        total_pixels = gray.size
        
        return non_zero_pixels / total_pixels
    
    def _calculate_complexity_score(self, image: np.ndarray) -> float:
        """Calculate overall complexity score."""
        # Combine multiple metrics
        edge_density = self._calculate_line_density(image)
        area_coverage = self._calculate_area_coverage(image)
        
        # Normalize and combine
        complexity_score = (edge_density * 0.6) + (area_coverage * 0.4)
        
        return min(complexity_score, 1.0)
    
    def _get_drawing_dimensions(self, file_path: str) -> Dict[str, int]:
        """Get drawing dimensions."""
        try:
            if file_path.lower().endswith('.pdf'):
                image = self._pdf_to_image(file_path)
            else:
                image = cv2.imread(file_path)
            
            if image is not None:
                height, width = image.shape[:2]
                return {"width": width, "height": height}
            else:
                return {"width": 0, "height": 0}
        except Exception as e:
            logger.error(f"Error getting drawing dimensions: {e}")
            return {"width": 0, "height": 0}
    
    def _get_color_mode(self, file_path: str) -> str:
        """Get color mode of drawing."""
        try:
            if file_path.lower().endswith('.pdf'):
                image = self._pdf_to_image(file_path)
            else:
                image = cv2.imread(file_path)
            
            if image is not None:
                if len(image.shape) == 3:
                    return "color"
                else:
                    return "grayscale"
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"Error getting color mode: {e}")
            return "unknown"
    
    def _estimate_text_density(self, file_path: str) -> float:
        """Estimate text density in drawing."""
        # TODO: Implement OCR-based text density estimation
        return 0.1  # Placeholder
    
    def _estimate_symbol_density(self, file_path: str) -> float:
        """Estimate symbol density in drawing."""
        # TODO: Implement symbol detection-based density estimation
        return 0.05  # Placeholder
    
    def _detect_drawing_standards(self, file_path: str) -> List[str]:
        """Detect drawing standards used."""
        # TODO: Implement standard detection based on symbols, text, and layout
        return ["BS"]  # Placeholder
    
    def _detect_units(self, file_path: str) -> str:
        """Detect units used in drawing."""
        text_content = self._extract_text_content(file_path)
        return self._detect_units_from_text(text_content)
    
    def _calculate_training_priority(self, quality_analysis: Dict, content_analysis: Dict) -> str:
        """Calculate training priority based on quality and content."""
        quality_score = quality_analysis.get("overall_score", 0.5)
        complexity_score = content_analysis.get("complexity_score", 0.5)
        
        # High priority for high quality and moderate complexity
        if quality_score > 0.7 and 0.3 < complexity_score < 0.8:
            return "high"
        elif quality_score > 0.5:
            return "medium"
        else:
            return "low"
    
    def _suggest_augmentations(self, quality_analysis: Dict) -> List[str]:
        """Suggest augmentations based on quality analysis."""
        suggestions = []
        
        if quality_analysis.get("contrast", {}).get("contrast_level") == "low":
            suggestions.append("contrast_enhancement")
        
        if quality_analysis.get("sharpness", {}).get("sharpness_level") == "low":
            suggestions.append("sharpness_enhancement")
        
        if quality_analysis.get("noise", {}).get("noise_rating") == "high":
            suggestions.append("noise_reduction")
        
        if quality_analysis.get("resolution", {}).get("resolution_level") == "low":
            suggestions.append("resolution_upscaling")
        
        return suggestions
    
    def _generate_enhanced_drawing_id(self, file_path: str, discipline: str) -> str:
        """Generate unique drawing ID with enhanced metadata."""
        # Create hash from file content, discipline, and timestamp
        with open(file_path, 'rb') as f:
            content = f.read()
        
        hash_input = content + discipline.encode() + str(datetime.now().timestamp()).encode()
        drawing_hash = hashlib.md5(hash_input).hexdigest()[:12]
        
        return f"{discipline}_{drawing_hash}"
    
    def _copy_file_with_validation(self, source_path: str, dest_path: Path):
        """Copy file with validation."""
        import shutil
        try:
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied {source_path} to {dest_path}")
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            raise
    
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get enhanced statistics about collected data."""
        stats = {}
        
        for discipline in self.disciplines:
            discipline_stats = {
                "total_drawings": 0,
                "quality_distribution": {"excellent": 0, "good": 0, "fair": 0, "poor": 0},
                "complexity_distribution": {"simple": 0, "moderate": 0, "complex": 0, "very_complex": 0},
                "format_distribution": {},
                "training_priority": {"high": 0, "medium": 0, "low": 0}
            }
            
            # Count drawings and analyze metadata
            metadata_dir = self.base_path / "metadata" / discipline
            if metadata_dir.exists():
                for metadata_file in metadata_dir.glob("*.json"):
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        discipline_stats["total_drawings"] += 1
                        
                        # Quality distribution
                        quality_level = metadata.get("quality_analysis", {}).get("quality_level", "unknown")
                        if quality_level in discipline_stats["quality_distribution"]:
                            discipline_stats["quality_distribution"][quality_level] += 1
                        
                        # Complexity distribution
                        complexity_level = metadata.get("content_analysis", {}).get("complexity_level", "unknown")
                        if complexity_level in discipline_stats["complexity_distribution"]:
                            discipline_stats["complexity_distribution"][complexity_level] += 1
                        
                        # Format distribution
                        file_format = metadata.get("file_format", "unknown")
                        discipline_stats["format_distribution"][file_format] = discipline_stats["format_distribution"].get(file_format, 0) + 1
                        
                        # Training priority
                        training_priority = metadata.get("training_priority", "unknown")
                        if training_priority in discipline_stats["training_priority"]:
                            discipline_stats["training_priority"][training_priority] += 1
                    
                    except Exception as e:
                        logger.error(f"Error processing metadata file {metadata_file}: {e}")
            
            stats[discipline] = discipline_stats
        
        return stats

def main():
    """Main function for testing enhanced data collector."""
    collector = EnhancedDataCollector()
    
    # Example usage
    print("Enhanced Data Collector initialized")
    print("Available disciplines:", collector.disciplines)
    
    # Get statistics
    stats = collector.get_enhanced_statistics()
    print("\nEnhanced Statistics:")
    for discipline, discipline_stats in stats.items():
        print(f"\n{discipline.upper()}:")
        print(f"  Total drawings: {discipline_stats['total_drawings']}")
        print(f"  Quality distribution: {discipline_stats['quality_distribution']}")
        print(f"  Complexity distribution: {discipline_stats['complexity_distribution']}")
        print(f"  Training priority: {discipline_stats['training_priority']}")

if __name__ == "__main__":
    main() 