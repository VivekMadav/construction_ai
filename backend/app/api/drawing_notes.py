"""
Drawing Notes API endpoints

This module provides API endpoints for analyzing drawing notes, title blocks,
and specifications to extract critical information like concrete strength,
steel grades, and construction details.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
import json
import logging

from ..core.database import get_db
from ..models.models import Drawing
from ..services.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["drawing-notes"])

@router.post("/analyze-notes/drawing/{drawing_id}")
async def analyze_drawing_notes(drawing_id: int, db: Session = Depends(get_db)):
    """Analyze drawing notes and extract specifications."""
    try:
        # Get drawing
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Construct drawing path
        drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
        if not os.path.exists(drawing_path):
            raise HTTPException(status_code=404, detail="Drawing file not found")
        
        # Initialize processor
        processor = PDFProcessor()
        
        if not processor.notes_analyzer:
            raise HTTPException(
                status_code=400, 
                detail="Drawing notes analyzer not available"
            )
        
        # Analyze drawing notes
        specifications = processor.notes_analyzer.analyze_drawing_notes(drawing_path)
        
        # Generate notes report
        notes_report = processor.notes_analyzer.generate_notes_report(specifications)
        
        return {
            "drawing_id": drawing_id,
            "filename": drawing.filename,
            "notes_analysis": {
                "concrete_specifications": len(specifications.concrete_specs),
                "steel_specifications": len(specifications.steel_specs),
                "other_materials": len(specifications.other_materials),
                "general_notes": len(specifications.general_notes),
                "construction_notes": len(specifications.construction_notes),
                "dimension_notes": len(specifications.dimension_notes),
                "revision_notes": len(specifications.revision_notes)
            },
            "material_specifications": {
                "concrete": [spec.grade for spec in specifications.concrete_specs],
                "steel": [spec.grade for spec in specifications.steel_specs],
                "other": [f"{spec.material_type.value}: {spec.grade}" for spec in specifications.other_materials]
            },
            "critical_information": specifications.critical_info,
            "notes_content": {
                "general_notes": specifications.general_notes,
                "construction_notes": specifications.construction_notes,
                "dimension_notes": specifications.dimension_notes,
                "revision_notes": specifications.revision_notes
            },
            "detailed_specifications": notes_report
        }
        
    except Exception as e:
        logger.error(f"Error analyzing drawing notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-notes/drawing/{drawing_id}")
async def apply_notes_to_elements(drawing_id: int, elements: List[Dict], db: Session = Depends(get_db)):
    """Apply drawing notes to detected elements."""
    try:
        # Get drawing
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Construct drawing path
        drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
        if not os.path.exists(drawing_path):
            raise HTTPException(status_code=404, detail="Drawing file not found")
        
        # Initialize processor
        processor = PDFProcessor()
        
        if not processor.notes_analyzer:
            raise HTTPException(
                status_code=400, 
                detail="Drawing notes analyzer not available"
            )
        
        # Apply notes to elements
        enhanced_elements, notes_report = processor.analyze_drawing_notes_and_apply(
            drawing_path, elements
        )
        
        return {
            "drawing_id": drawing_id,
            "original_elements": len(elements),
            "enhanced_elements": len(enhanced_elements),
            "enhanced_elements": enhanced_elements,
            "notes_report": notes_report,
            "improvements": {
                "elements_with_material_specs": len([e for e in enhanced_elements if 'material' in e]),
                "elements_with_concrete_specs": len([e for e in enhanced_elements if 'concrete_grade' in e]),
                "elements_with_steel_specs": len([e for e in enhanced_elements if 'steel_grade' in e]),
                "elements_with_critical_info": len([e for e in enhanced_elements if 'critical_info' in e])
            }
        }
        
    except Exception as e:
        logger.error(f"Error applying notes to elements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notes-statistics/drawing/{drawing_id}")
async def get_drawing_notes_statistics(drawing_id: int, db: Session = Depends(get_db)):
    """Get statistics about drawing notes analysis."""
    try:
        # Get drawing
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Construct drawing path
        drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
        if not os.path.exists(drawing_path):
            raise HTTPException(status_code=404, detail="Drawing file not found")
        
        # Initialize processor
        processor = PDFProcessor()
        
        if not processor.notes_analyzer:
            raise HTTPException(
                status_code=400, 
                detail="Drawing notes analyzer not available"
            )
        
        # Analyze drawing notes
        specifications = processor.notes_analyzer.analyze_drawing_notes(drawing_path)
        
        # Calculate statistics
        stats = {
            "drawing_id": drawing_id,
            "filename": drawing.filename,
            "total_specifications": len(specifications.concrete_specs) + len(specifications.steel_specs) + len(specifications.other_materials),
            "concrete_specifications": len(specifications.concrete_specs),
            "steel_specifications": len(specifications.steel_specs),
            "other_material_specifications": len(specifications.other_materials),
            "total_notes": len(specifications.general_notes) + len(specifications.construction_notes) + len(specifications.dimension_notes) + len(specifications.revision_notes),
            "general_notes": len(specifications.general_notes),
            "construction_notes": len(specifications.construction_notes),
            "dimension_notes": len(specifications.dimension_notes),
            "revision_notes": len(specifications.revision_notes),
            "critical_information_items": len(specifications.critical_info),
            "notes_analysis_available": True
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting drawing notes statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-specifications/drawing/{drawing_id}")
async def extract_material_specifications(drawing_id: int, db: Session = Depends(get_db)):
    """Extract material specifications from drawing notes."""
    try:
        # Get drawing
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Construct drawing path
        drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
        if not os.path.exists(drawing_path):
            raise HTTPException(status_code=404, detail="Drawing file not found")
        
        # Initialize processor
        processor = PDFProcessor()
        
        if not processor.notes_analyzer:
            raise HTTPException(
                status_code=400, 
                detail="Drawing notes analyzer not available"
            )
        
        # Analyze drawing notes
        specifications = processor.notes_analyzer.analyze_drawing_notes(drawing_path)
        
        # Extract detailed specifications
        concrete_specs = []
        for spec in specifications.concrete_specs:
            concrete_specs.append({
                "grade": spec.grade,
                "strength": spec.strength,
                "specification": spec.specification,
                "notes": spec.notes,
                "confidence": spec.confidence
            })
        
        steel_specs = []
        for spec in specifications.steel_specs:
            steel_specs.append({
                "grade": spec.grade,
                "specification": spec.specification,
                "notes": spec.notes,
                "confidence": spec.confidence
            })
        
        other_specs = []
        for spec in specifications.other_materials:
            other_specs.append({
                "material_type": spec.material_type.value,
                "grade": spec.grade,
                "specification": spec.specification,
                "notes": spec.notes,
                "confidence": spec.confidence
            })
        
        return {
            "drawing_id": drawing_id,
            "filename": drawing.filename,
            "concrete_specifications": concrete_specs,
            "steel_specifications": steel_specs,
            "other_material_specifications": other_specs,
            "critical_information": specifications.critical_info,
            "extraction_summary": {
                "total_specifications": len(concrete_specs) + len(steel_specs) + len(other_specs),
                "concrete_count": len(concrete_specs),
                "steel_count": len(steel_specs),
                "other_count": len(other_specs),
                "critical_info_count": len(specifications.critical_info)
            }
        }
        
    except Exception as e:
        logger.error(f"Error extracting material specifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notes-capabilities")
async def get_notes_analysis_capabilities():
    """Get information about drawing notes analysis capabilities."""
    try:
        processor = PDFProcessor()
        
        capabilities = {
            "notes_analyzer_available": processor.notes_analyzer is not None,
            "supported_note_types": [
                "title_block",
                "general_notes", 
                "specifications",
                "material_notes",
                "construction_notes",
                "dimension_notes",
                "revision_notes"
            ],
            "supported_materials": [
                "concrete",
                "steel", 
                "timber",
                "masonry",
                "insulation",
                "finishes",
                "mep"
            ],
            "extraction_patterns": {
                "concrete_patterns": [
                    "CONCRETE GRADE: C30",
                    "CONCRETE STRENGTH: 30 N/mm²", 
                    "C30 CONCRETE",
                    "F30 CONCRETE"
                ],
                "steel_patterns": [
                    "STEEL GRADE: S355",
                    "REINFORCEMENT: B500B",
                    "S355 STEEL"
                ],
                "critical_info_patterns": [
                    "FIRE RATING: 2 HOURS",
                    "LOAD CAPACITY: 50 KN",
                    "SEISMIC: ZONE 3"
                ]
            },
            "features": [
                "Title block analysis",
                "Material specification extraction",
                "Critical information detection",
                "Construction notes processing",
                "Element enhancement with notes",
                "Specification application to elements"
            ]
        }
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Error getting notes analysis capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 