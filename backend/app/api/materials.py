from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.models import Material
from ..models.schemas import MaterialCreate, MaterialUpdate, Material as MaterialSchema

router = APIRouter()


@router.get("/", response_model=List[MaterialSchema])
async def get_materials(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all materials with pagination"""
    try:
        materials = db.query(Material).filter(Material.is_active == True).offset(skip).limit(limit).all()
        return materials
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving materials: {str(e)}"
        )


@router.get("/{material_id}", response_model=MaterialSchema)
async def get_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific material by ID"""
    try:
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found"
            )
        return material
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving material: {str(e)}"
        ) 