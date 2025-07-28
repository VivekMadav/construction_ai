from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
from datetime import datetime


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
    discipline = Column(String(50), default="architectural")  # architectural, structural, civil, mep
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="drawings")
    elements = relationship("Element", back_populates="drawing")
    steel_elements = relationship("SteelElement", back_populates="drawing")
    concrete_elements = relationship("ConcreteElement", back_populates="drawing")


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


class SteelSection(Base):
    """Steel section database for structural steel detection"""
    __tablename__ = "steel_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    section_name = Column(String, index=True, nullable=False)  # e.g., "W310x52"
    section_type = Column(String, nullable=False)  # e.g., "W", "H", "I", "C", "L"
    depth_mm = Column(Float)  # Depth in mm
    width_mm = Column(Float)  # Width in mm
    thickness_mm = Column(Float)  # Thickness in mm
    kg_per_meter = Column(Float, nullable=False)  # Mass per meter in kg
    area_mm2 = Column(Float)  # Cross-sectional area in mm²
    inertia_mm4 = Column(Float)  # Moment of inertia in mm⁴
    description = Column(String)  # Additional description
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SteelElement(Base):
    """Detected steel elements with mass calculations"""
    __tablename__ = "steel_elements"
    
    id = Column(Integer, primary_key=True, index=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)
    element_type = Column(String, nullable=False)  # e.g., "beam", "column", "truss"
    section_name = Column(String, nullable=False)  # e.g., "W310x52"
    section_type = Column(String, nullable=False)  # e.g., "W", "H", "I"
    length_mm = Column(Float)  # Length in mm
    mass_kg = Column(Float)  # Calculated mass in kg
    confidence_score = Column(Float, default=0.0)
    bbox = Column(String)  # JSON string of bounding box
    text_references = Column(String)  # JSON string of associated text
    properties = Column(String)  # JSON string of additional properties
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    drawing = relationship("Drawing", back_populates="steel_elements")


class ConcreteElement(Base):
    """Detected concrete elements with volume measurements"""
    __tablename__ = "concrete_elements"
    
    id = Column(Integer, primary_key=True, index=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)
    element_type = Column(String, nullable=False)  # foundation, slab, wall, column, beam, etc.
    concrete_grade = Column(String, nullable=False, default="C25")  # C25, C30, C40, etc.
    length_m = Column(Float, nullable=False)  # Length in meters
    width_m = Column(Float, nullable=False)   # Width in meters
    depth_m = Column(Float, nullable=False)   # Depth/thickness in meters
    volume_m3 = Column(Float, nullable=False) # Volume in cubic meters
    confidence_score = Column(Float, default=0.0)
    location = Column(String)  # Optional location description
    description = Column(Text)  # Additional description
    text_references = Column(String)  # JSON string of associated text
    bbox = Column(String)  # JSON string of bounding box
    properties = Column(String)  # JSON string of additional properties
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    drawing = relationship("Drawing", back_populates="concrete_elements") 