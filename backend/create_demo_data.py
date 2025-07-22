#!/usr/bin/env python3
"""
Demo data creation script for Construction AI Platform
Creates sample projects and materials for demonstration purposes
"""

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.models import Project, Material, Element, Drawing
from datetime import datetime

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def create_demo_materials():
    """Create sample construction materials"""
    materials = [
        Material(
            name="Concrete Block",
            category="masonry",
            unit_cost=45.0,
            unit="m2",
            carbon_factor=50.0,
            density=1900.0,
            description="Standard concrete block for walls"
        ),
        Material(
            name="Brick",
            category="masonry", 
            unit_cost=60.0,
            unit="m2",
            carbon_factor=80.0,
            density=1800.0,
            description="Traditional clay brick"
        ),
        Material(
            name="Timber Frame",
            category="structural",
            unit_cost=35.0,
            unit="m2",
            carbon_factor=30.0,
            density=500.0,
            description="Wooden frame construction"
        ),
        Material(
            name="Steel Frame",
            category="structural",
            unit_cost=80.0,
            unit="m2", 
            carbon_factor=120.0,
            density=7850.0,
            description="Steel structural frame"
        ),
        Material(
            name="Concrete Slab",
            category="flooring",
            unit_cost=70.0,
            unit="m2",
            carbon_factor=80.0,
            density=2400.0,
            description="Reinforced concrete floor slab"
        ),
        Material(
            name="Timber Door",
            category="doors",
            unit_cost=250.0,
            unit="unit",
            carbon_factor=100.0,
            density=600.0,
            description="Solid timber door"
        ),
        Material(
            name="Aluminum Window",
            category="windows",
            unit_cost=300.0,
            unit="unit",
            carbon_factor=150.0,
            density=2700.0,
            description="Double-glazed aluminum window"
        ),
        Material(
            name="Concrete Column",
            category="structural",
            unit_cost=600.0,
            unit="unit",
            carbon_factor=200.0,
            density=2400.0,
            description="Reinforced concrete column"
        )
    ]
    
    for material in materials:
        db.add(material)
    
    db.commit()
    print(f"✅ Created {len(materials)} demo materials")

def create_demo_projects():
    """Create sample construction projects"""
    projects = [
        Project(
            name="Office Building - London",
            description="3-story commercial office building with modern amenities",
            client_name="TechCorp Ltd",
            project_type="commercial",
            location="London, UK",
            total_area=2500.0,
            status="active"
        ),
        Project(
            name="Residential Complex - Manchester",
            description="50-unit residential development with parking",
            client_name="Urban Living Developments",
            project_type="residential",
            location="Manchester, UK",
            total_area=8000.0,
            status="active"
        ),
        Project(
            name="Industrial Warehouse - Birmingham",
            description="Large industrial warehouse with office space",
            client_name="Logistics Solutions Ltd",
            project_type="industrial",
            location="Birmingham, UK",
            total_area=15000.0,
            status="completed"
        )
    ]
    
    for project in projects:
        db.add(project)
    
    db.commit()
    print(f"✅ Created {len(projects)} demo projects")
    return projects

def create_demo_elements(projects):
    """Create sample building elements for projects"""
    elements = []
    
    # Office Building elements
    office_project = projects[0]
    office_elements = [
        Element(
            project_id=office_project.id,
            element_type="wall",
            quantity=450.0,
            unit="m2",
            area=450.0,
            confidence_score=0.85
        ),
        Element(
            project_id=office_project.id,
            element_type="floor",
            quantity=2500.0,
            unit="m2",
            area=2500.0,
            confidence_score=0.92
        ),
        Element(
            project_id=office_project.id,
            element_type="door",
            quantity=24.0,
            unit="unit",
            confidence_score=0.78
        ),
        Element(
            project_id=office_project.id,
            element_type="window",
            quantity=36.0,
            unit="unit",
            confidence_score=0.81
        ),
        Element(
            project_id=office_project.id,
            element_type="column",
            quantity=12.0,
            unit="unit",
            confidence_score=0.89
        )
    ]
    elements.extend(office_elements)
    
    # Residential Complex elements
    residential_project = projects[1]
    residential_elements = [
        Element(
            project_id=residential_project.id,
            element_type="wall",
            quantity=1200.0,
            unit="m2",
            area=1200.0,
            confidence_score=0.87
        ),
        Element(
            project_id=residential_project.id,
            element_type="floor",
            quantity=8000.0,
            unit="m2",
            area=8000.0,
            confidence_score=0.94
        ),
        Element(
            project_id=residential_project.id,
            element_type="door",
            quantity=150.0,
            unit="unit",
            confidence_score=0.82
        ),
        Element(
            project_id=residential_project.id,
            element_type="window",
            quantity=200.0,
            unit="unit",
            confidence_score=0.79
        )
    ]
    elements.extend(residential_elements)
    
    # Industrial Warehouse elements
    warehouse_project = projects[2]
    warehouse_elements = [
        Element(
            project_id=warehouse_project.id,
            element_type="wall",
            quantity=3000.0,
            unit="m2",
            area=3000.0,
            confidence_score=0.91
        ),
        Element(
            project_id=warehouse_project.id,
            element_type="floor",
            quantity=15000.0,
            unit="m2",
            area=15000.0,
            confidence_score=0.96
        ),
        Element(
            project_id=warehouse_project.id,
            element_type="column",
            quantity=48.0,
            unit="unit",
            confidence_score=0.88
        )
    ]
    elements.extend(warehouse_elements)
    
    for element in elements:
        db.add(element)
    
    db.commit()
    print(f"✅ Created {len(elements)} demo elements")

def main():
    """Main function to create all demo data"""
    print("🚀 Creating demo data for Construction AI Platform...")
    
    try:
        # Create materials first
        create_demo_materials()
        
        # Create projects
        projects = create_demo_projects()
        
        # Create elements for projects
        create_demo_elements(projects)
        
        print("\n🎉 Demo data created successfully!")
        print("\n📊 Summary:")
        print("- 8 construction materials")
        print("- 3 sample projects")
        print("- 12 building elements")
        print("\n🌐 Access your platform:")
        print("- Frontend: http://localhost:3000")
        print("- API Docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 