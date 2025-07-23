"""
Data Collection Tool for Construction AI Training Data

This module provides tools to collect, organize, and preprocess training data
for discipline-specific element detection.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingDataCollector:
    """Manages collection and organization of training data by discipline."""
    
    def __init__(self, base_path: str = "ml/data"):
        self.base_path = Path(base_path)
        self.disciplines = ["architectural", "structural", "civil", "mep"]
        self.supported_formats = [".pdf", ".dwg", ".dxf", ".jpg", ".png", ".tiff"]
        
        # Create directory structure
        self._create_directory_structure()
        
    def _create_directory_structure(self):
        """Create the training data directory structure."""
        directories = [
            "raw", "processed", "annotations", "metadata", "datasets"
        ]
        
        for discipline in self.disciplines:
            for directory in directories:
                path = self.base_path / directory / discipline
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {path}")
    
    def collect_drawing(self, 
                       file_path: str, 
                       discipline: str, 
                       metadata: Optional[Dict] = None) -> str:
        """
        Collect a drawing file and organize it by discipline.
        
        Args:
            file_path: Path to the drawing file
            discipline: Discipline category (architectural, structural, civil, mep)
            metadata: Optional metadata about the drawing
            
        Returns:
            Unique drawing ID
        """
        if discipline not in self.disciplines:
            raise ValueError(f"Invalid discipline: {discipline}")
        
        # Validate file format
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Generate unique drawing ID
        drawing_id = self._generate_drawing_id(file_path, discipline)
        
        # Copy file to raw data directory
        raw_path = self.base_path / "raw" / discipline / f"{drawing_id}{file_ext}"
        shutil.copy2(file_path, raw_path)
        
        # Save metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "drawing_id": drawing_id,
            "discipline": discipline,
            "original_path": str(file_path),
            "collected_at": datetime.now().isoformat(),
            "file_size": os.path.getsize(file_path),
            "file_format": file_ext
        })
        
        metadata_path = self.base_path / "metadata" / discipline / f"{drawing_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Collected drawing {drawing_id} for discipline {discipline}")
        return drawing_id
    
    def _generate_drawing_id(self, file_path: str, discipline: str) -> str:
        """Generate a unique drawing ID based on file content and discipline."""
        # Create hash from file content and discipline
        with open(file_path, 'rb') as f:
            content = f.read()
        
        hash_input = content + discipline.encode()
        file_hash = hashlib.md5(hash_input).hexdigest()[:8]
        
        return f"{discipline}_{file_hash}"
    
    def get_drawings_by_discipline(self, discipline: str) -> List[str]:
        """Get all drawing IDs for a specific discipline."""
        if discipline not in self.disciplines:
            raise ValueError(f"Invalid discipline: {discipline}")
        
        raw_path = self.base_path / "raw" / discipline
        drawings = []
        
        for file_path in raw_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                drawing_id = file_path.stem
                drawings.append(drawing_id)
        
        return drawings
    
    def get_drawing_metadata(self, drawing_id: str, discipline: str) -> Dict:
        """Get metadata for a specific drawing."""
        metadata_path = self.base_path / "metadata" / discipline / f"{drawing_id}.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found for drawing {drawing_id}")
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def get_statistics(self) -> Dict:
        """Get statistics about collected training data."""
        stats = {}
        
        for discipline in self.disciplines:
            drawings = self.get_drawings_by_discipline(discipline)
            stats[discipline] = {
                "total_drawings": len(drawings),
                "file_formats": self._get_format_distribution(discipline),
                "total_size_mb": self._get_total_size_mb(discipline)
            }
        
        return stats
    
    def _get_format_distribution(self, discipline: str) -> Dict[str, int]:
        """Get distribution of file formats for a discipline."""
        raw_path = self.base_path / "raw" / discipline
        formats = {}
        
        for file_path in raw_path.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                formats[ext] = formats.get(ext, 0) + 1
        
        return formats
    
    def _get_total_size_mb(self, discipline: str) -> float:
        """Get total size of all files for a discipline in MB."""
        raw_path = self.base_path / "raw" / discipline
        total_size = 0
        
        for file_path in raw_path.iterdir():
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return round(total_size / (1024 * 1024), 2)

class AnnotationManager:
    """Manages element annotations for training data."""
    
    def __init__(self, base_path: str = "ml/data"):
        self.base_path = Path(base_path)
        self.disciplines = ["architectural", "structural", "civil", "mep"]
    
    def create_annotation(self, 
                         drawing_id: str, 
                         discipline: str, 
                         elements: List[Dict]) -> str:
        """
        Create an annotation file for a drawing.
        
        Args:
            drawing_id: Unique drawing identifier
            discipline: Discipline category
            elements: List of detected elements with annotations
            
        Returns:
            Annotation file path
        """
        if discipline not in self.disciplines:
            raise ValueError(f"Invalid discipline: {discipline}")
        
        annotation_data = {
            "drawing_id": drawing_id,
            "discipline": discipline,
            "created_at": datetime.now().isoformat(),
            "elements": elements,
            "total_elements": len(elements)
        }
        
        annotation_path = self.base_path / "annotations" / discipline / f"{drawing_id}.json"
        
        with open(annotation_path, 'w') as f:
            json.dump(annotation_data, f, indent=2)
        
        logger.info(f"Created annotation for drawing {drawing_id}")
        return str(annotation_path)
    
    def get_annotation(self, drawing_id: str, discipline: str) -> Dict:
        """Get annotation data for a specific drawing."""
        annotation_path = self.base_path / "annotations" / discipline / f"{drawing_id}.json"
        
        if not annotation_path.exists():
            raise FileNotFoundError(f"Annotation not found for drawing {drawing_id}")
        
        with open(annotation_path, 'r') as f:
            return json.load(f)
    
    def validate_annotation(self, annotation_data: Dict) -> Tuple[bool, List[str]]:
        """Validate annotation data format and content."""
        errors = []
        
        # Check required fields
        required_fields = ["drawing_id", "discipline", "elements"]
        for field in required_fields:
            if field not in annotation_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate discipline
        if "discipline" in annotation_data:
            if annotation_data["discipline"] not in self.disciplines:
                errors.append(f"Invalid discipline: {annotation_data['discipline']}")
        
        # Validate elements
        if "elements" in annotation_data:
            elements = annotation_data["elements"]
            if not isinstance(elements, list):
                errors.append("Elements must be a list")
            else:
                for i, element in enumerate(elements):
                    element_errors = self._validate_element(element, i)
                    errors.extend(element_errors)
        
        return len(errors) == 0, errors
    
    def _validate_element(self, element: Dict, index: int) -> List[str]:
        """Validate individual element annotation."""
        errors = []
        
        required_element_fields = ["id", "type", "bbox"]
        for field in required_element_fields:
            if field not in element:
                errors.append(f"Element {index}: Missing required field '{field}'")
        
        # Validate bbox format
        if "bbox" in element:
            bbox = element["bbox"]
            if not isinstance(bbox, list) or len(bbox) != 4:
                errors.append(f"Element {index}: Bbox must be a list of 4 coordinates")
            else:
                for coord in bbox:
                    if not isinstance(coord, (int, float)):
                        errors.append(f"Element {index}: Bbox coordinates must be numbers")
        
        return errors

def main():
    """Example usage of the training data collector."""
    collector = TrainingDataCollector()
    annotation_mgr = AnnotationManager()
    
    # Example: Collect a drawing
    # drawing_id = collector.collect_drawing(
    #     "path/to/drawing.pdf",
    #     "architectural",
    #     {"project": "Sample Project", "scale": "1:100"}
    # )
    
    # Example: Create annotation
    # elements = [
    #     {
    #         "id": "wall_001",
    #         "type": "wall",
    #         "bbox": [100, 100, 200, 150],
    #         "confidence": 0.95,
    #         "properties": {"thickness": "200mm", "material": "concrete"}
    #     }
    # ]
    # annotation_mgr.create_annotation(drawing_id, "architectural", elements)
    
    # Print statistics
    stats = collector.get_statistics()
    print("Training Data Statistics:")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main() 