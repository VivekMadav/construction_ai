#!/usr/bin/env python3
"""
Create a sample PDF drawing for testing the Construction AI Platform
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import black, blue, red, green
import os

def create_sample_drawing():
    """Create a sample construction drawing PDF"""
    
    # Create uploads directory if it doesn't exist
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Create PDF
    filename = os.path.join(uploads_dir, "sample_floor_plan.pdf")
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-3*cm, "Sample Floor Plan - Office Building")
    
    # Scale
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height-4*cm, "Scale: 1:100")
    c.drawString(2*cm, height-4.5*cm, "Drawing: Ground Floor Plan")
    
    # Draw walls (rectangles)
    c.setStrokeColor(black)
    c.setLineWidth(2)
    
    # Outer walls
    c.rect(4*cm, 6*cm, 12*cm, 8*cm)
    
    # Internal walls
    c.line(8*cm, 6*cm, 8*cm, 14*cm)  # Vertical wall
    c.line(4*cm, 10*cm, 16*cm, 10*cm)  # Horizontal wall
    
    # Doors (small rectangles)
    c.setFillColor(blue)
    c.rect(7.5*cm, 5.8*cm, 1*cm, 0.4*cm)  # Door 1
    c.rect(11.5*cm, 5.8*cm, 1*cm, 0.4*cm)  # Door 2
    c.rect(7.5*cm, 9.8*cm, 1*cm, 0.4*cm)  # Door 3
    
    # Windows (larger rectangles)
    c.setFillColor(green)
    c.rect(5*cm, 13.8*cm, 2*cm, 0.4*cm)  # Window 1
    c.rect(9*cm, 13.8*cm, 2*cm, 0.4*cm)  # Window 2
    c.rect(13*cm, 13.8*cm, 2*cm, 0.4*cm)  # Window 3
    
    # Columns (circles)
    c.setFillColor(red)
    c.circle(6*cm, 7*cm, 0.3*cm, fill=1)
    c.circle(14*cm, 7*cm, 0.3*cm, fill=1)
    c.circle(6*cm, 13*cm, 0.3*cm, fill=1)
    c.circle(14*cm, 13*cm, 0.3*cm, fill=1)
    
    # Labels
    c.setFont("Helvetica", 8)
    c.setFillColor(black)
    c.drawString(5*cm, 5*cm, "Room 1")
    c.drawString(9*cm, 5*cm, "Room 2")
    c.drawString(5*cm, 9*cm, "Room 3")
    c.drawString(9*cm, 9*cm, "Room 4")
    
    # Dimensions
    c.drawString(4*cm, 4*cm, "12.0m")
    c.drawString(2*cm, 10*cm, "8.0m")
    
    # Legend
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, 2*cm, "Legend:")
    c.setFont("Helvetica", 8)
    c.drawString(2*cm, 1.5*cm, "Blue: Doors | Green: Windows | Red: Columns | Black: Walls")
    
    c.save()
    print(f"✅ Sample PDF created: {filename}")
    print(f"📁 File location: {os.path.abspath(filename)}")
    return filename

if __name__ == "__main__":
    create_sample_drawing() 