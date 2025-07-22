from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Project(Base):
    """Project model for storing construction project information"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    client_name = Column(String(255))
    project_type = Column(String(100))  # residential, commercial, etc.
    location = Column(String(255))
    total_area = Column(Float)  # in square meters
    total_cost = Column(Float)
    carbon_footprint = Column(Float)  # in kg CO2
    status = Column(String(50), default="draft")  # draft, processing, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    drawings = relationship("Drawing", back_populates="project")
    elements = relationship("Element", back_populates="project")
    reports = relationship("Report", back_populates="project")


class Drawing(Base):
    """Drawing model for storing uploaded construction drawings"""
    __tablename__ = "drawings"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(10))  # pdf, png, etc.
    page_count = Column(Integer, default=1)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="drawings")
    elements = relationship("Element", back_populates="drawing")


class Element(Base):
    """Building element model for storing detected construction elements"""
    __tablename__ = "elements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    drawing_id = Column(Integer, ForeignKey("drawings.id"))
    element_type = Column(String(100), nullable=False)  # wall, floor, door, window, etc.
    material_id = Column(Integer, ForeignKey("materials.id"))
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # m2, m3, units, etc.
    area = Column(Float)  # in square meters
    volume = Column(Float)  # in cubic meters
    confidence_score = Column(Float)  # ML model confidence
    bounding_box = Column(Text)  # JSON string of coordinates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="elements")
    drawing = relationship("Drawing", back_populates="elements")
    material = relationship("Material", back_populates="elements")


class Material(Base):
    """Material model for storing construction materials and their properties"""
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100))  # concrete, steel, timber, etc.
    unit_cost = Column(Float, nullable=False)  # cost per unit
    unit = Column(String(20), nullable=False)  # m2, m3, kg, etc.
    carbon_factor = Column(Float)  # kg CO2 per unit
    density = Column(Float)  # kg/m3
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    elements = relationship("Element", back_populates="material")


class Report(Base):
    """Report model for storing generated quantity survey reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    report_type = Column(String(50), nullable=False)  # boq, cost_summary, carbon_analysis
    filename = Column(String(255))
    file_path = Column(String(500))
    total_cost = Column(Float)
    total_carbon = Column(Float)
    summary_data = Column(Text)  # JSON string of summary statistics
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="reports")


class CostDatabase(Base):
    """Cost database model for storing regional cost data"""
    __tablename__ = "cost_database"
    
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String(100), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"))
    labor_cost = Column(Float)  # labor cost per unit
    equipment_cost = Column(Float)  # equipment cost per unit
    overhead_percentage = Column(Float)  # overhead as percentage
    year = Column(Integer, nullable=False)
    source = Column(String(255))  # data source
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    material = relationship("Material") 