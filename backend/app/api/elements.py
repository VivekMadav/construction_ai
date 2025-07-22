from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.models import Element, Project
from ..models.schemas import ElementCreate, Element as ElementSchema

router = APIRouter()


@router.get("/project/{project_id}", response_model=List[ElementSchema])
async def get_project_elements(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get all elements for a project"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        elements = db.query(Element).filter(Element.project_id == project_id).all()
        return elements
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving elements: {str(e)}"
        )


@router.get("/{element_id}", response_model=ElementSchema)
async def get_element(
    element_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific element by ID"""
    try:
        element = db.query(Element).filter(Element.id == element_id).first()
        if not element:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Element not found"
            )
        return element
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving element: {str(e)}"
        )


@router.delete("/{element_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_element(
    element_id: int,
    db: Session = Depends(get_db)
):
    """Delete an element"""
    try:
        element = db.query(Element).filter(Element.id == element_id).first()
        if not element:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Element not found"
            )
        
        db.delete(element)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting element: {str(e)}"
        ) 