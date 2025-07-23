from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os

from ..core.database import get_db
from ..models.models import Project, Drawing
from ..services.cost_calculator import CostCalculator
from ..services.pdf_processor import pdf_processor

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


@router.get("/project/{project_id}/carbon")
async def analyze_project_carbon(
    project_id: int,
    project_type: str = "commercial",
    db: Session = Depends(get_db)
):
    """Analyze carbon footprint for a project"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get all drawings for the project
        drawings = db.query(Drawing).filter(Drawing.project_id == project_id).all()
        
        if not drawings:
            return {
                "status": "success",
                "message": "No drawings found for project",
                "total_carbon_kg_co2e": 0.0,
                "carbon_intensity_kg_co2e_per_unit": 0.0,
                "sustainability_score": 0.0,
                "material_breakdown": {},
                "optimization_recommendations": ["No drawings available for carbon analysis"],
                "project_type": project_type,
                "drawing_count": 0
            }
        
        # Analyze carbon for each drawing
        total_carbon = 0.0
        total_elements = 0
        all_material_breakdown = {}
        all_recommendations = []
        drawing_analyses = []
        
        for drawing in drawings:
            try:
                # Get the full path to the drawing file
                drawing_path = drawing.file_path
                if not os.path.exists(drawing_path):
                    continue
                
                # Analyze carbon footprint for this drawing
                carbon_result = pdf_processor.analyze_carbon_footprint(
                    drawing_path, 
                    drawing.discipline, 
                    project_type
                )
                
                if carbon_result['status'] == 'success':
                    total_carbon += carbon_result.get('total_carbon_kg_co2e', 0)
                    total_elements += carbon_result.get('element_count', 0)
                    
                    # Aggregate material breakdown
                    material_breakdown = carbon_result.get('material_breakdown', {})
                    for material, carbon in material_breakdown.items():
                        if material not in all_material_breakdown:
                            all_material_breakdown[material] = 0
                        all_material_breakdown[material] += carbon
                    
                    # Collect recommendations
                    recommendations = carbon_result.get('optimization_recommendations', [])
                    all_recommendations.extend(recommendations)
                    
                    drawing_analyses.append({
                        "drawing_id": drawing.id,
                        "drawing_name": drawing.name,
                        "discipline": drawing.discipline,
                        "carbon_analysis": carbon_result
                    })
                
            except Exception as e:
                print(f"Error analyzing carbon for drawing {drawing.id}: {e}")
                continue
        
        # Calculate overall metrics
        carbon_intensity = total_carbon / total_elements if total_elements > 0 else 0
        
        # Remove duplicate recommendations
        unique_recommendations = list(set(all_recommendations))
        
        return {
            "status": "success",
            "message": f"Carbon analysis completed for project {project_id}",
            "total_carbon_kg_co2e": round(total_carbon, 2),
            "carbon_intensity_kg_co2e_per_unit": round(carbon_intensity, 3),
            "sustainability_score": round(min(100, max(0, 100 - (total_carbon / 1200) * 100)), 1),
            "material_breakdown": all_material_breakdown,
            "optimization_recommendations": unique_recommendations,
            "project_type": project_type,
            "drawing_count": len(drawings),
            "element_count": total_elements,
            "drawing_analyses": drawing_analyses
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing project carbon: {str(e)}"
        )


@router.get("/drawing/{drawing_id}/carbon")
async def analyze_drawing_carbon(
    drawing_id: int,
    project_type: str = "commercial",
    db: Session = Depends(get_db)
):
    """Analyze carbon footprint for a specific drawing"""
    try:
        drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
        if not drawing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drawing not found"
            )
        
        # Get the full path to the drawing file
        drawing_path = drawing.file_path
        if not os.path.exists(drawing_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drawing file not found"
            )
        
        # Analyze carbon footprint
        carbon_result = pdf_processor.analyze_carbon_footprint(
            drawing_path, 
            drawing.discipline, 
            project_type
        )
        
        # Add drawing metadata
        carbon_result["drawing_id"] = drawing_id
        carbon_result["drawing_name"] = drawing.name
        carbon_result["discipline"] = drawing.discipline
        carbon_result["project_id"] = drawing.project_id
        
        return carbon_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing drawing carbon: {str(e)}"
        ) 