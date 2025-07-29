"""
Enhanced Analysis API endpoints with cross-drawing references

This module provides API endpoints for enhanced drawing analysis that includes
cross-drawing reference analysis for improved measurement accuracy.
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

router = APIRouter(tags=["enhanced-analysis"])

@router.post("/drawing/{drawing_id}")
async def enhanced_drawing_analysis(drawing_id: int, db: Session = Depends(get_db)):
    """Perform enhanced analysis with cross-drawing references."""
    try:
        # Get drawing
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Construct drawing path
        drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
        if not os.path.exists(drawing_path):
            raise HTTPException(status_code=404, detail="Drawing file not found")
        
        # Initialize enhanced processor
        processor = PDFProcessor()
        
        # Perform enhanced analysis
        enhanced_results = processor.process_drawing_with_cross_references(
            drawing_id, drawing_path, drawing.discipline or "architectural"
        )
        
        if enhanced_results['status'] != 'success':
            raise HTTPException(status_code=500, detail=enhanced_results['message'])
        
        return {
            "drawing_id": drawing_id,
            "enhanced_elements": enhanced_results["elements"],
            "cross_references": enhanced_results["cross_references"],
            "measurement_confidence": enhanced_results["measurement_confidence"],
            "completeness_score": enhanced_results["completeness_score"],
            "element_count": enhanced_results["element_count"],
            "reference_count": enhanced_results["reference_count"]
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cross-references/drawing/{drawing_id}")
async def get_cross_references(drawing_id: int, db: Session = Depends(get_db)):
    """Get cross-references for a drawing."""
    try:
        # Get drawing
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Get cross-references
        processor = PDFProcessor()
        cross_references = processor.get_drawing_cross_references(drawing_id)
        
        return {
            "drawing_id": drawing_id,
            "cross_references": cross_references,
            "reference_count": len(cross_references)
        }
        
    except Exception as e:
        logger.error(f"Error getting cross-references: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{project_id}")
async def enhanced_project_analysis(project_id: int, db: Session = Depends(get_db)):
    """Perform enhanced analysis for all drawings in a project."""
    try:
        # Get all drawings for the project
        drawings = db.query(Drawing).filter(Drawing.project_id == project_id).all()
        
        if not drawings:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Initialize processor
        processor = PDFProcessor()
        
        # Process each drawing with enhanced analysis
        project_results = {
            "project_id": project_id,
            "drawings": [],
            "total_elements": 0,
            "total_references": 0,
            "average_confidence": 0.0,
            "average_completeness": 0.0
        }
        
        total_confidence = 0.0
        total_completeness = 0.0
        processed_drawings = 0
        
        for drawing in drawings:
            try:
                drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
                if os.path.exists(drawing_path):
                    # Perform enhanced analysis
                    enhanced_results = processor.process_drawing_with_cross_references(
                        drawing.id, drawing_path, drawing.discipline or "architectural"
                    )
                    
                    if enhanced_results['status'] == 'success':
                        drawing_result = {
                            "drawing_id": drawing.id,
                            "filename": drawing.filename,
                            "discipline": drawing.discipline,
                            "element_count": enhanced_results["element_count"],
                            "reference_count": enhanced_results["reference_count"],
                            "measurement_confidence": enhanced_results["measurement_confidence"],
                            "completeness_score": enhanced_results["completeness_score"]
                        }
                        
                        project_results["drawings"].append(drawing_result)
                        project_results["total_elements"] += enhanced_results["element_count"]
                        project_results["total_references"] += enhanced_results["reference_count"]
                        
                        total_confidence += enhanced_results["measurement_confidence"]
                        total_completeness += enhanced_results["completeness_score"]
                        processed_drawings += 1
                        
            except Exception as e:
                logger.error(f"Error processing drawing {drawing.id}: {e}")
                continue
        
        # Calculate averages
        if processed_drawings > 0:
            project_results["average_confidence"] = total_confidence / processed_drawings
            project_results["average_completeness"] = total_completeness / processed_drawings
        
        return project_results
        
    except Exception as e:
        logger.error(f"Error in enhanced project analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_enhanced_analysis_statistics(db: Session = Depends(get_db)):
    """Get statistics about enhanced analysis capabilities."""
    try:
        processor = PDFProcessor()
        
        # Check if reference analysis is available
        reference_analysis_available = processor.reference_analyzer is not None
        enhanced_measurement_available = processor.enhanced_measurement is not None
        
        # Get reference statistics if available
        reference_stats = {}
        if processor.reference_analyzer:
            reference_stats = processor.reference_analyzer.get_reference_statistics()
        
        return {
            "reference_analysis_available": reference_analysis_available,
            "enhanced_measurement_available": enhanced_measurement_available,
            "reference_statistics": reference_stats,
            "capabilities": {
                "cross_drawing_analysis": reference_analysis_available,
                "enhanced_measurement": enhanced_measurement_available,
                "reference_detection": reference_analysis_available,
                "measurement_validation": enhanced_measurement_available
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting enhanced analysis statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-measurements")
async def validate_measurements_across_drawings(
    drawing_ids: List[int], 
    db: Session = Depends(get_db)
):
    """Validate measurements across multiple drawings."""
    try:
        processor = PDFProcessor()
        
        if not processor.reference_analyzer or not processor.enhanced_measurement:
            raise HTTPException(
                status_code=400, 
                detail="Enhanced analysis not available"
            )
        
        validation_results = []
        
        for drawing_id in drawing_ids:
            # Get drawing
            drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
            if not drawing:
                continue
            
            drawing_path = f"uploads/{drawing.project_id}/{drawing.filename}"
            if not os.path.exists(drawing_path):
                continue
            
            try:
                # Analyze references
                references = processor.reference_analyzer.analyze_drawing_references(
                    str(drawing_id), drawing_path
                )
                
                validation_result = {
                    "drawing_id": drawing_id,
                    "filename": drawing.filename,
                    "reference_count": len(references),
                    "references": [
                        {
                            "target_drawing_id": ref.target_drawing_id,
                            "reference_type": ref.reference_type.value,
                            "reference_mark": ref.reference_mark,
                            "confidence": ref.confidence
                        }
                        for ref in references
                    ]
                }
                
                validation_results.append(validation_result)
                
            except Exception as e:
                logger.error(f"Error validating drawing {drawing_id}: {e}")
                continue
        
        return {
            "validation_results": validation_results,
            "total_drawings": len(validation_results),
            "total_references": sum(r["reference_count"] for r in validation_results)
        }
        
    except Exception as e:
        logger.error(f"Error validating measurements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{project_id}/batch")
async def batch_enhanced_analysis_project(project_id: int, analysis_request: dict, db: Session = Depends(get_db)):
    """Perform batch enhanced analysis with specific drawing IDs and options"""
    try:
        drawing_ids = analysis_request.get("drawing_ids", [])
        enable_cross_references = analysis_request.get("enable_cross_references", True)
        enable_notes_analysis = analysis_request.get("enable_notes_analysis", True)
        
        if not drawing_ids:
            raise HTTPException(status_code=400, detail="No drawing IDs provided")
        
        # Get specific drawings
        drawings = db.query(Drawing).filter(
            Drawing.id.in_(drawing_ids),
            Drawing.project_id == project_id
        ).all()
        
        if not drawings:
            raise HTTPException(status_code=404, detail="No drawings found")
        
        # Initialize processor
        processor = PDFProcessor()
        
        # Process each drawing with enhanced analysis
        results = []
        cross_references_count = 0
        notes_analyzed_count = 0
        
        for drawing in drawings:
            try:
                drawing_path = f"uploads/{project_id}/{drawing.filename}"
                if os.path.exists(drawing_path):
                    result = processor.process_drawing_with_cross_references(
                        drawing.id, drawing_path, drawing.discipline or "architectural"
                    )
                    
                    if result['status'] == 'success':
                        results.append(result)
                        
                        # Count cross-references and notes
                        if 'cross_references' in result:
                            cross_references_count += len(result['cross_references'])
                        if 'notes_report' in result:
                            notes_analyzed_count += 1
                    else:
                        results.append({
                            "drawing_id": drawing.id,
                            "error": result.get('message', 'Unknown error'),
                            "status": "failed"
                        })
                        
            except Exception as e:
                logger.error(f"Error processing drawing {drawing.id}: {e}")
                results.append({
                    "drawing_id": drawing.id,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "project_id": project_id,
            "total_drawings": len(drawings),
            "processed_drawings": len(results),
            "cross_references_count": cross_references_count,
            "notes_analyzed_count": notes_analyzed_count,
            "enable_cross_references": enable_cross_references,
            "enable_notes_analysis": enable_notes_analysis,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch enhanced project analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 