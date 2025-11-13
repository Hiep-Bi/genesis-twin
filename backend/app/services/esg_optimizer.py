"""Real-time ESG Optimizer with Pareto optimization"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class ESGOptimizer:
    """
    🌍 Real-time ESG (Environmental, Social, Governance) Optimizer
    
    Features:
    1. Calculate holistic ESG score
    2. Dynamic balancing of Cost / Productivity / Carbon
    3. Pareto optimization for trade-off analysis
    4. Real-time recommendations
    """
    
    def __init__(self):
        self.esg_history = []
        self.thresholds = {
            "carbon_kg_per_unit": 2.0,  # Max 2kg CO2 per product
            "energy_kwh_per_unit": 5.0,  # Max 5 kWh per product
            "water_liters_per_unit": 15.0,
            "waste_kg_per_unit": 0.5
        }
    
    def calculate_esg_score(
        self,
        production_data: Dict[str, Any],
        environmental_data: Dict[str, Any],
        social_data: Dict[str, Any],
        governance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📊 Calculate comprehensive ESG score (0-100)
        
        Components:
        - E (Environmental): 40% weight
        - S (Social): 30% weight
        - G (Governance): 30% weight
        """
        
        # Environmental score (0-100)
        e_score = self._calculate_environmental_score(
            production_data,
            environmental_data
        )
        
        # Social score (0-100)
        s_score = self._calculate_social_score(social_data)
        
        # Governance score (0-100)
        g_score = self._calculate_governance_score(governance_data)
        
        # Weighted total
        total_score = (
            e_score * 0.4 +
            s_score * 0.3 +
            g_score * 0.3
        )
        
        # Rating
        rating = self._get_esg_rating(total_score)
        
        return {
            "total_score": round(total_score, 2),
            "rating": rating,
            "components": {
                "environmental": {
                    "score": round(e_score, 2),
                    "weight": 0.4,
                    "details": self._get_environmental_details(environmental_data)
                },
                "social": {
                    "score": round(s_score, 2),
                    "weight": 0.3,
                    "details": self._get_social_details(social_data)
                },
                "governance": {
                    "score": round(g_score, 2),
                    "weight": 0.3,
                    "details": self._get_governance_details(governance_data)
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": self._generate_esg_recommendations(e_score, s_score, g_score)
        }
    
    def _calculate_environmental_score(
        self,
        production_data: Dict[str, Any],
        environmental_data: Dict[str, Any]
    ) -> float:
        """Calculate Environmental score"""
        
        units_produced = production_data.get("units_produced", 1000)
        
        # Carbon footprint
        total_carbon = environmental_data.get("carbon_emissions_kg", 2000)
        carbon_per_unit = total_carbon / units_produced
        carbon_score = max(0, 100 - (carbon_per_unit / self.thresholds["carbon_kg_per_unit"]) * 100)
        
        # Energy efficiency
        total_energy = environmental_data.get("energy_consumed_kwh", 5000)
        energy_per_unit = total_energy / units_produced
        energy_score = max(0, 100 - (energy_per_unit / self.thresholds["energy_kwh_per_unit"]) * 100)
        
        # Water usage
        total_water = environmental_data.get("water_used_liters", 10000)
        water_per_unit = total_water / units_produced
        water_score = max(0, 100 - (water_per_unit / self.thresholds["water_liters_per_unit"]) * 100)
        
        # Waste generation
        total_waste = environmental_data.get("waste_generated_kg", 500)
        waste_per_unit = total_waste / units_produced
        waste_score = max(0, 100 - (waste_per_unit / self.thresholds["waste_kg_per_unit"]) * 100)
        
        # Renewable energy usage
        renewable_percent = environmental_data.get("renewable_energy_percent", 30)
        renewable_score = renewable_percent  # Already 0-100
        
        # Weighted average
        e_score = (
            carbon_score * 0.3 +
            energy_score * 0.25 +
            water_score * 0.15 +
            waste_score * 0.15 +
            renewable_score * 0.15
        )
        
        return min(100, max(0, e_score))
    
    def _calculate_social_score(self, social_data: Dict[str, Any]) -> float:
        """Calculate Social score"""
        
        # Worker safety (accidents per 1000 workers)
        accident_rate = social_data.get("accident_rate", 2.5)
        safety_score = max(0, 100 - accident_rate * 10)
        
        # Training hours per employee
        training_hours = social_data.get("training_hours_per_employee", 20)
        training_score = min(100, training_hours * 2.5)  # 40 hours = 100
        
        # Employee satisfaction
        satisfaction = social_data.get("employee_satisfaction_percent", 75)
        
        # Diversity ratio
        diversity_percent = social_data.get("diversity_percent", 35)
        diversity_score = min(100, diversity_percent * 2)  # 50% diversity = 100
        
        # Weighted average
        s_score = (
            safety_score * 0.35 +
            training_score * 0.25 +
            satisfaction * 0.25 +
            diversity_score * 0.15
        )
        
        return min(100, max(0, s_score))
    
    def _calculate_governance_score(self, governance_data: Dict[str, Any]) -> float:
        """Calculate Governance score"""
        
        # Compliance rate
        compliance_percent = governance_data.get("compliance_rate_percent", 95)
        
        # Audit frequency (audits per year)
        audits_per_year = governance_data.get("audits_per_year", 4)
        audit_score = min(100, audits_per_year * 25)  # 4 audits = 100
        
        # Data transparency
        transparency_score = governance_data.get("data_transparency_percent", 80)
        
        # Ethical sourcing
        ethical_sourcing_percent = governance_data.get("ethical_sourcing_percent", 70)
        
        # Weighted average
        g_score = (
            compliance_percent * 0.35 +
            audit_score * 0.25 +
            transparency_score * 0.20 +
            ethical_sourcing_percent * 0.20
        )
        
        return min(100, max(0, g_score))
    
    def _get_esg_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 90:
            return "AAA"
        elif score >= 80:
            return "AA"
        elif score >= 70:
            return "A"
        elif score >= 60:
            return "BBB"
        elif score >= 50:
            return "BB"
        elif score >= 40:
            return "B"
        else:
            return "C"
    
    def _get_environmental_details(self, data: Dict) -> Dict:
        """Get detailed environmental breakdown"""
        return {
            "carbon_emissions_kg": data.get("carbon_emissions_kg", 0),
            "energy_consumed_kwh": data.get("energy_consumed_kwh", 0),
            "water_used_liters": data.get("water_used_liters", 0),
            "waste_generated_kg": data.get("waste_generated_kg", 0),
            "renewable_energy_percent": data.get("renewable_energy_percent", 0)
        }
    
    def _get_social_details(self, data: Dict) -> Dict:
        """Get detailed social breakdown"""
        return {
            "accident_rate": data.get("accident_rate", 0),
            "training_hours": data.get("training_hours_per_employee", 0),
            "satisfaction_percent": data.get("employee_satisfaction_percent", 0),
            "diversity_percent": data.get("diversity_percent", 0)
        }
    
    def _get_governance_details(self, data: Dict) -> Dict:
        """Get detailed governance breakdown"""
        return {
            "compliance_rate": data.get("compliance_rate_percent", 0),
            "audits_per_year": data.get("audits_per_year", 0),
            "transparency_percent": data.get("data_transparency_percent", 0),
            "ethical_sourcing": data.get("ethical_sourcing_percent", 0)
        }
    
    def _generate_esg_recommendations(
        self,
        e_score: float,
        s_score: float,
        g_score: float
    ) -> List[str]:
        """Generate recommendations to improve ESG score"""
        recommendations = []
        
        if e_score < 70:
            recommendations.append("🌱 Increase renewable energy usage to reduce carbon footprint")
            recommendations.append("💡 Optimize energy consumption during off-peak production")
        
        if s_score < 70:
            recommendations.append("👷 Invest in worker safety training programs")
            recommendations.append("📚 Increase employee skill development initiatives")
        
        if g_score < 70:
            recommendations.append("📋 Schedule additional compliance audits")
            recommendations.append("🤝 Improve supply chain transparency and ethical sourcing")
        
        return recommendations
    
    def pareto_optimize(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        🎯 Pareto Optimization: Find optimal balance between Cost, Productivity, Carbon
        
        Args:
            scenarios: List of possible operating scenarios with metrics
        
        Returns:
            Pareto-optimal solutions and recommendations
        """
        
        if not scenarios:
            return {"error": "No scenarios provided"}
        
        # Extract objectives for each scenario
        objectives = []
        for scenario in scenarios:
            objectives.append([
                scenario.get("cost", 0),  # Minimize
                -scenario.get("productivity", 0),  # Maximize (negate for minimization)
                scenario.get("carbon_kg", 0)  # Minimize
            ])
        
        # Find Pareto front
        pareto_indices = self._find_pareto_front(objectives)
        pareto_scenarios = [scenarios[i] for i in pareto_indices]
        
        # Rank scenarios
        ranked = self._rank_scenarios(pareto_scenarios)
        
        return {
            "total_scenarios": len(scenarios),
            "pareto_optimal_count": len(pareto_scenarios),
            "pareto_solutions": ranked,
            "recommendation": ranked[0] if ranked else None,
            "analysis": self._analyze_tradeoffs(ranked)
        }
    
    def _find_pareto_front(self, objectives: List[List[float]]) -> List[int]:
        """Find Pareto-optimal solutions"""
        pareto_indices = []
        
        for i, obj_i in enumerate(objectives):
            is_dominated = False
            
            for j, obj_j in enumerate(objectives):
                if i == j:
                    continue
                
                # Check if obj_j dominates obj_i
                if all(obj_j[k] <= obj_i[k] for k in range(len(obj_i))) and \
                   any(obj_j[k] < obj_i[k] for k in range(len(obj_i))):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_indices.append(i)
        
        return pareto_indices
    
    def _rank_scenarios(self, scenarios: List[Dict]) -> List[Dict]:
        """Rank Pareto-optimal scenarios by composite score"""
        
        scored = []
        for scenario in scenarios:
            # Normalize and combine (lower is better for all)
            cost_norm = scenario.get("cost", 0) / 10000  # Normalize to ~0-1
            productivity_norm = (100 - scenario.get("productivity", 0)) / 100  # Invert
            carbon_norm = scenario.get("carbon_kg", 0) / 1000
            
            # Weighted score (equal weights)
            composite_score = (cost_norm + productivity_norm + carbon_norm) / 3
            
            scored.append({
                "scenario": scenario,
                "composite_score": composite_score
            })
        
        # Sort by composite score (lower is better)
        scored.sort(key=lambda x: x["composite_score"])
        
        return [item["scenario"] for item in scored]
    
    def _analyze_tradeoffs(self, ranked_scenarios: List[Dict]) -> str:
        """Analyze tradeoffs between top scenarios"""
        
        if len(ranked_scenarios) < 2:
            return "Single optimal solution found"
        
        best = ranked_scenarios[0]
        second = ranked_scenarios[1]
        
        cost_diff = best.get("cost", 0) - second.get("cost", 0)
        prod_diff = best.get("productivity", 0) - second.get("productivity", 0)
        carbon_diff = best.get("carbon_kg", 0) - second.get("carbon_kg", 0)
        
        analysis = f"Best scenario saves ${abs(cost_diff):.2f} vs second best, "
        
        if prod_diff > 0:
            analysis += f"with {prod_diff:.1f}% higher productivity "
        else:
            analysis += f"trading {abs(prod_diff):.1f}% productivity "
        
        if carbon_diff < 0:
            analysis += f"and {abs(carbon_diff):.2f} kg less CO₂"
        else:
            analysis += f"but {carbon_diff:.2f} kg more CO₂"
        
        return analysis


# Global instance
esg_optimizer = ESGOptimizer()

