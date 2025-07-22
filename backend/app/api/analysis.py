from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.models import Project
from ..services.cost_calculator import CostCalculator

router = APIRouter()
cost_calculator = CostCalculator()


@router.get("/project/{project_id}/costs")
async def calculate_project_costs(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Calculate total costs for a project"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        summary = cost_calculator.calculate_project_costs(db, project_id)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating project costs: {str(e)}"
        )


@router.get("/costs")
async def get_all_project_costs(db: Session = Depends(get_db)):
    """Get total costs across all projects"""
    try:
        # Get all projects
        projects = db.query(Project).all()
        
        total_cost = 0
        total_elements = 0
        total_area = 0
        
        # Calculate costs for each project
        for project in projects:
            try:
                summary = cost_calculator.calculate_project_costs(db, project.id)
                total_cost += summary.total_cost
                total_elements += summary.total_elements
                total_area += summary.total_area
            except Exception as e:
                print(f"Error calculating costs for project {project.id}: {e}")
                continue
        
        return {
            "total_cost": total_cost,
            "total_elements": total_elements,
            "total_area": total_area,
            "project_count": len(projects)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating total costs: {str(e)}"
        )


@router.get("/materials/suggestions/{element_type}")
async def get_material_suggestions(element_type: str):
    """Get material suggestions for an element type"""
    try:
        suggestions = cost_calculator.get_material_suggestions(element_type)
        return {"element_type": element_type, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving material suggestions: {str(e)}"
        ) 