from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from ..core.database import get_db
from ..core.config import settings
from ..models.models import Drawing, Project, Element
from ..models.schemas import Drawing as DrawingSchema, DrawingWithElements, FileUploadResponse
from ..services.pdf_processor import PDFProcessor

router = APIRouter()
pdf_processor = PDFProcessor()


@router.post("/upload/{project_id}", response_model=FileUploadResponse)
async def upload_drawing(
    project_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Upload a construction drawing (PDF) for processing"""
    try:
        # Validate project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.allowed_file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_file_types}"
            )
        
        # Validate file size
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size {file.size} exceeds maximum allowed size {settings.max_file_size}"
            )
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.upload_dir, str(project_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create drawing record
        drawing = Drawing(
            project_id=project_id,
            filename=filename,
            file_path=file_path,
            file_size=file.size,
            file_type=file_extension,
            processing_status="pending"
        )
        
        db.add(drawing)
        db.commit()
        db.refresh(drawing)
        
        # Start background processing for PDF files
        if file_extension == '.pdf' and background_tasks:
            background_tasks.add_task(process_pdf_drawing, drawing.id, file_path, db)
        
        return FileUploadResponse(
            filename=filename,
            file_id=drawing.id,
            status="uploaded",
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


async def process_pdf_drawing(drawing_id: int, file_path: str, db: Session):
    """Background task to process PDF drawing"""
    # Create a new database session for the background task
    from ..core.database import SessionLocal
    db_session = SessionLocal()
    
    try:
        # Update status to processing
        drawing = db_session.query(Drawing).filter(Drawing.id == drawing_id).first()
        if drawing:
            drawing.processing_status = "processing"
            db_session.commit()
        
        # Process the PDF
        results = pdf_processor.process_pdf_drawing(file_path)
        
        # Save detected elements to database
        if results['status'] == 'completed' and results['total_elements'] > 0:
            for page in results['pages']:
                for element_data in page['elements']:
                    # Calculate bounding box as JSON string
                    bbox = element_data['bounding_box']
                    bounding_box_json = f'{{"x1": {bbox[0]}, "y1": {bbox[1]}, "x2": {bbox[2]}, "y2": {bbox[3]}}}'
                    
                    # Calculate area in square meters (assuming 100 pixels per meter)
                    area_m2 = element_data['area'] / (100 * 100)  # Convert from pixels to m2
                    
                    element = Element(
                        drawing_id=drawing_id,
                        project_id=drawing.project_id,
                        element_type=element_data['type'],
                        quantity=area_m2,
                        unit="m2",
                        area=area_m2,
                        confidence_score=element_data['confidence'],
                        bounding_box=bounding_box_json
                    )
                    db_session.add(element)
            
            drawing.processing_status = "completed"
        else:
            drawing.processing_status = "failed"
        
        db_session.commit()
        
    except Exception as e:
        # Update status to failed
        drawing = db_session.query(Drawing).filter(Drawing.id == drawing_id).first()
        if drawing:
            drawing.processing_status = "failed"
            db_session.commit()
    finally:
        db_session.close()


@router.get("/", response_model=List[DrawingWithElements])
async def get_all_drawings(db: Session = Depends(get_db)):
    """Get all drawings across all projects"""
    try:
        drawings = db.query(Drawing).all()
        return drawings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving drawings: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=List[DrawingWithElements])
async def get_project_drawings(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get all drawings for a project with their elements"""
    try:
        # Validate project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get drawings with their elements
        drawings = db.query(Drawing).filter(Drawing.project_id == project_id).all()
        return drawings
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving drawings: {str(e)}"
        )


@router.get("/{drawing_id}", response_model=DrawingSchema)
async def get_drawing(
    drawing_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific drawing by ID"""
    try:
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drawing not found"
            )
        return drawing
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving drawing: {str(e)}"
        )


@router.delete("/{drawing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drawing(
    drawing_id: int,
    db: Session = Depends(get_db)
):
    """Delete a drawing and its file"""
    try:
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drawing not found"
            )
        
        # Delete file from filesystem
        if os.path.exists(drawing.file_path):
            os.remove(drawing.file_path)
        
        # Delete from database
        db.delete(drawing)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting drawing: {str(e)}"
        )


@router.post("/{drawing_id}/reprocess")
async def reprocess_drawing(
    drawing_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reprocess a drawing"""
    try:
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drawing not found"
            )
        
        if not os.path.exists(drawing.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drawing file not found"
            )
        
        # Start background reprocessing
        background_tasks.add_task(process_pdf_drawing, drawing.id, drawing.file_path, db)
        
        return {
            "message": "Drawing reprocessing started",
            "drawing_id": drawing_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reprocessing drawing: {str(e)}"
        ) 