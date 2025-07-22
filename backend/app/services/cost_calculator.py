import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models.models import Element, Material, CostDatabase
from ..models.schemas import CostCalculationResult, ProjectSummary

logger = logging.getLogger(__name__)


class CostCalculator:
    """Service for calculating construction costs based on detected elements"""
    
    def __init__(self):
        # Default cost factors for MVP
        self.default_labor_rates = {
            'wall': 25.0,  # $/m2
            'floor': 30.0,  # $/m2
            'door': 150.0,  # $/unit
            'window': 200.0,  # $/unit
            'column': 500.0,  # $/unit
            'roof': 45.0,  # $/m2
        }
        
        self.default_overhead_rate = 0.15  # 15% overhead
        self.default_equipment_rate = 0.10  # 10% equipment cost
    
    def calculate_element_cost(self, element: Element, material: Optional[Material] = None) -> CostCalculationResult:
        """
        Calculate cost for a single element
        
        Args:
            element: Element object
            material: Associated material (optional)
            
        Returns:
            CostCalculationResult with detailed cost breakdown
        """
        try:
            # Material cost
            material_cost = 0.0
            if material:
                material_cost = element.quantity * material.unit_cost
            else:
                # Use default material costs for MVP
                default_material_costs = {
                    'wall': 50.0,  # $/m2
                    'floor': 80.0,  # $/m2
                    'door': 300.0,  # $/unit
                    'window': 400.0,  # $/unit
                    'column': 800.0,  # $/unit
                    'roof': 120.0,  # $/m2
                }
                material_cost = element.quantity * default_material_costs.get(element.element_type, 100.0)
            
            # Labor cost
            labor_rate = self.default_labor_rates.get(element.element_type, 30.0)
            labor_cost = element.quantity * labor_rate
            
            # Equipment cost
            equipment_cost = material_cost * self.default_equipment_rate
            
            # Overhead cost
            overhead_cost = (material_cost + labor_cost + equipment_cost) * self.default_overhead_rate
            
            # Total cost
            total_cost = material_cost + labor_cost + equipment_cost + overhead_cost
            
            # Carbon footprint (if material has carbon factor)
            carbon_footprint = None
            if material and material.carbon_factor:
                carbon_footprint = element.quantity * material.carbon_factor
            
            return CostCalculationResult(
                element_id=element.id,
                material_cost=material_cost,
                labor_cost=labor_cost,
                equipment_cost=equipment_cost,
                overhead_cost=overhead_cost,
                total_cost=total_cost,
                carbon_footprint=carbon_footprint
            )
            
        except Exception as e:
            logger.error(f"Error calculating cost for element {element.id}: {str(e)}")
            raise
    
    def calculate_project_costs(self, db: Session, project_id: int) -> ProjectSummary:
        """
        Calculate total costs for an entire project
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            ProjectSummary with total costs and breakdowns
        """
        try:
            # Get all elements for the project
            elements = db.query(Element).filter(Element.project_id == project_id).all()
            
            if not elements:
                return ProjectSummary(
                    project_id=project_id,
                    total_elements=0,
                    total_area=0.0,
                    total_volume=0.0,
                    total_cost=0.0,
                    total_carbon=None,
                    cost_breakdown={},
                    element_breakdown={}
                )
            
            # Calculate costs for each element
            total_cost = 0.0
            total_carbon = 0.0
            total_area = 0.0
            total_volume = 0.0
            cost_breakdown = {}
            element_breakdown = {}
            
            for element in elements:
                # Get associated material
                material = None
                if element.material_id:
                    material = db.query(Material).filter(Material.id == element.material_id).first()
                
                # Calculate element cost
                cost_result = self.calculate_element_cost(element, material)
                total_cost += cost_result.total_cost
                
                # Accumulate areas and volumes
                if element.area:
                    total_area += element.area
                if element.volume:
                    total_volume += element.volume
                
                # Carbon footprint
                if cost_result.carbon_footprint:
                    total_carbon += cost_result.carbon_footprint
                
                # Cost breakdown by element type
                element_type = element.element_type
                if element_type not in cost_breakdown:
                    cost_breakdown[element_type] = 0.0
                cost_breakdown[element_type] += cost_result.total_cost
                
                # Element count breakdown
                if element_type not in element_breakdown:
                    element_breakdown[element_type] = 0
                element_breakdown[element_type] += 1
            
            return ProjectSummary(
                project_id=project_id,
                total_elements=len(elements),
                total_area=total_area,
                total_volume=total_volume,
                total_cost=total_cost,
                total_carbon=total_carbon if total_carbon > 0 else None,
                cost_breakdown=cost_breakdown,
                element_breakdown=element_breakdown
            )
            
        except Exception as e:
            logger.error(f"Error calculating project costs for project {project_id}: {str(e)}")
            raise
    
    def get_material_suggestions(self, element_type: str) -> List[Dict]:
        """
        Get material suggestions for an element type
        
        Args:
            element_type: Type of construction element
            
        Returns:
            List of suggested materials with costs
        """
        # Material suggestions for MVP
        material_suggestions = {
            'wall': [
                {'name': 'Concrete Block', 'unit_cost': 45.0, 'unit': 'm2'},
                {'name': 'Brick', 'unit_cost': 60.0, 'unit': 'm2'},
                {'name': 'Timber Frame', 'unit_cost': 35.0, 'unit': 'm2'},
                {'name': 'Steel Frame', 'unit_cost': 80.0, 'unit': 'm2'},
            ],
            'floor': [
                {'name': 'Concrete Slab', 'unit_cost': 70.0, 'unit': 'm2'},
                {'name': 'Timber Joists', 'unit_cost': 55.0, 'unit': 'm2'},
                {'name': 'Steel Deck', 'unit_cost': 90.0, 'unit': 'm2'},
            ],
            'door': [
                {'name': 'Timber Door', 'unit_cost': 250.0, 'unit': 'unit'},
                {'name': 'Steel Door', 'unit_cost': 400.0, 'unit': 'unit'},
                {'name': 'Aluminum Door', 'unit_cost': 350.0, 'unit': 'unit'},
            ],
            'window': [
                {'name': 'Aluminum Window', 'unit_cost': 300.0, 'unit': 'unit'},
                {'name': 'Timber Window', 'unit_cost': 250.0, 'unit': 'unit'},
                {'name': 'PVC Window', 'unit_cost': 200.0, 'unit': 'unit'},
            ],
            'column': [
                {'name': 'Concrete Column', 'unit_cost': 600.0, 'unit': 'unit'},
                {'name': 'Steel Column', 'unit_cost': 800.0, 'unit': 'unit'},
                {'name': 'Timber Column', 'unit_cost': 400.0, 'unit': 'unit'},
            ],
            'roof': [
                {'name': 'Concrete Roof', 'unit_cost': 100.0, 'unit': 'm2'},
                {'name': 'Timber Truss', 'unit_cost': 80.0, 'unit': 'm2'},
                {'name': 'Steel Truss', 'unit_cost': 120.0, 'unit': 'm2'},
            ]
        }
        
        return material_suggestions.get(element_type, [])
    
    def calculate_carbon_footprint(self, element: Element, material: Optional[Material] = None) -> float:
        """
        Calculate carbon footprint for an element
        
        Args:
            element: Element object
            material: Associated material (optional)
            
        Returns:
            Carbon footprint in kg CO2
        """
        try:
            if material and material.carbon_factor:
                return element.quantity * material.carbon_factor
            
            # Default carbon factors for MVP
            default_carbon_factors = {
                'wall': 50.0,  # kg CO2/m2
                'floor': 80.0,  # kg CO2/m2
                'door': 100.0,  # kg CO2/unit
                'window': 150.0,  # kg CO2/unit
                'column': 200.0,  # kg CO2/unit
                'roof': 120.0,  # kg CO2/m2
            }
            
            factor = default_carbon_factors.get(element.element_type, 50.0)
            return element.quantity * factor
            
        except Exception as e:
            logger.error(f"Error calculating carbon footprint for element {element.id}: {str(e)}")
            return 0.0
    
    def generate_cost_report(self, project_summary: ProjectSummary) -> Dict:
        """
        Generate a detailed cost report
        
        Args:
            project_summary: Project cost summary
            
        Returns:
            Detailed cost report dictionary
        """
        try:
            report = {
                'project_id': project_summary.project_id,
                'summary': {
                    'total_cost': project_summary.total_cost,
                    'total_area': project_summary.total_area,
                    'total_volume': project_summary.total_volume,
                    'total_elements': project_summary.total_elements,
                    'cost_per_m2': project_summary.total_cost / project_summary.total_area if project_summary.total_area > 0 else 0,
                    'carbon_footprint': project_summary.total_carbon,
                },
                'cost_breakdown': project_summary.cost_breakdown,
                'element_breakdown': project_summary.element_breakdown,
                'recommendations': self._generate_recommendations(project_summary)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating cost report: {str(e)}")
            raise
    
    def _generate_recommendations(self, project_summary: ProjectSummary) -> List[str]:
        """
        Generate cost optimization recommendations
        
        Args:
            project_summary: Project cost summary
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Analyze cost breakdown and provide recommendations
        if project_summary.cost_breakdown:
            highest_cost_element = max(project_summary.cost_breakdown.items(), key=lambda x: x[1])
            
            if highest_cost_element[0] == 'wall' and highest_cost_element[1] > project_summary.total_cost * 0.4:
                recommendations.append("Consider alternative wall materials to reduce costs")
            
            if highest_cost_element[0] == 'floor' and highest_cost_element[1] > project_summary.total_cost * 0.3:
                recommendations.append("Floor system costs are high - review structural options")
        
        # General recommendations
        if project_summary.total_cost > 1000000:  # $1M threshold
            recommendations.append("Consider value engineering to optimize costs")
        
        if not recommendations:
            recommendations.append("Cost structure appears reasonable for project scope")
        
        return recommendations 