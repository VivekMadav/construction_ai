"""
Enhanced Cost Estimation System for Construction AI

This module integrates cost estimation with the enhanced inference system
to provide intelligent cost analysis based on detected elements and text.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

# Import our modules
from cost_estimation import CostEstimator, CostDatabase, ProjectCostSummary, ElementCost
from models.enhanced_inference import EnhancedInferenceSystem, Discipline

logger = logging.getLogger(__name__)

@dataclass
class EnhancedCostAnalysis:
    """Enhanced cost analysis with detailed breakdowns."""
    project_summary: ProjectCostSummary
    discipline_breakdown: Dict[str, Dict[str, Any]]
    material_analysis: Dict[str, Any]
    specification_impact: Dict[str, Any]
    cost_trends: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class EnhancedCostEstimator:
    """Enhanced cost estimator that integrates with enhanced inference system."""
    
    def __init__(self, enhanced_system: Optional[EnhancedInferenceSystem] = None):
        self.enhanced_system = enhanced_system or EnhancedInferenceSystem()
        self.cost_estimator = CostEstimator()
        
    def analyze_drawing_costs(self, 
                             image: np.ndarray, 
                             discipline: Discipline,
                             project_scale: str = "medium") -> EnhancedCostAnalysis:
        """
        Analyze costs for a drawing with enhanced detection.
        
        Args:
            image: Input image
            discipline: Discipline for analysis
            project_scale: Project scale (small, medium, large)
            
        Returns:
            Enhanced cost analysis results
        """
        try:
            # Step 1: Enhanced element detection
            logger.info(f"Performing enhanced detection for {discipline.value}")
            detection_results = self.enhanced_system.detect_elements_enhanced(
                image, discipline, use_ocr=True
            )
            
            elements = detection_results.get('elements', [])
            extracted_texts = detection_results.get('extracted_texts', [])
            
            # Step 2: Cost estimation
            logger.info(f"Estimating costs for {len(elements)} elements")
            project_summary = self.cost_estimator.estimate_project_costs(elements)
            
            # Step 3: Enhanced analysis
            discipline_breakdown = self._analyze_discipline_costs(elements, project_summary)
            material_analysis = self._analyze_material_distribution(elements, project_summary)
            specification_impact = self._analyze_specification_impact(elements, project_summary)
            cost_trends = self._analyze_cost_trends(elements, project_summary)
            recommendations = self._generate_recommendations(elements, project_summary, project_scale)
            confidence_score = self._calculate_confidence_score(elements, extracted_texts)
            
            return EnhancedCostAnalysis(
                project_summary=project_summary,
                discipline_breakdown=discipline_breakdown,
                material_analysis=material_analysis,
                specification_impact=specification_impact,
                cost_trends=cost_trends,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error in enhanced cost analysis: {e}")
            return self._create_error_analysis(str(e))
    
    def analyze_multi_discipline_costs(self, 
                                      image: np.ndarray,
                                      project_scale: str = "medium") -> Dict[str, EnhancedCostAnalysis]:
        """
        Analyze costs for all disciplines.
        
        Args:
            image: Input image
            project_scale: Project scale
            
        Returns:
            Dictionary of cost analyses by discipline
        """
        results = {}
        
        for discipline in Discipline:
            logger.info(f"Analyzing costs for {discipline.value}")
            analysis = self.analyze_drawing_costs(image, discipline, project_scale)
            results[discipline.value] = analysis
        
        return results
    
    def _analyze_discipline_costs(self, 
                                 elements: List[Dict[str, Any]], 
                                 summary: ProjectCostSummary) -> Dict[str, Any]:
        """Analyze costs by discipline categories."""
        discipline_costs = {
            "structural": {"count": 0, "cost": 0.0, "elements": []},
            "architectural": {"count": 0, "cost": 0.0, "elements": []},
            "mep": {"count": 0, "cost": 0.0, "elements": []},
            "civil": {"count": 0, "cost": 0.0, "elements": []}
        }
        
        # Categorize elements by discipline
        for element_cost in summary.element_costs:
            element_type = element_cost.element_type
            
            # Map element types to disciplines
            if element_type in ['wall', 'column', 'beam', 'slab', 'foundation']:
                discipline = "structural"
            elif element_type in ['door', 'window', 'room', 'furniture']:
                discipline = "architectural"
            elif element_type in ['hvac_duct', 'electrical_panel', 'plumbing_pipe']:
                discipline = "mep"
            elif element_type in ['road', 'utility', 'drainage']:
                discipline = "civil"
            else:
                discipline = "architectural"  # Default
            
            discipline_costs[discipline]["count"] += 1
            discipline_costs[discipline]["cost"] += element_cost.total_cost
            discipline_costs[discipline]["elements"].append({
                "type": element_type,
                "cost": element_cost.total_cost,
                "material": element_cost.breakdown.get('material', 'unknown')
            })
        
        return discipline_costs
    
    def _analyze_material_distribution(self, 
                                      elements: List[Dict[str, Any]], 
                                      summary: ProjectCostSummary) -> Dict[str, Any]:
        """Analyze material distribution and costs."""
        material_stats = {}
        
        for element_cost in summary.element_costs:
            material = element_cost.breakdown.get('material', 'unknown')
            
            if material not in material_stats:
                material_stats[material] = {
                    "count": 0,
                    "total_cost": 0.0,
                    "avg_cost": 0.0,
                    "elements": []
                }
            
            material_stats[material]["count"] += 1
            material_stats[material]["total_cost"] += element_cost.total_cost
            material_stats[material]["elements"].append({
                "type": element_cost.element_type,
                "cost": element_cost.total_cost,
                "quantity": element_cost.quantity
            })
        
        # Calculate averages
        for material, stats in material_stats.items():
            if stats["count"] > 0:
                stats["avg_cost"] = stats["total_cost"] / stats["count"]
        
        return material_stats
    
    def _analyze_specification_impact(self, 
                                     elements: List[Dict[str, Any]], 
                                     summary: ProjectCostSummary) -> Dict[str, Any]:
        """Analyze the impact of specifications on costs."""
        spec_impact = {
            "total_specifications": 0,
            "specification_breakdown": {},
            "cost_impact": 0.0,
            "most_expensive_specs": []
        }
        
        for element_cost in summary.element_costs:
            specs = element_cost.breakdown.get('specifications', [])
            spec_impact["total_specifications"] += len(specs)
            
            for spec in specs:
                if spec not in spec_impact["specification_breakdown"]:
                    spec_impact["specification_breakdown"][spec] = {
                        "count": 0,
                        "total_cost": 0.0,
                        "elements": []
                    }
                
                spec_impact["specification_breakdown"][spec]["count"] += 1
                spec_impact["specification_breakdown"][spec]["total_cost"] += element_cost.total_cost
                spec_impact["specification_breakdown"][spec]["elements"].append({
                    "type": element_cost.element_type,
                    "cost": element_cost.total_cost
                })
        
        # Calculate cost impact (difference between base and adjusted rates)
        for element_cost in summary.element_costs:
            base_rate = element_cost.breakdown.get('base_rate', 0)
            adjusted_rate = element_cost.breakdown.get('adjusted_rate', 0)
            if base_rate > 0:
                impact = (adjusted_rate - base_rate) * element_cost.quantity
                spec_impact["cost_impact"] += impact
        
        # Get most expensive specifications
        spec_costs = [(spec, data["total_cost"]) for spec, data in spec_impact["specification_breakdown"].items()]
        spec_costs.sort(key=lambda x: x[1], reverse=True)
        spec_impact["most_expensive_specs"] = spec_costs[:5]
        
        return spec_impact
    
    def _analyze_cost_trends(self, 
                            elements: List[Dict[str, Any]], 
                            summary: ProjectCostSummary) -> Dict[str, Any]:
        """Analyze cost trends and patterns."""
        trends = {
            "cost_distribution": {
                "low_cost": 0,      # < $100
                "medium_cost": 0,   # $100 - $500
                "high_cost": 0,     # $500 - $1000
                "very_high_cost": 0 # > $1000
            },
            "element_cost_ranking": [],
            "cost_efficiency": {
                "most_efficient": [],
                "least_efficient": []
            }
        }
        
        # Analyze cost distribution
        for element_cost in summary.element_costs:
            cost = element_cost.total_cost
            if cost < 100:
                trends["cost_distribution"]["low_cost"] += 1
            elif cost < 500:
                trends["cost_distribution"]["medium_cost"] += 1
            elif cost < 1000:
                trends["cost_distribution"]["high_cost"] += 1
            else:
                trends["cost_distribution"]["very_high_cost"] += 1
        
        # Element cost ranking
        element_costs = [(cost.element_type, cost.total_cost) for cost in summary.element_costs]
        element_costs.sort(key=lambda x: x[1], reverse=True)
        trends["element_cost_ranking"] = element_costs[:10]
        
        # Cost efficiency (cost per unit area/length)
        efficiency_data = []
        for element_cost in summary.element_costs:
            if element_cost.quantity > 0:
                efficiency = element_cost.total_cost / element_cost.quantity
                efficiency_data.append({
                    "element_type": element_cost.element_type,
                    "efficiency": efficiency,
                    "cost": element_cost.total_cost,
                    "quantity": element_cost.quantity
                })
        
        efficiency_data.sort(key=lambda x: x["efficiency"])
        trends["cost_efficiency"]["most_efficient"] = efficiency_data[:5]
        trends["cost_efficiency"]["least_efficient"] = efficiency_data[-5:]
        
        return trends
    
    def _generate_recommendations(self, 
                                 elements: List[Dict[str, Any]], 
                                 summary: ProjectCostSummary,
                                 project_scale: str) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Analyze high-cost elements
        high_cost_elements = [cost for cost in summary.element_costs if cost.total_cost > 500]
        if len(high_cost_elements) > len(summary.element_costs) * 0.3:
            recommendations.append("Consider reviewing high-cost elements (>$500) for potential alternatives")
        
        # Analyze specifications
        spec_impact = self._analyze_specification_impact(elements, summary)
        if spec_impact["cost_impact"] > summary.total_cost * 0.2:
            recommendations.append("Specifications are adding significant cost - review necessity")
        
        # Material recommendations
        material_analysis = self._analyze_material_distribution(elements, summary)
        expensive_materials = ['steel', 'aluminium']
        for material in expensive_materials:
            if material in material_analysis and material_analysis[material]["total_cost"] > summary.total_cost * 0.4:
                recommendations.append(f"High use of {material} - consider cost-effective alternatives")
        
        # Project scale recommendations
        if project_scale == "small" and summary.total_cost > 50000:
            recommendations.append("Cost seems high for small project - review scope and specifications")
        elif project_scale == "large" and summary.total_cost < 100000:
            recommendations.append("Cost seems low for large project - ensure all elements are captured")
        
        # Efficiency recommendations
        trends = self._analyze_cost_trends(elements, summary)
        if trends["cost_distribution"]["very_high_cost"] > 5:
            recommendations.append("Multiple very high-cost elements detected - consider value engineering")
        
        return recommendations
    
    def _calculate_confidence_score(self, 
                                   elements: List[Dict[str, Any]], 
                                   extracted_texts: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for cost estimation."""
        if not elements:
            return 0.0
        
        # Base confidence from element detection
        base_confidence = 0.7
        
        # Boost confidence based on text extraction
        if extracted_texts:
            text_confidence_boost = min(0.2, len(extracted_texts) / len(elements) * 0.1)
            base_confidence += text_confidence_boost
        
        # Boost confidence based on enhanced properties
        enhanced_elements = [elem for elem in elements if elem.get('enhanced_properties')]
        if enhanced_elements:
            enhancement_boost = len(enhanced_elements) / len(elements) * 0.1
            base_confidence += enhancement_boost
        
        # Reduce confidence for elements without cost rates
        cost_estimator = CostEstimator()
        elements_with_costs = 0
        for element in elements:
            cost = cost_estimator.estimate_element_cost(element)
            if cost:
                elements_with_costs += 1
        
        if elements:
            cost_coverage = elements_with_costs / len(elements)
            base_confidence *= cost_coverage
        
        return min(1.0, max(0.0, base_confidence))
    
    def _create_error_analysis(self, error_message: str) -> EnhancedCostAnalysis:
        """Create error analysis when processing fails."""
        return EnhancedCostAnalysis(
            project_summary=ProjectCostSummary(
                total_cost=0.0,
                currency="USD",
                element_count=0,
                cost_breakdown={},
                element_costs=[],
                assumptions={"error": error_message}
            ),
            discipline_breakdown={},
            material_analysis={},
            specification_impact={},
            cost_trends={},
            recommendations=["Error in cost analysis - check input data"],
            confidence_score=0.0
        )
    
    def generate_comprehensive_report(self, 
                                     analysis: EnhancedCostAnalysis,
                                     project_name: str = "Unknown Project") -> Dict[str, Any]:
        """Generate a comprehensive cost report."""
        report = {
            "project_info": {
                "name": project_name,
                "analysis_timestamp": analysis.analysis_timestamp,
                "confidence_score": analysis.confidence_score
            },
            "cost_summary": {
                "total_cost": analysis.project_summary.total_cost,
                "currency": analysis.project_summary.currency,
                "element_count": analysis.project_summary.element_count,
                "average_cost_per_element": analysis.project_summary.total_cost / analysis.project_summary.element_count if analysis.project_summary.element_count > 0 else 0
            },
            "discipline_breakdown": analysis.discipline_breakdown,
            "material_analysis": analysis.material_analysis,
            "specification_impact": analysis.specification_impact,
            "cost_trends": analysis.cost_trends,
            "recommendations": analysis.recommendations,
            "detailed_costs": [
                {
                    "element_id": cost.element_id,
                    "element_type": cost.element_type,
                    "total_cost": cost.total_cost,
                    "quantity": cost.quantity,
                    "unit": cost.unit,
                    "material": cost.breakdown.get('material', 'unknown'),
                    "specifications": cost.breakdown.get('specifications', [])
                }
                for cost in analysis.project_summary.element_costs
            ]
        }
        
        return report
    
    def save_analysis_report(self, 
                            analysis: EnhancedCostAnalysis, 
                            output_path: str,
                            project_name: str = "Unknown Project"):
        """Save analysis report to JSON file."""
        try:
            report = self.generate_comprehensive_report(analysis, project_name)
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Cost analysis report saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving cost analysis report: {e}")

def main():
    """Example usage of the enhanced cost estimation system."""
    # Initialize enhanced cost estimator
    enhanced_cost_estimator = EnhancedCostEstimator()
    
    print("Enhanced Cost Estimation System")
    print("=" * 50)
    
    # Example: Analyze costs for a sample image
    # image = cv2.imread("sample_drawing.jpg")
    # analysis = enhanced_cost_estimator.analyze_drawing_costs(
    #     image, Discipline.ARCHITECTURAL, "medium"
    # )
    # 
    # report = enhanced_cost_estimator.generate_comprehensive_report(analysis, "Sample Project")
    # print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main() 