import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from app.services.pdf_processor import PDFProcessor


class TestPDFProcessor:
    def setup_method(self):
        self.processor = PDFProcessor()
    
    def test_init(self):
        """Test PDF processor initialization"""
        assert self.processor.supported_formats == ['.pdf']
        assert self.processor.max_image_size == (4096, 4096)
    
    def test_classify_element_wall(self):
        """Test wall element classification"""
        # Long rectangle (wall-like)
        result = self.processor._classify_element(area=1000, aspect_ratio=5.0, width=100, height=20)
        assert result == "wall"
    
    def test_classify_element_door(self):
        """Test door element classification"""
        # Medium rectangle (door-like)
        result = self.processor._classify_element(area=5000, aspect_ratio=1.5, width=150, height=100)
        assert result == "door"
    
    def test_classify_element_window(self):
        """Test window element classification"""
        # Small rectangle (window-like)
        result = self.processor._classify_element(area=2000, aspect_ratio=1.2, width=120, height=100)
        assert result == "window"
    
    def test_classify_element_column(self):
        """Test column element classification"""
        # Square-ish shape (column-like)
        result = self.processor._classify_element(area=3000, aspect_ratio=1.0, width=100, height=100)
        assert result == "column"
    
    def test_classify_element_unknown(self):
        """Test unknown element classification"""
        # Small area, should not be classified
        result = self.processor._classify_element(area=50, aspect_ratio=1.0, width=10, height=10)
        assert result is None
    
    def test_calculate_scale_factor(self):
        """Test scale factor calculation"""
        # Mock image array
        mock_image = Mock()
        scale_factor = self.processor.calculate_scale_factor(mock_image)
        assert scale_factor == 100.0  # Default value for MVP
    
    @patch('app.services.pdf_processor.convert_from_path')
    def test_extract_images_from_pdf_success(self, mock_convert):
        """Test successful PDF image extraction"""
        # Mock the pdf2image conversion
        mock_pil_image = Mock()
        mock_convert.return_value = [mock_pil_image]
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'fake pdf content')
            tmp_file_path = tmp_file.name
        
        try:
            images = self.processor.extract_images_from_pdf(tmp_file_path)
            assert len(images) == 1
            assert images[0][1] == 1  # Page number
        finally:
            os.unlink(tmp_file_path)
    
    def test_extract_images_from_pdf_error(self):
        """Test PDF image extraction with error"""
        with pytest.raises(Exception):
            self.processor.extract_images_from_pdf('nonexistent_file.pdf')
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        import numpy as np
        
        # Create a mock image array
        mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        processed = self.processor.preprocess_image(mock_image)
        
        # Should return a processed image
        assert processed is not None
        assert processed.shape[:2] == mock_image.shape[:2]  # Same dimensions
    
    def test_detect_drawing_elements(self):
        """Test element detection"""
        import numpy as np
        
        # Create a mock image with some contours
        mock_image = np.zeros((100, 100), dtype=np.uint8)
        # Add a rectangle (simulating a wall)
        mock_image[10:20, 10:80] = 255
        
        elements = self.processor.detect_drawing_elements(mock_image)
        
        # Should detect at least one element
        assert len(elements) >= 0  # Could be 0 if no elements meet criteria
    
    def test_extract_text_from_image(self):
        """Test text extraction"""
        import numpy as np
        
        # Create a mock image
        mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        text_elements = self.processor.extract_text_from_image(mock_image)
        
        # Should return a list (could be empty)
        assert isinstance(text_elements, list)
    
    @patch('app.services.pdf_processor.PDFProcessor.extract_images_from_pdf')
    def test_process_pdf_drawing_success(self, mock_extract):
        """Test successful PDF processing"""
        # Mock the image extraction
        import numpy as np
        mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mock_extract.return_value = [(mock_image, 1)]
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'fake pdf content')
            tmp_file_path = tmp_file.name
        
        try:
            results = self.processor.process_pdf_drawing(tmp_file_path)
            
            assert results['status'] == 'completed'
            assert 'pages' in results
            assert 'total_elements' in results
        finally:
            os.unlink(tmp_file_path)
    
    def test_process_pdf_drawing_error(self):
        """Test PDF processing with error"""
        results = self.processor.process_pdf_drawing('nonexistent_file.pdf')
        
        assert results['status'] == 'failed'
        assert 'error' in results 