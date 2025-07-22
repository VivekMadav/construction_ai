from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.models import Project, Report
from ..models.schemas import ReportCreate, Report as ReportSchema
from ..services.cost_calculator import CostCalculator

router = APIRouter()
cost_calculator = CostCalculator()


@router.post("/project/{project_id}/generate", response_model=ReportSchema)
async def generate_cost_report(
    project_id: int,
    report_type: str = "cost_summary",
    db: Session = Depends(get_db)
):
    """Generate a cost report for a project"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Calculate project costs
        summary = cost_calculator.calculate_project_costs(db, project_id)
        
        # Generate detailed report
        detailed_report = cost_calculator.generate_cost_report(summary)
        
        # Create report record
        report = Report(
            project_id=project_id,
            report_type=report_type,
            total_cost=summary.total_cost,
            total_carbon=summary.total_carbon,
            summary_data=str(detailed_report)
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=list[ReportSchema])
async def get_project_reports(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get all reports for a project"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        reports = db.query(Report).filter(Report.project_id == project_id).all()
        return reports
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving reports: {str(e)}"
        ) 