"""
Concrete API endpoints for detecting and measuring concrete elements
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
import json
import logging

from ..core.database import get_db
from ..models.models import Drawing, ConcreteElement
from ..services.concrete_processor import ConcreteProcessor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["concrete"])

@router.post("/detect-elements/{drawing_id}")
async def detect_concrete_elements(drawing_id: int, db: Session = Depends(get_db)):
    """Detect concrete elements in a drawing and calculate volumes"""
    try:
        # Get drawing
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Construct drawing path
        drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
        if not os.path.exists(drawing_path):
            raise HTTPException(status_code=404, detail="Drawing file not found")
        
        # Process drawing for concrete elements
        processor = ConcreteProcessor()
        concrete_elements = processor.process_drawing_for_concrete(drawing_path)
        
        # Save to database
        saved_elements = []
        for element in concrete_elements:
            db_element = ConcreteElement(
                drawing_id=drawing_id,
                element_type=element.element_type,
                concrete_grade=element.grade,
                length_m=element.dimensions.length,
                width_m=element.dimensions.width,
                depth_m=element.dimensions.depth,
                volume_m3=element.dimensions.volume,
                confidence_score=element.dimensions.confidence,
                description=element.description,
                text_references=json.dumps([element.dimensions.text_reference]),
                location=element.location
            )
            db.add(db_element)
            saved_elements.append(db_element)
        
        db.commit()
        
        # Generate report
        report = processor.generate_concrete_report(concrete_elements)
        
        return {
            "message": f"Detected {len(saved_elements)} concrete elements",
            "elements": report,
            "drawing_id": drawing_id
        }
        
    except Exception as e:
        logger.error(f"Error detecting concrete elements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/elements/drawing/{drawing_id}")
async def get_concrete_elements(drawing_id: int, db: Session = Depends(get_db)):
    """Get concrete elements for a specific drawing"""
    try:
        # Check if drawing exists
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Get concrete elements
        elements = db.query(ConcreteElement).filter(
            ConcreteElement.drawing_id == drawing_id
        ).all()
        
        # Format response
        formatted_elements = []
        for element in elements:
            formatted_elements.append({
                "id": element.id,
                "element_type": element.element_type,
                "concrete_grade": element.concrete_grade,
                "length_m": element.length_m,
                "width_m": element.width_m,
                "depth_m": element.depth_m,
                "volume_m3": element.volume_m3,
                "confidence_score": element.confidence_score,
                "location": element.location,
                "description": element.description,
                "created_at": element.created_at.isoformat() if element.created_at else None
            })
        
        return {
            "drawing_id": drawing_id,
            "elements": formatted_elements,
            "total_elements": len(formatted_elements),
            "total_volume_m3": sum(e.volume_m3 for e in elements)
        }
        
    except Exception as e:
        logger.error(f"Error getting concrete elements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/drawing/{drawing_id}")
async def get_concrete_report(drawing_id: int, db: Session = Depends(get_db)):
    """Get a comprehensive concrete measurement report for a drawing"""
    try:
        # Check if drawing exists
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Get concrete elements
        elements = db.query(ConcreteElement).filter(
            ConcreteElement.drawing_id == drawing_id
        ).all()
        
        if not elements:
            return {
                "drawing_id": drawing_id,
                "message": "No concrete elements found",
                "total_volume_m3": 0,
                "element_count": 0
            }
        
        # Generate report
        processor = ConcreteProcessor()
        
        # Convert database elements to ConcreteElement objects for report generation
        concrete_elements = []
        for db_element in elements:
            from ..services.concrete_processor import ConcreteElement as ProcElement, ConcreteDimension
            
            dimension = ConcreteDimension(
                length=db_element.length_m,
                width=db_element.width_m,
                depth=db_element.depth_m,
                volume=db_element.volume_m3,
                confidence=db_element.confidence_score,
                text_reference="Database element"
            )
            
            proc_element = ProcElement(
                element_type=db_element.element_type,
                dimensions=dimension,
                grade=db_element.concrete_grade,
                location=db_element.location,
                description=db_element.description
            )
            concrete_elements.append(proc_element)
        
        report = processor.generate_concrete_report(concrete_elements)
        report["drawing_id"] = drawing_id
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating concrete report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/project/{project_id}")
async def get_project_concrete_summary(project_id: int, db: Session = Depends(get_db)):
    """Get concrete summary for all drawings in a project"""
    try:
        # Get all drawings for the project
        drawings = db.query(Drawing).filter(Drawing.project_id == project_id).all()
        
        if not drawings:
            raise HTTPException(status_code=404, detail="Project not found")
        
        total_volume = 0
        total_elements = 0
        by_type = {}
        by_grade = {}
        
        for drawing in drawings:
            elements = db.query(ConcreteElement).filter(
                ConcreteElement.drawing_id == drawing.id
            ).all()
            
            for element in elements:
                total_volume += element.volume_m3
                total_elements += 1
                
                # Group by type
                if element.element_type not in by_type:
                    by_type[element.element_type] = {"count": 0, "volume_m3": 0}
                by_type[element.element_type]["count"] += 1
                by_type[element.element_type]["volume_m3"] += element.volume_m3
                
                # Group by grade
                if element.concrete_grade not in by_grade:
                    by_grade[element.concrete_grade] = {"count": 0, "volume_m3": 0}
                by_grade[element.concrete_grade]["count"] += 1
                by_grade[element.concrete_grade]["volume_m3"] += element.volume_m3
        
        # Calculate percentages
        for element_type in by_type:
            by_type[element_type]["percentage"] = (
                by_type[element_type]["volume_m3"] / total_volume * 100
            ) if total_volume > 0 else 0
        
        for grade in by_grade:
            by_grade[grade]["percentage"] = (
                by_grade[grade]["volume_m3"] / total_volume * 100
            ) if total_volume > 0 else 0
        
        return {
            "project_id": project_id,
            "total_volume_m3": total_volume,
            "total_elements": total_elements,
            "by_type": by_type,
            "by_grade": by_grade,
            "drawing_count": len(drawings)
        }
        
    except Exception as e:
        logger.error(f"Error getting project concrete summary: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 