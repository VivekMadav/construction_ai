"""
Data Preprocessing Tool for Construction AI Training Data

This module provides tools to preprocess and prepare training data
for discipline-specific element detection models.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from PIL import Image
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import io
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Preprocesses training data for ML model training."""
    
    def __init__(self, base_path: str = "ml/data"):
        self.base_path = Path(base_path)
        self.disciplines = ["architectural", "structural", "civil", "mep"]
        self.output_formats = [".jpg", ".png"]
        self.target_size = (1024, 1024)  # Standard size for training
        
    def preprocess_drawing(self, 
                          drawing_id: str, 
                          discipline: str,
                          target_size: Optional[Tuple[int, int]] = None) -> str:
        """
        Preprocess a drawing for training.
        
        Args:
            drawing_id: Unique drawing identifier
            discipline: Discipline category
            target_size: Target image size (width, height)
            
        Returns:
            Path to preprocessed image
        """
        if discipline not in self.disciplines:
            raise ValueError(f"Invalid discipline: {discipline}")
        
        if target_size is None:
            target_size = self.target_size
        
        # Find raw drawing file
        raw_path = self.base_path / "raw" / discipline
        drawing_file = None
        
        for file_path in raw_path.iterdir():
            if file_path.stem == drawing_id:
                drawing_file = file_path
                break
        
        if drawing_file is None:
            raise FileNotFoundError(f"Drawing {drawing_id} not found in raw data")
        
        # Process based on file type
        if drawing_file.suffix.lower() == ".pdf":
            processed_path = self._process_pdf(drawing_file, drawing_id, discipline, target_size)
        else:
            processed_path = self._process_image(drawing_file, drawing_id, discipline, target_size)
        
        logger.info(f"Preprocessed drawing {drawing_id} for discipline {discipline}")
        return str(processed_path)
    
    def _process_pdf(self, 
                    pdf_path: Path, 
                    drawing_id: str, 
                    discipline: str,
                    target_size: Tuple[int, int]) -> Path:
        """Process PDF drawing and extract images."""
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        
        # Process first page (assuming single page drawings)
        page = pdf_document[0]
        
        # Convert to image
        mat = fitz.Matrix(2.0, 2.0)  # Scale factor for better quality
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Preprocess image
        processed_img = self._preprocess_image(img, target_size)
        
        # Save processed image
        output_path = self.base_path / "processed" / discipline / f"{drawing_id}.jpg"
        processed_img.save(output_path, "JPEG", quality=95)
        
        pdf_document.close()
        return output_path
    
    def _process_image(self, 
                      image_path: Path, 
                      drawing_id: str, 
                      discipline: str,
                      target_size: Tuple[int, int]) -> Path:
        """Process image file."""
        # Load image
        img = Image.open(image_path)
        
        # Preprocess image
        processed_img = self._preprocess_image(img, target_size)
        
        # Save processed image
        output_path = self.base_path / "processed" / discipline / f"{drawing_id}.jpg"
        processed_img.save(output_path, "JPEG", quality=95)
        
        return output_path
    
    def _preprocess_image(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Apply preprocessing steps to image."""
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize while maintaining aspect ratio
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Create new image with target size and white background
        new_img = Image.new("RGB", target_size, (255, 255, 255))
        
        # Center the image
        x = (target_size[0] - img.width) // 2
        y = (target_size[1] - img.height) // 2
        new_img.paste(img, (x, y))
        
        # Apply image enhancement
        enhanced_img = self._enhance_image(new_img)
        
        return enhanced_img
    
    def _enhance_image(self, img: Image.Image) -> Image.Image:
        """Apply image enhancement techniques."""
        # Convert to numpy array
        img_array = np.array(img)
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
        
        # Convert back to RGB
        enhanced_rgb = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
        
        return Image.fromarray(enhanced_rgb)
    
    def create_training_dataset(self, discipline: str, split_ratio: float = 0.8) -> Dict:
        """
        Create training dataset for a specific discipline.
        
        Args:
            discipline: Discipline category
            split_ratio: Ratio of training to validation data
            
        Returns:
            Dataset configuration
        """
        if discipline not in self.disciplines:
            raise ValueError(f"Invalid discipline: {discipline}")
        
        # Get all processed drawings
        processed_path = self.base_path / "processed" / discipline
        drawings = []
        
        for file_path in processed_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in [".jpg", ".png"]:
                drawings.append(file_path.stem)
        
        # Split into train/validation
        np.random.shuffle(drawings)
        split_idx = int(len(drawings) * split_ratio)
        
        train_drawings = drawings[:split_idx]
        val_drawings = drawings[split_idx:]
        
        # Create dataset configuration
        dataset_config = {
            "discipline": discipline,
            "total_drawings": len(drawings),
            "train_drawings": len(train_drawings),
            "val_drawings": len(val_drawings),
            "train_list": train_drawings,
            "val_list": val_drawings,
            "created_at": datetime.now().isoformat()
        }
        
        # Save dataset configuration
        dataset_path = self.base_path / "datasets" / discipline / "dataset_config.json"
        with open(dataset_path, 'w') as f:
            json.dump(dataset_config, f, indent=2)
        
        logger.info(f"Created dataset for {discipline}: {len(train_drawings)} train, {len(val_drawings)} val")
        return dataset_config
    
    def generate_annotation_visualization(self, 
                                        drawing_id: str, 
                                        discipline: str,
                                        save_path: Optional[str] = None) -> str:
        """
        Generate visualization of annotations on a drawing.
        
        Args:
            drawing_id: Drawing identifier
            discipline: Discipline category
            save_path: Optional path to save visualization
            
        Returns:
            Path to saved visualization
        """
        # Load processed image
        processed_path = self.base_path / "processed" / discipline / f"{drawing_id}.jpg"
        if not processed_path.exists():
            raise FileNotFoundError(f"Processed image not found: {processed_path}")
        
        # Load annotation
        annotation_path = self.base_path / "annotations" / discipline / f"{drawing_id}.json"
        if not annotation_path.exists():
            raise FileNotFoundError(f"Annotation not found: {annotation_path}")
        
        with open(annotation_path, 'r') as f:
            annotation_data = json.load(f)
        
        # Load image
        img = cv2.imread(str(processed_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Draw annotations
        for element in annotation_data["elements"]:
            bbox = element["bbox"]
            element_type = element["type"]
            
            # Draw bounding box
            cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
            
            # Add label
            cv2.putText(img, element_type, (bbox[0], bbox[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Save visualization
        if save_path is None:
            viz_path = self.base_path / "datasets" / discipline / f"{drawing_id}_annotated.jpg"
        else:
            viz_path = Path(save_path)
        
        plt.figure(figsize=(12, 8))
        plt.imshow(img)
        plt.title(f"Annotations for {drawing_id} ({discipline})")
        plt.axis('off')
        plt.savefig(viz_path, bbox_inches='tight', dpi=150)
        plt.close()
        
        return str(viz_path)

class DataValidator:
    """Validates training data quality and consistency."""
    
    def __init__(self, base_path: str = "ml/data"):
        self.base_path = Path(base_path)
        self.disciplines = ["architectural", "structural", "civil", "mep"]
    
    def validate_dataset(self, discipline: str) -> Dict:
        """
        Validate a complete dataset for a discipline.
        
        Args:
            discipline: Discipline category
            
        Returns:
            Validation results
        """
        if discipline not in self.disciplines:
            raise ValueError(f"Invalid discipline: {discipline}")
        
        validation_results = {
            "discipline": discipline,
            "status": "valid",
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Check raw data
        raw_path = self.base_path / "raw" / discipline
        if not raw_path.exists():
            validation_results["errors"].append("Raw data directory not found")
            validation_results["status"] = "invalid"
        
        # Check processed data
        processed_path = self.base_path / "processed" / discipline
        if not processed_path.exists():
            validation_results["errors"].append("Processed data directory not found")
            validation_results["status"] = "invalid"
        
        # Check annotations
        annotation_path = self.base_path / "annotations" / discipline
        if not annotation_path.exists():
            validation_results["warnings"].append("Annotations directory not found")
        
        # Count files
        raw_count = len(list(raw_path.glob("*"))) if raw_path.exists() else 0
        processed_count = len(list(processed_path.glob("*.jpg"))) if processed_path.exists() else 0
        annotation_count = len(list(annotation_path.glob("*.json"))) if annotation_path.exists() else 0
        
        validation_results["statistics"] = {
            "raw_files": raw_count,
            "processed_files": processed_count,
            "annotations": annotation_count
        }
        
        # Check for missing processed files
        if raw_count > processed_count:
            validation_results["warnings"].append(f"Missing processed files: {raw_count - processed_count}")
        
        # Check for missing annotations
        if processed_count > annotation_count:
            validation_results["warnings"].append(f"Missing annotations: {processed_count - annotation_count}")
        
        return validation_results

def main():
    """Example usage of the data preprocessor."""
    preprocessor = DataPreprocessor()
    validator = DataValidator()
    
    # Example: Preprocess a drawing
    # processed_path = preprocessor.preprocess_drawing("sample_drawing", "architectural")
    
    # Example: Create dataset
    # dataset_config = preprocessor.create_training_dataset("architectural")
    
    # Example: Validate dataset
    # validation_results = validator.validate_dataset("architectural")
    # print("Validation Results:")
    # print(json.dumps(validation_results, indent=2))

if __name__ == "__main__":
    main() 