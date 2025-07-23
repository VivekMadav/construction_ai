"""
Cost Estimation System for Construction AI

This module provides intelligent cost estimation based on detected construction
elements, materials, specifications, and dimensions from drawings.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class CostUnit(Enum):
    """Units for cost calculations."""
    PER_SQM = "per_sqm"           # Per square meter
    PER_LM = "per_lm"             # Per linear meter
    PER_UNIT = "per_unit"         # Per individual unit
    PER_CUBIC_M = "per_cubic_m"   # Per cubic meter
    PER_KG = "per_kg"             # Per kilogram
    PER_TON = "per_ton"           # Per ton

class MaterialType(Enum):
    """Types of construction materials."""
    CONCRETE = "concrete"
    STEEL = "steel"
    TIMBER = "timber"
    BRICK = "brick"
    GLASS = "glass"
    ALUMINIUM = "aluminium"
    PLASTIC = "plastic"
    CERAMIC = "ceramic"
    INSULATION = "insulation"
    FINISHES = "finishes"

class ElementCategory(Enum):
    """Categories of construction elements."""
    STRUCTURAL = "structural"
    ARCHITECTURAL = "architectural"
    MEP = "mep"
    CIVIL = "civil"
    FINISHES = "finishes"

@dataclass
class CostRate:
    """Represents a cost rate for a specific element type."""
    element_type: str
    material: str
    unit: CostUnit
    base_rate: float
    currency: str = "USD"
    region: str = "global"
    date_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    specifications: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ElementCost:
    """Represents the cost calculation for a single element."""
    element_id: str
    element_type: str
    quantity: float
    unit: str
    unit_cost: float
    total_cost: float
    currency: str
    breakdown: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProjectCostSummary:
    """Summary of project costs."""
    total_cost: float
    currency: str
    element_count: int
    cost_breakdown: Dict[str, float]
    element_costs: List[ElementCost]
    assumptions: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class CostDatabase:
    """Database of cost rates for construction elements."""
    
    def __init__(self, rates_file: Optional[str] = None):
        self.rates_file = rates_file or "ml/data/cost_rates.json"
        self.rates: Dict[str, CostRate] = {}
        self.load_default_rates()
        
        if os.path.exists(self.rates_file):
            self.load_rates_from_file()
    
    def load_default_rates(self):
        """Load default cost rates for common construction elements."""
        default_rates = {
            # Structural Elements
            "wall": {
                "concrete": CostRate("wall", "concrete", CostUnit.PER_SQM, 85.0),
                "brick": CostRate("wall", "brick", CostUnit.PER_SQM, 65.0),
                "steel": CostRate("wall", "steel", CostUnit.PER_SQM, 120.0),
            },
            "column": {
                "concrete": CostRate("column", "concrete", CostUnit.PER_UNIT, 450.0),
                "steel": CostRate("column", "steel", CostUnit.PER_UNIT, 800.0),
            },
            "beam": {
                "concrete": CostRate("beam", "concrete", CostUnit.PER_LM, 180.0),
                "steel": CostRate("beam", "steel", CostUnit.PER_LM, 320.0),
            },
            "slab": {
                "concrete": CostRate("slab", "concrete", CostUnit.PER_SQM, 95.0),
            },
            "foundation": {
                "concrete": CostRate("foundation", "concrete", CostUnit.PER_CUBIC_M, 280.0),
            },
            
            # Architectural Elements
            "door": {
                "timber": CostRate("door", "timber", CostUnit.PER_UNIT, 350.0),
                "aluminium": CostRate("door", "aluminium", CostUnit.PER_UNIT, 450.0),
                "steel": CostRate("door", "steel", CostUnit.PER_UNIT, 600.0),
            },
            "window": {
                "aluminium": CostRate("window", "aluminium", CostUnit.PER_UNIT, 280.0),
                "timber": CostRate("window", "timber", CostUnit.PER_UNIT, 320.0),
                "steel": CostRate("window", "steel", CostUnit.PER_UNIT, 380.0),
            },
            "room": {
                "finishes": CostRate("room", "finishes", CostUnit.PER_SQM, 45.0),
            },
            
            # MEP Elements
            "hvac_duct": {
                "steel": CostRate("hvac_duct", "steel", CostUnit.PER_LM, 85.0),
                "aluminium": CostRate("hvac_duct", "aluminium", CostUnit.PER_LM, 95.0),
            },
            "electrical_panel": {
                "steel": CostRate("electrical_panel", "steel", CostUnit.PER_UNIT, 1200.0),
            },
            "plumbing_pipe": {
                "plastic": CostRate("plumbing_pipe", "plastic", CostUnit.PER_LM, 25.0),
                "steel": CostRate("plumbing_pipe", "steel", CostUnit.PER_LM, 45.0),
            },
            
            # Civil Elements
            "road": {
                "asphalt": CostRate("road", "asphalt", CostUnit.PER_SQM, 75.0),
                "concrete": CostRate("road", "concrete", CostUnit.PER_SQM, 95.0),
            },
            "utility": {
                "steel": CostRate("utility", "steel", CostUnit.PER_UNIT, 350.0),
            },
        }
        
        for element_type, materials in default_rates.items():
            for material, rate in materials.items():
                key = f"{element_type}_{material}"
                self.rates[key] = rate
    
    def load_rates_from_file(self):
        """Load cost rates from JSON file."""
        try:
            with open(self.rates_file, 'r') as f:
                data = json.load(f)
            
            for key, rate_data in data.items():
                rate = CostRate(
                    element_type=rate_data['element_type'],
                    material=rate_data['material'],
                    unit=CostUnit(rate_data['unit']),
                    base_rate=rate_data['base_rate'],
                    currency=rate_data.get('currency', 'USD'),
                    region=rate_data.get('region', 'global'),
                    date_updated=rate_data.get('date_updated', datetime.now().isoformat()),
                    specifications=rate_data.get('specifications', {})
                )
                self.rates[key] = rate
                
        except Exception as e:
            logger.error(f"Error loading cost rates from file: {e}")
    
    def save_rates_to_file(self):
        """Save cost rates to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.rates_file), exist_ok=True)
            
            data = {}
            for key, rate in self.rates.items():
                data[key] = {
                    'element_type': rate.element_type,
                    'material': rate.material,
                    'unit': rate.unit.value,
                    'base_rate': rate.base_rate,
                    'currency': rate.currency,
                    'region': rate.region,
                    'date_updated': rate.date_updated,
                    'specifications': rate.specifications
                }
            
            with open(self.rates_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving cost rates to file: {e}")
    
    def get_rate(self, element_type: str, material: str = "default") -> Optional[CostRate]:
        """Get cost rate for element type and material."""
        key = f"{element_type}_{material}"
        return self.rates.get(key)
    
    def add_rate(self, element_type: str, material: str, rate: CostRate):
        """Add or update a cost rate."""
        key = f"{element_type}_{material}"
        self.rates[key] = rate
        self.save_rates_to_file()

class QuantityCalculator:
    """Calculates quantities for cost estimation."""
    
    @staticmethod
    def calculate_area(bbox: List[int]) -> float:
        """Calculate area from bounding box."""
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width * height
    
    @staticmethod
    def calculate_length(bbox: List[int]) -> float:
        """Calculate length from bounding box."""
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return max(width, height)
    
    @staticmethod
    def calculate_volume(bbox: List[int], depth: float = 0.3) -> float:
        """Calculate volume from bounding box and assumed depth."""
        area = QuantityCalculator.calculate_area(bbox)
        return area * depth
    
    @staticmethod
    def calculate_quantity(element: Dict[str, Any], unit: CostUnit) -> float:
        """Calculate quantity based on element properties and cost unit."""
        bbox = element.get('bbox', [0, 0, 0, 0])
        properties = element.get('properties', {})
        enhanced_properties = element.get('enhanced_properties', {})
        
        # Use enhanced properties if available
        if enhanced_properties:
            # Check for dimensions from text
            dimensions = enhanced_properties.get('dimensions', [])
            if dimensions:
                dim = dimensions[0]
                value = dim.get('value', 0)
                unit_text = dim.get('unit', 'MM').upper()
                
                # Convert to meters
                if unit_text == 'MM':
                    value = value / 1000
                elif unit_text == 'CM':
                    value = value / 100
                elif unit_text == 'M':
                    value = value
                
                if unit == CostUnit.PER_LM:
                    return value
                elif unit == CostUnit.PER_SQM:
                    # Assume width based on element type
                    element_type = element.get('type', '')
                    if element_type in ['wall', 'beam']:
                        return value * 0.3  # Assume 300mm width
                    else:
                        return value * value  # Assume square
        
        # Fallback to geometric calculations
        if unit == CostUnit.PER_SQM:
            return QuantityCalculator.calculate_area(bbox)
        elif unit == CostUnit.PER_LM:
            return QuantityCalculator.calculate_length(bbox)
        elif unit == CostUnit.PER_CUBIC_M:
            return QuantityCalculator.calculate_volume(bbox)
        elif unit == CostUnit.PER_UNIT:
            return 1.0
        else:
            return 1.0

class CostEstimator:
    """Main cost estimation engine."""
    
    def __init__(self, cost_db: Optional[CostDatabase] = None):
        self.cost_db = cost_db or CostDatabase()
        self.quantity_calc = QuantityCalculator()
        
    def estimate_element_cost(self, element: Dict[str, Any]) -> Optional[ElementCost]:
        """Estimate cost for a single element."""
        try:
            element_type = element.get('type', '')
            element_id = element.get('id', f"{element_type}_{hash(str(element))}")
            
            # Determine material from enhanced properties
            material = self._determine_material(element)
            
            # Get cost rate
            rate = self.cost_db.get_rate(element_type, material)
            if not rate:
                # Try default material
                rate = self.cost_db.get_rate(element_type, "default")
                if not rate:
                    logger.warning(f"No cost rate found for element type: {element_type}")
                    return None
            
            # Calculate quantity
            quantity = self.quantity_calc.calculate_quantity(element, rate.unit)
            
            # Apply adjustments based on specifications
            adjusted_rate = self._apply_specification_adjustments(rate, element)
            
            # Calculate total cost
            total_cost = quantity * adjusted_rate
            
            # Create cost breakdown
            breakdown = {
                "quantity": quantity,
                "unit": rate.unit.value,
                "base_rate": rate.base_rate,
                "adjusted_rate": adjusted_rate,
                "material": material,
                "specifications": element.get('enhanced_properties', {}).get('specifications', [])
            }
            
            return ElementCost(
                element_id=element_id,
                element_type=element_type,
                quantity=quantity,
                unit=rate.unit.value,
                unit_cost=adjusted_rate,
                total_cost=total_cost,
                currency=rate.currency,
                breakdown=breakdown
            )
            
        except Exception as e:
            logger.error(f"Error estimating cost for element: {e}")
            return None
    
    def _determine_material(self, element: Dict[str, Any]) -> str:
        """Determine material from element properties."""
        enhanced_properties = element.get('enhanced_properties', {})
        
        # Check for materials from text
        materials = enhanced_properties.get('materials', [])
        if materials:
            material = materials[0].lower()
            # Map common material names
            material_map = {
                'concrete': 'concrete',
                'steel': 'steel',
                'timber': 'timber',
                'brick': 'brick',
                'glass': 'glass',
                'aluminium': 'aluminium',
                'plastic': 'plastic',
                'ceramic': 'ceramic',
                'insulation': 'insulation',
                'finishes': 'finishes'
            }
            return material_map.get(material, 'default')
        
        # Fallback based on element type
        element_type = element.get('type', '')
        type_material_map = {
            'wall': 'concrete',
            'column': 'concrete',
            'beam': 'concrete',
            'slab': 'concrete',
            'foundation': 'concrete',
            'door': 'timber',
            'window': 'aluminium',
            'hvac_duct': 'steel',
            'electrical_panel': 'steel',
            'plumbing_pipe': 'plastic',
            'road': 'asphalt',
            'utility': 'steel'
        }
        
        return type_material_map.get(element_type, 'default')
    
    def _apply_specification_adjustments(self, rate: CostRate, element: Dict[str, Any]) -> float:
        """Apply adjustments based on specifications."""
        adjusted_rate = rate.base_rate
        enhanced_properties = element.get('enhanced_properties', {})
        specifications = enhanced_properties.get('specifications', [])
        
        # Apply specification multipliers
        spec_multipliers = {
            'fire rated': 1.25,
            'insulated': 1.15,
            'waterproof': 1.20,
            'structural': 1.10,
            'reinforced': 1.30,
            'precast': 0.90
        }
        
        for spec in specifications:
            spec_lower = spec.lower()
            for spec_key, multiplier in spec_multipliers.items():
                if spec_key in spec_lower:
                    adjusted_rate *= multiplier
                    break
        
        return adjusted_rate
    
    def estimate_project_costs(self, elements: List[Dict[str, Any]]) -> ProjectCostSummary:
        """Estimate costs for all elements in a project."""
        element_costs = []
        cost_breakdown = {}
        total_cost = 0.0
        currency = "USD"
        
        for element in elements:
            cost = self.estimate_element_cost(element)
            if cost:
                element_costs.append(cost)
                total_cost += cost.total_cost
                currency = cost.currency
                
                # Add to breakdown by element type
                element_type = cost.element_type
                if element_type not in cost_breakdown:
                    cost_breakdown[element_type] = 0.0
                cost_breakdown[element_type] += cost.total_cost
        
        # Create assumptions
        assumptions = {
            "total_elements": len(elements),
            "estimated_elements": len(element_costs),
            "estimation_method": "enhanced_detection",
            "material_assumptions": "text_derived_with_fallbacks",
            "specification_impact": "applied_multipliers"
        }
        
        return ProjectCostSummary(
            total_cost=total_cost,
            currency=currency,
            element_count=len(element_costs),
            cost_breakdown=cost_breakdown,
            element_costs=element_costs,
            assumptions=assumptions
        )
    
    def generate_cost_report(self, summary: ProjectCostSummary) -> Dict[str, Any]:
        """Generate a detailed cost report."""
        report = {
            "summary": {
                "total_cost": summary.total_cost,
                "currency": summary.currency,
                "element_count": summary.element_count,
                "average_cost_per_element": summary.total_cost / summary.element_count if summary.element_count > 0 else 0
            },
            "breakdown": {
                "by_element_type": summary.cost_breakdown,
                "by_material": self._breakdown_by_material(summary.element_costs),
                "by_specification": self._breakdown_by_specification(summary.element_costs)
            },
            "top_cost_elements": self._get_top_cost_elements(summary.element_costs, 10),
            "assumptions": summary.assumptions,
            "timestamp": summary.timestamp
        }
        
        return report
    
    def _breakdown_by_material(self, element_costs: List[ElementCost]) -> Dict[str, float]:
        """Break down costs by material."""
        material_costs = {}
        for cost in element_costs:
            material = cost.breakdown.get('material', 'unknown')
            if material not in material_costs:
                material_costs[material] = 0.0
            material_costs[material] += cost.total_cost
        return material_costs
    
    def _breakdown_by_specification(self, element_costs: List[ElementCost]) -> Dict[str, float]:
        """Break down costs by specification."""
        spec_costs = {}
        for cost in element_costs:
            specs = cost.breakdown.get('specifications', [])
            for spec in specs:
                if spec not in spec_costs:
                    spec_costs[spec] = 0.0
                spec_costs[spec] += cost.total_cost
        return spec_costs
    
    def _get_top_cost_elements(self, element_costs: List[ElementCost], top_n: int) -> List[Dict[str, Any]]:
        """Get top cost elements."""
        sorted_costs = sorted(element_costs, key=lambda x: x.total_cost, reverse=True)
        top_elements = []
        
        for cost in sorted_costs[:top_n]:
            top_elements.append({
                "element_id": cost.element_id,
                "element_type": cost.element_type,
                "total_cost": cost.total_cost,
                "quantity": cost.quantity,
                "unit": cost.unit,
                "material": cost.breakdown.get('material', 'unknown')
            })
        
        return top_elements

def main():
    """Example usage of the cost estimation system."""
    # Initialize cost estimator
    cost_db = CostDatabase()
    estimator = CostEstimator(cost_db)
    
    # Example elements (from enhanced detection)
    example_elements = [
        {
            "id": "wall_001",
            "type": "wall",
            "bbox": [100, 100, 300, 200],
            "enhanced_properties": {
                "materials": ["CONCRETE"],
                "specifications": ["FIRE RATED"],
                "dimensions": [{"value": 3000, "unit": "MM"}]
            }
        },
        {
            "id": "door_001",
            "type": "door",
            "bbox": [150, 200, 200, 250],
            "enhanced_properties": {
                "materials": ["TIMBER"],
                "specifications": ["FIRE RATED"]
            }
        }
    ]
    
    # Estimate costs
    summary = estimator.estimate_project_costs(example_elements)
    report = estimator.generate_cost_report(summary)
    
    print("Cost Estimation Report:")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main() 