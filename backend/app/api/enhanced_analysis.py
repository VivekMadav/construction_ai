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
        
        drawings = _get_drawings_for_analysis(project_id, drawing_ids, db)
        processor = _initialize_processor()
        processing_results = _process_drawings_batch(drawings, project_id, processor)
        
        return _create_batch_response(
            project_id, drawings, processing_results, 
            enable_cross_references, enable_notes_analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch enhanced project analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

def _get_drawings_for_analysis(project_id: int, drawing_ids: List[int], db: Session) -> List[Drawing]:
    """Get drawings for batch analysis with validation."""
    drawings = db.query(Drawing).filter(
        Drawing.id.in_(drawing_ids),
        Drawing.project_id == project_id
    ).all()
    
    if not drawings:
        raise HTTPException(status_code=404, detail="No drawings found")
    
    return drawings

def _initialize_processor() -> PDFProcessor:
    """Initialize PDF processor with error handling."""
    try:
        return PDFProcessor()
    except Exception as e:
        logger.error(f"Failed to initialize PDF processor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize processor: {str(e)}")

def _process_drawings_batch(drawings: List[Drawing], project_id: int, processor: PDFProcessor) -> List[Dict]:
    """Process all drawings in batch with progress tracking."""
    processing_results = []
    successful_count = 0
    failed_count = 0
    
    for drawing_index, drawing in enumerate(drawings):
        logger.info(f"Processing drawing {drawing.id} ({drawing_index + 1}/{len(drawings)})")
        
        result = _process_single_drawing(drawing, project_id, processor)
        processing_results.append(result)
        
        if result["status"] == "success":
            successful_count += 1
        else:
            failed_count += 1
    
    logger.info(f"Batch processing completed: {successful_count}/{len(drawings)} successful")
    return processing_results

def _process_single_drawing(drawing: Drawing, project_id: int, processor: PDFProcessor) -> Dict:
    """Process a single drawing with comprehensive error handling."""
    drawing_path = f"uploads/{project_id}/{drawing.filename}"
    
    # Check if file exists
    if not os.path.exists(drawing_path):
        logger.warning(f"Drawing file not found: {drawing_path}")
        return _create_failed_result(drawing, "File not found")
    
    # Process drawing with error handling
    try:
        result = processor.process_drawing_with_cross_references(
            drawing.id, drawing_path, drawing.discipline or "architectural"
        )
        
        if result.get('status') == 'success':
            logger.info(f"Successfully processed drawing {drawing.id}")
            return result
        else:
            error_message = result.get('message', 'Unknown error')
            logger.error(f"Failed to process drawing {drawing.id}: {error_message}")
            return _create_failed_result(drawing, error_message)
            
    except Exception as e:
        logger.error(f"Exception processing drawing {drawing.id}: {e}")
        return _create_failed_result(drawing, str(e))

def _create_failed_result(drawing: Drawing, error_message: str) -> Dict:
    """Create a standardized failed result dictionary."""
    return {
        "drawing_id": drawing.id,
        "filename": drawing.filename,
        "error": error_message,
        "status": "failed"
    }

def _create_batch_response(project_id: int, drawings: List[Drawing], 
                         processing_results: List[Dict], enable_cross_references: bool, 
                         enable_notes_analysis: bool) -> Dict:
    """Create the final batch response with statistics."""
    total_drawings = len(drawings)
    successful_results = [r for r in processing_results if r.get('status') == 'success']
    failed_results = [r for r in processing_results if r.get('status') == 'failed']
    
    # Calculate statistics
    successful_count = len(successful_results)
    failed_count = len(failed_results)
    success_rate = (successful_count / total_drawings * 100) if total_drawings > 0 else 0
    
    # Count cross-references and notes
    cross_references_count = sum(
        len(r.get('cross_references', [])) for r in successful_results
    )
    notes_analyzed_count = sum(
        1 for r in successful_results if 'notes_report' in r
    )
    
    return {
        "project_id": project_id,
        "total_drawings": total_drawings,
        "processed_drawings": len(processing_results),
        "successful_processing": successful_count,
        "failed_processing": failed_count,
        "success_rate": success_rate,
        "cross_references_count": cross_references_count,
        "notes_analyzed_count": notes_analyzed_count,
        "enable_cross_references": enable_cross_references,
        "enable_notes_analysis": enable_notes_analysis,
        "processing_summary": {
            "total": total_drawings,
            "successful": successful_count,
            "failed": failed_count,
            "success_rate_percentage": success_rate
        },
        "results": processing_results
    } 