from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = None
    project_type: Optional[str] = None
    location: Optional[str] = None
    total_area: Optional[float] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = None
    project_type: Optional[str] = None
    location: Optional[str] = None
    total_area: Optional[float] = None
    status: Optional[str] = None


class Project(ProjectBase):
    id: int
    total_cost: Optional[float] = None
    carbon_footprint: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Drawing schemas
class DrawingBase(BaseModel):
    filename: str
    file_type: str


class DrawingCreate(DrawingBase):
    project_id: int
    discipline: Optional[str] = "architectural"  # architectural, structural, civil, mep


class Drawing(DrawingBase):
    id: int
    project_id: int
    file_path: str
    file_size: Optional[int] = None
    page_count: int = 1
    discipline: str = "architectural"
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DrawingWithElements(Drawing):
    elements: Optional[List['Element']] = None


# Element schemas
class ElementBase(BaseModel):
    element_type: str
    quantity: float
    unit: str
    area: Optional[float] = None
    volume: Optional[float] = None
    confidence_score: Optional[float] = None
    bounding_box: Optional[str] = None


class ElementCreate(ElementBase):
    project_id: int
    drawing_id: int
    material_id: Optional[int] = None


class Element(ElementBase):
    id: int
    project_id: int
    drawing_id: int
    material_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Material schemas
class MaterialBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = None
    unit_cost: float = Field(..., gt=0)
    unit: str
    carbon_factor: Optional[float] = None
    density: Optional[float] = None
    description: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = None
    unit_cost: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None
    carbon_factor: Optional[float] = None
    density: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Material(MaterialBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Report schemas
class ReportBase(BaseModel):
    report_type: str
    total_cost: Optional[float] = None
    total_carbon: Optional[float] = None
    summary_data: Optional[str] = None


class ReportCreate(ReportBase):
    project_id: int


class Report(ReportBase):
    id: int
    project_id: int
    filename: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Cost Database schemas
class CostDatabaseBase(BaseModel):
    region: str
    material_id: int
    labor_cost: Optional[float] = None
    equipment_cost: Optional[float] = None
    overhead_percentage: Optional[float] = None
    year: int
    source: Optional[str] = None


class CostDatabaseCreate(CostDatabaseBase):
    pass


class CostDatabase(CostDatabaseBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analysis schemas
class ElementDetectionResult(BaseModel):
    element_type: str
    confidence: float
    bounding_box: List[float]
    area: Optional[float] = None
    volume: Optional[float] = None
    suggested_material: Optional[str] = None


class DrawingAnalysisResult(BaseModel):
    drawing_id: int
    elements_detected: List[ElementDetectionResult]
    processing_time: float
    status: str


class CostCalculationResult(BaseModel):
    element_id: int
    material_cost: float
    labor_cost: float
    equipment_cost: float
    overhead_cost: float
    total_cost: float
    carbon_footprint: Optional[float] = None


class ProjectSummary(BaseModel):
    project_id: int
    total_elements: int
    total_area: float
    total_volume: float
    total_cost: float
    total_carbon: Optional[float] = None
    cost_breakdown: dict
    element_breakdown: dict


# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_id: int
    status: str
    message: str


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None 