#!/usr/bin/env python3
"""
Add demo elements to drawings in the database for testing
"""

import sqlite3
import random
from datetime import datetime

def create_demo_elements():
    """Add demo elements to existing drawings"""
    
    # Connect to database
    conn = sqlite3.connect('qs_ai.db')
    cursor = conn.cursor()
    
    # Get all drawings with their project_id
    cursor.execute("SELECT id, filename, project_id FROM drawings")
    drawings = cursor.fetchall()
    
    if not drawings:
        print("❌ No drawings found in database")
        return
    
    print(f"📋 Found {len(drawings)} drawings")
    
    # Element types for construction drawings
    element_types = [
        "wall", "door", "window", "column", "beam", "slab", "foundation",
        "roof", "stair", "elevator", "duct", "pipe", "electrical_outlet",
        "light_fixture", "fire_alarm", "sprinkler", "ceiling_tile", "floor_tile"
    ]
    
    units = ["m", "m²", "m³", "pcs", "sets", "linear_m"]
    
    for drawing_id, filename, project_id in drawings:
        print(f"🔧 Adding elements to drawing: {filename}")
        
        # Generate 5-15 random elements per drawing
        num_elements = random.randint(5, 15)
        
        for i in range(num_elements):
            element_type = random.choice(element_types)
            quantity = random.uniform(1, 100)
            unit = random.choice(units)
            confidence = random.uniform(0.6, 0.95)
            area = random.uniform(10, 500) if unit in ["m²", "m³"] else None
            
            cursor.execute("""
                INSERT INTO elements (drawing_id, project_id, element_type, quantity, unit, area, confidence_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (drawing_id, project_id, element_type, quantity, unit, area, confidence, datetime.now().isoformat()))
        
        # Update drawing status to processed
        cursor.execute("UPDATE drawings SET processing_status = 'processed' WHERE id = ?", (drawing_id,))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("✅ Demo elements added successfully!")
    print(f"📊 Added elements to {len(drawings)} drawings")

if __name__ == "__main__":
    create_demo_elements() 