from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import logging
from ..core.database import get_db
from ..models.schemas import SteelSection, SteelSectionCreate, SteelElement, SteelElementCreate
from ..services.steel_database import SteelDatabaseService
from pathlib import Path
import shutil
import os

logger = logging.getLogger(__name__)

router = APIRouter(tags=["steel"])

@router.post("/sections/", response_model=SteelSection)
def create_steel_section(section: SteelSectionCreate, db: Session = Depends(get_db)):
    """Create a new steel section"""
    steel_service = SteelDatabaseService(db)
    return steel_service.add_steel_section(section)

@router.get("/sections/", response_model=List[SteelSection])
def get_all_steel_sections(db: Session = Depends(get_db)):
    """Get all steel sections"""
    steel_service = SteelDatabaseService(db)
    return steel_service.get_all_steel_sections()

@router.get("/sections/search/", response_model=List[SteelSection])
def search_steel_sections(query: str, db: Session = Depends(get_db)):
    """Search steel sections"""
    steel_service = SteelDatabaseService(db)
    return steel_service.search_steel_sections(query)

@router.get("/sections/{section_name}", response_model=SteelSection)
def get_steel_section(section_name: str, db: Session = Depends(get_db)):
    """Get steel section by name"""
    steel_service = SteelDatabaseService(db)
    section = steel_service.get_steel_section(section_name)
    if not section:
        raise HTTPException(status_code=404, detail="Steel section not found")
    return section

@router.post("/import-database/")
def import_steel_database(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import British Steel UK sections database from PDF"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads/steel_database")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Import British Steel database
    steel_service = SteelDatabaseService(db)
    result = steel_service.import_british_steel_database_from_pdf(str(file_path))
    
    # Clean up uploaded file
    os.remove(file_path)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@router.post("/detect-elements/{drawing_id}")
def detect_steel_elements(drawing_id: int, db: Session = Depends(get_db)):
    """Detect steel elements in a drawing"""
    from ..models.models import Drawing
    
    # Get drawing
    drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    # Get drawing file path
    drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
    if not os.path.exists(drawing_path):
        raise HTTPException(status_code=404, detail="Drawing file not found")
    
    # Detect steel elements
    steel_service = SteelDatabaseService(db)
    steel_elements = steel_service.detect_steel_elements_in_drawing(drawing_path, drawing_id)
    
    return {
        "drawing_id": drawing_id,
        "elements_detected": len(steel_elements),
        "elements": [
            {
                "id": element.id,
                "element_type": element.element_type,
                "section_name": element.section_name,
                "section_type": element.section_type,
                "length_mm": element.length_mm,
                "mass_kg": element.mass_kg,
                "confidence_score": element.confidence_score
            }
            for element in steel_elements
        ]
    }

@router.get("/elements/drawing/{drawing_id}", response_model=List[SteelElement])
def get_steel_elements_for_drawing(drawing_id: int, db: Session = Depends(get_db)):
    """Get steel elements for a specific drawing"""
    from ..models.models import SteelElement
    elements = db.query(SteelElement).filter(SteelElement.drawing_id == drawing_id).all()
    return elements

@router.get("/elements/project/{project_id}")
def get_steel_elements_for_project(project_id: int, db: Session = Depends(get_db)):
    """Get steel elements for a specific project"""
    from ..models.models import SteelElement, Drawing
    
    # Get all drawings for the project
    drawings = db.query(Drawing).filter(Drawing.project_id == project_id).all()
    drawing_ids = [drawing.id for drawing in drawings]
    
    # Get steel elements for all drawings
    elements = db.query(SteelElement).filter(SteelElement.drawing_id.in_(drawing_ids)).all()
    
    # Calculate totals
    total_mass = sum(element.mass_kg or 0 for element in elements)
    total_elements = len(elements)
    
    return {
        "project_id": project_id,
        "total_elements": total_elements,
        "total_mass_kg": total_mass,
        "elements": [
            {
                "id": element.id,
                "drawing_id": element.drawing_id,
                "element_type": element.element_type,
                "section_name": element.section_name,
                "section_type": element.section_type,
                "length_mm": element.length_mm,
                "mass_kg": element.mass_kg,
                "confidence_score": element.confidence_score
            }
            for element in elements
        ]
    }

@router.post("/calculate-mass/")
def calculate_steel_mass(section_name: str, length_mm: float, db: Session = Depends(get_db)):
    """Calculate mass for a steel section"""
    steel_service = SteelDatabaseService(db)
    mass_kg = steel_service.calculate_steel_mass(section_name, length_mm)
    
    if mass_kg is None:
        raise HTTPException(status_code=404, detail="Steel section not found")
    
    return {
        "section_name": section_name,
        "length_mm": length_mm,
        "mass_kg": mass_kg
    }

@router.post("/detect-sections-in-text/")
def detect_sections_in_text(text: str, db: Session = Depends(get_db)):
    """Detect steel sections in text"""
    steel_service = SteelDatabaseService(db)
    detected_sections = steel_service.detect_steel_sections_in_text(text)
    
    return {
        "text": text,
        "detected_sections": detected_sections,
        "count": len(detected_sections)
    } 