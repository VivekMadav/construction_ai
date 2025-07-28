#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.models import SteelSection

def add_hollow_sections():
    """Add all hollow sections from Barrett Steel brochure to database"""
    db = SessionLocal()
    
    try:
        # CHS (Circular Hollow Sections) - BS EN 10219-1: 2006
        chs_sections = [
            # Size (mm), Kg/m
            ("21.3 x 3.0", 1.35),
            ("26.9 x 2.0", 1.23),
            ("26.9 x 2.5", 1.50),
            ("26.9 x 3.0", 1.77),
            ("33.7 x 2.0", 1.56),
            ("33.7 x 2.5", 1.92),
            ("33.7 x 3.0", 2.27),
            ("33.7 x 4.0", 2.93),
            ("42.4 x 2.0", 1.99),
            ("42.4 x 2.5", 2.46),
            ("42.4 x 3.0", 2.91),
            ("42.4 x 3.2", 3.09),
            ("42.4 x 4.0", 3.79),
            ("48.3 x 2.5", 2.82),
            ("48.3 x 3.0", 3.35),
            ("48.3 x 3.2", 3.59),
            ("48.3 x 4.0", 4.37),
            ("48.3 x 5.0", 5.34),
            ("60.3 x 3.0", 4.24),
            ("60.3 x 3.5", 4.90),
            ("60.3 x 4.0", 5.55),
            ("60.3 x 5.0", 6.82),
            ("76.1 x 3.0", 5.40),
            ("76.1 x 3.5", 6.26),
            ("76.1 x 4.0", 7.11),
            ("76.1 x 5.0", 8.76),
            ("88.9 x 3.0", 6.36),
            ("88.9 x 3.5", 7.38),
            ("88.9 x 4.0", 8.38),
            ("88.9 x 5.0", 10.34),
            ("114.3 x 3.0", 8.25),
            ("114.3 x 3.5", 9.57),
            ("114.3 x 4.0", 10.88),
            ("114.3 x 5.0", 13.44),
            ("139.7 x 3.0", 10.11),
            ("139.7 x 3.5", 11.73),
            ("139.7 x 4.0", 13.34),
            ("139.7 x 5.0", 16.48),
            ("168.3 x 3.0", 12.22),
            ("168.3 x 3.5", 14.18),
            ("168.3 x 4.0", 16.13),
            ("168.3 x 5.0", 19.93),
            ("219.1 x 3.0", 15.96),
            ("219.1 x 3.5", 18.51),
            ("219.1 x 4.0", 21.05),
            ("219.1 x 5.0", 26.00),
            ("273.0 x 3.0", 19.93),
            ("273.0 x 3.5", 23.12),
            ("273.0 x 4.0", 26.30),
            ("273.0 x 5.0", 32.50),
            ("323.9 x 3.0", 23.67),
            ("323.9 x 3.5", 27.45),
            ("323.9 x 4.0", 31.22),
            ("323.9 x 5.0", 38.58),
            ("355.6 x 3.0", 26.04),
            ("355.6 x 3.5", 30.20),
            ("355.6 x 4.0", 34.35),
            ("355.6 x 5.0", 42.42),
            ("406.4 x 3.0", 29.82),
            ("406.4 x 3.5", 34.58),
            ("406.4 x 4.0", 39.33),
            ("406.4 x 5.0", 48.58),
            ("457.0 x 3.0", 33.52),
            ("457.0 x 3.5", 38.88),
            ("457.0 x 4.0", 44.23),
            ("457.0 x 5.0", 54.62),
            ("508.0 x 3.0", 37.34),
            ("508.0 x 3.5", 43.30),
            ("508.0 x 4.0", 49.25),
            ("508.0 x 5.0", 60.82),
        ]
        
        # RHS (Rectangular Hollow Sections) - BS EN 10210-1: 2006
        rhs_sections = [
            # Size (mm), Kg/m
            ("50 x 30 x 3.2", 3.61),
            ("50 x 30 x 4.0", 4.39),
            ("50 x 30 x 5.0", 5.28),
            ("60 x 40 x 3.2", 4.62),
            ("60 x 40 x 4.0", 5.64),
            ("60 x 40 x 5.0", 6.85),
            ("80 x 40 x 3.2", 5.62),
            ("80 x 40 x 4.0", 6.90),
            ("80 x 40 x 5.0", 8.42),
            ("80 x 40 x 6.3", 10.30),
            ("90 x 50 x 3.6", 7.40),
            ("90 x 50 x 5.0", 9.99),
            ("90 x 50 x 6.3", 12.30),
            ("100 x 50 x 3.2", 7.13),
            ("100 x 50 x 4.0", 8.78),
            ("100 x 50 x 5.0", 10.80),
            ("100 x 50 x 6.3", 13.30),
            ("100 x 50 x 8.0", 16.30),
            ("100 x 60 x 3.6", 8.53),
            ("100 x 60 x 5.0", 11.60),
            ("100 x 60 x 6.3", 14.20),
            ("100 x 60 x 8.0", 17.50),
            ("120 x 60 x 3.6", 9.66),
            ("120 x 60 x 5.0", 13.10),
            ("120 x 60 x 6.3", 16.20),
            ("120 x 60 x 8.0", 20.10),
            ("120 x 80 x 5.0", 14.70),
            ("120 x 80 x 6.3", 18.20),
            ("120 x 80 x 8.0", 22.60),
            ("120 x 80 x 10.0", 27.40),
            ("150 x 100 x 4.0", 15.10),
            ("150 x 100 x 5.0", 18.60),
            ("150 x 100 x 6.0", 21.70),
            ("150 x 100 x 6.3", 23.10),
            ("150 x 100 x 8.0", 28.90),
            ("150 x 100 x 10.0", 35.30),
            ("150 x 100 x 12.5", 42.80),
            ("160 x 80 x 4.0", 14.40),
            ("160 x 80 x 5.0", 17.80),
            ("160 x 80 x 6.3", 22.20),
            ("160 x 80 x 8.0", 27.60),
            ("160 x 80 x 10.0", 33.70),
            ("160 x 80 x 12.5", 40.90),
            ("200 x 100 x 5.0", 22.60),
            ("200 x 100 x 6.3", 28.10),
            ("200 x 100 x 8.0", 35.10),
            ("200 x 100 x 10.0", 43.10),
            ("200 x 100 x 12.5", 52.70),
            ("200 x 100 x 16.0", 65.20),
            ("200 x 120 x 5.0", 24.10),
            ("200 x 120 x 6.3", 30.10),
            ("200 x 120 x 8.0", 37.60),
            ("200 x 120 x 10.0", 46.30),
            ("200 x 120 x 12.5", 56.60),
            ("200 x 150 x 8.0", 41.40),
            ("200 x 150 x 10.0", 51.00),
            ("250 x 100 x 6.3", 33.00),
            ("250 x 150 x 5.0", 30.40),
            ("250 x 150 x 6.3", 38.00),
            ("250 x 150 x 8.0", 47.70),
            ("250 x 150 x 10.0", 58.80),
            ("250 x 150 x 12.5", 72.30),
            ("250 x 150 x 16.0", 90.30),
            ("300 x 100 x 8.0", 47.70),
            ("300 x 100 x 10.0", 58.80),
            ("300 x 200 x 6.3", 47.90),
            ("300 x 200 x 8.0", 60.30),
            ("300 x 200 x 10.0", 74.50),
            ("300 x 200 x 12.5", 91.90),
            ("300 x 200 x 16.0", 115.00),
            ("400 x 200 x 8.0", 72.80),
            ("400 x 200 x 10.0", 90.20),
            ("400 x 200 x 12.5", 112.00),
            ("400 x 200 x 16.0", 141.00),
            ("450 x 250 x 8.0", 85.40),
            ("450 x 250 x 10.0", 106.00),
            ("450 x 250 x 12.5", 131.00),
            ("450 x 250 x 16.0", 166.00),
            ("500 x 300 x 10.0", 122.00),
            ("500 x 300 x 12.5", 151.00),
            ("500 x 300 x 16.0", 191.00),
        ]
        
        # SHS (Square Hollow Sections) - BS EN 10210-1: 2006
        shs_sections = [
            # Size (mm), Kg/m
            ("20 x 20 x 2.0", 1.12),
            ("25 x 25 x 2.0", 1.43),
            ("25 x 25 x 2.5", 1.75),
            ("30 x 30 x 2.0", 1.73),
            ("30 x 30 x 2.5", 2.12),
            ("30 x 30 x 3.0", 2.49),
            ("40 x 40 x 2.0", 2.33),
            ("40 x 40 x 2.5", 2.86),
            ("40 x 40 x 3.0", 3.37),
            ("50 x 50 x 2.0", 2.93),
            ("50 x 50 x 2.5", 3.60),
            ("50 x 50 x 3.0", 4.25),
            ("50 x 50 x 4.0", 5.48),
            ("60 x 60 x 2.0", 3.53),
            ("60 x 60 x 2.5", 4.34),
            ("60 x 60 x 3.0", 5.13),
            ("60 x 60 x 4.0", 6.62),
            ("70 x 70 x 2.5", 5.08),
            ("70 x 70 x 3.0", 6.01),
            ("70 x 70 x 4.0", 7.76),
            ("80 x 80 x 2.5", 5.82),
            ("80 x 80 x 3.0", 6.89),
            ("80 x 80 x 4.0", 8.90),
            ("90 x 90 x 2.5", 6.56),
            ("90 x 90 x 3.0", 7.77),
            ("90 x 90 x 4.0", 10.04),
            ("100 x 100 x 2.5", 7.30),
            ("100 x 100 x 3.0", 8.65),
            ("100 x 100 x 4.0", 11.18),
            ("120 x 120 x 3.0", 10.41),
            ("120 x 120 x 4.0", 13.46),
            ("120 x 120 x 5.0", 16.40),
            ("140 x 140 x 3.0", 12.17),
            ("140 x 140 x 4.0", 15.74),
            ("140 x 140 x 5.0", 19.20),
            ("150 x 150 x 3.0", 13.05),
            ("150 x 150 x 4.0", 16.88),
            ("150 x 150 x 5.0", 20.60),
            ("160 x 160 x 3.0", 13.93),
            ("160 x 160 x 4.0", 18.02),
            ("160 x 160 x 5.0", 22.00),
            ("180 x 180 x 3.0", 15.69),
            ("180 x 180 x 4.0", 20.30),
            ("180 x 180 x 5.0", 24.80),
            ("200 x 200 x 3.0", 17.45),
            ("200 x 200 x 4.0", 22.58),
            ("200 x 200 x 5.0", 27.60),
            ("220 x 220 x 3.0", 19.21),
            ("220 x 220 x 4.0", 24.86),
            ("220 x 220 x 5.0", 30.40),
            ("250 x 250 x 3.0", 21.85),
            ("250 x 250 x 4.0", 28.26),
            ("250 x 250 x 5.0", 34.56),
            ("300 x 300 x 3.0", 26.25),
            ("300 x 300 x 4.0", 33.96),
            ("300 x 300 x 5.0", 41.56),
            ("350 x 350 x 3.0", 30.65),
            ("350 x 350 x 4.0", 39.66),
            ("350 x 350 x 5.0", 48.56),
            ("400 x 400 x 3.0", 35.05),
            ("400 x 400 x 4.0", 45.36),
            ("400 x 400 x 5.0", 55.56),
        ]
        
        # Add CHS sections
        print("Adding CHS (Circular Hollow Sections)...")
        for size, mass_per_meter in chs_sections:
            # Parse size for CHS (e.g., "21.3 x 3.0" -> diameter=21.3, thickness=3.0)
            parts = size.split(" x ")
            diameter = float(parts[0])
            thickness = float(parts[1])
            
            section = SteelSection(
                section_name=f"CHS {size}",
                section_type="CHS",
                depth_mm=diameter,
                width_mm=diameter,
                thickness_mm=thickness,
                kg_per_meter=mass_per_meter,
                description=f"Circular Hollow Section - BS EN 10219-1: 2006"
            )
            db.add(section)
        
        # Add RHS sections
        print("Adding RHS (Rectangular Hollow Sections)...")
        for size, mass_per_meter in rhs_sections:
            # Parse size for RHS (e.g., "50 x 30 x 3.2" -> width=50, height=30, thickness=3.2)
            parts = size.split(" x ")
            width = float(parts[0])
            height = float(parts[1])
            thickness = float(parts[2])
            
            section = SteelSection(
                section_name=f"RHS {size}",
                section_type="RHS",
                depth_mm=height,
                width_mm=width,
                thickness_mm=thickness,
                kg_per_meter=mass_per_meter,
                description=f"Rectangular Hollow Section - BS EN 10210-1: 2006"
            )
            db.add(section)
        
        # Add SHS sections
        print("Adding SHS (Square Hollow Sections)...")
        for size, mass_per_meter in shs_sections:
            # Parse size for SHS (e.g., "20 x 20 x 2.0" -> width=20, height=20, thickness=2.0)
            parts = size.split(" x ")
            width = float(parts[0])
            height = float(parts[1])
            thickness = float(parts[2])
            
            section = SteelSection(
                section_name=f"SHS {size}",
                section_type="SHS",
                depth_mm=height,
                width_mm=width,
                thickness_mm=thickness,
                kg_per_meter=mass_per_meter,
                description=f"Square Hollow Section - BS EN 10210-1: 2006"
            )
            db.add(section)
        
        db.commit()
        print(f"Successfully added {len(chs_sections)} CHS, {len(rhs_sections)} RHS, and {len(shs_sections)} SHS sections to database")
        
    except Exception as e:
        print(f"Error adding hollow sections: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_hollow_sections() 