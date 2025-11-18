"""Gemini AI Client"""
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import logging
import json

from config import config

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        self.model = None
        self._configure()
    
    def _configure(self):
        """Configure Gemini API"""
        if not config.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. AI features will be disabled.")
            return
        
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            logger.info(f"Gemini client configured with model: {config.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
    
    async def predict_defect(
        self,
        sensor_data: Dict[str, Any],
        machine_info: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Predict product defect probability using Gemini
        
        Args:
            sensor_data: Current sensor readings
            machine_info: Machine specifications and state
            historical_data: Optional historical sensor data
        
        Returns:
            {
                "defect_probability": float,
                "defect_types": List[str],
                "confidence": float,
                "reasoning": str,
                "recommendations": List[str]
            }
        """
        if not self.model:
            return self._mock_defect_prediction()
        
        try:
            # Prepare prompt
            prompt = f"""
You are an AI expert in smart manufacturing and predictive quality control.

Analyze the following manufacturing data and predict if the current product being manufactured will have defects:

**Current Sensor Data:**
{json.dumps(sensor_data, indent=2)}

**Machine Information:**
{json.dumps(machine_info, indent=2)}

{"**Historical Data (last 10 readings):**" + json.dumps(historical_data[-10:], indent=2) if historical_data else ""}

Based on this data, provide:
1. **Defect Probability** (0.0 to 1.0): Probability that the current product will have defects
2. **Potential Defect Types**: List of possible defect types (e.g., surface scratches, dimensional error, cracks)
3. **Confidence Level** (0.0 to 1.0): Your confidence in this prediction
4. **Reasoning**: Explain what indicators led to this prediction
5. **Recommendations**: Specific actions to prevent the defect

Respond in JSON format:
{{
    "defect_probability": <float>,
    "defect_types": [<string>],
    "confidence": <float>,
    "reasoning": "<string>",
    "recommendations": [<string>]
}}
"""
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config.GEMINI_TEMPERATURE,
                    max_output_tokens=config.GEMINI_MAX_TOKENS,
                )
            )
            
            # Parse response
            result_text = response.text.strip()
            
            # Extract JSON from response (handles markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            logger.info(f"Defect prediction: {result['defect_probability']:.2%} probability")
            return result
        
        except Exception as e:
            logger.error(f"Error in defect prediction: {e}")
            return self._mock_defect_prediction()
    
    async def optimize_energy(
        self,
        current_energy_data: Dict[str, Any],
        production_schedule: Dict[str, Any],
        energy_costs: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Optimize energy consumption and reduce carbon emissions
        
        Returns:
            {
                "optimizations": List[Dict],
                "estimated_savings_kwh": float,
                "estimated_cost_savings": float,
                "carbon_reduction_kg": float,
                "priority_actions": List[str]
            }
        """
        if not self.model:
            return self._mock_energy_optimization()
        
        try:
            prompt = f"""
You are an AI expert in industrial energy optimization and sustainability.

Analyze the following energy data and provide optimization recommendations:

**Current Energy Consumption:**
{json.dumps(current_energy_data, indent=2)}

**Production Schedule:**
{json.dumps(production_schedule, indent=2)}

**Energy Costs (per kWh by time):**
{json.dumps(energy_costs, indent=2)}

Provide actionable recommendations to:
1. Reduce energy consumption
2. Minimize carbon emissions
3. Optimize production scheduling for lower energy costs
4. Identify energy-wasting processes

Respond in JSON format:
{{
    "optimizations": [
        {{
            "machine_id": "<string>",
            "action": "<string>",
            "impact_kwh": <float>,
            "implementation_difficulty": "easy|medium|hard"
        }}
    ],
    "estimated_savings_kwh": <float>,
    "estimated_cost_savings": <float>,
    "carbon_reduction_kg": <float>,
    "priority_actions": [<string>]
}}
"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config.GEMINI_TEMPERATURE,
                    max_output_tokens=config.GEMINI_MAX_TOKENS,
                )
            )
            
            result_text = response.text.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            logger.info(f"Energy optimization: {result['estimated_savings_kwh']:.2f} kWh savings potential")
            return result
        
        except Exception as e:
            logger.error(f"Error in energy optimization: {e}")
            return self._mock_energy_optimization()
    
    async def optimize_supply_chain(
        self,
        inventory_data: Dict[str, Any],
        supplier_performance: Dict[str, Any],
        demand_forecast: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize supply chain and supplier selection
        
        Returns:
            {
                "supplier_recommendations": List[Dict],
                "inventory_optimizations": List[Dict],
                "cost_savings": float,
                "risk_assessment": Dict
            }
        """
        if not self.model:
            return self._mock_supply_chain_optimization()
        
        try:
            prompt = f"""
You are an AI expert in supply chain optimization and logistics.

Analyze the following supply chain data:

**Current Inventory:**
{json.dumps(inventory_data, indent=2)}

**Supplier Performance:**
{json.dumps(supplier_performance, indent=2)}

**Demand Forecast:**
{json.dumps(demand_forecast, indent=2)}

Provide recommendations to:
1. Optimize supplier selection
2. Reduce inventory costs
3. Minimize supply chain risks
4. Improve delivery reliability

Respond in JSON format:
{{
    "supplier_recommendations": [
        {{
            "supplier_id": "<string>",
            "recommendation": "<string>",
            "reasoning": "<string>"
        }}
    ],
    "inventory_optimizations": [
        {{
            "material_id": "<string>",
            "action": "<string>",
            "quantity": <float>
        }}
    ],
    "cost_savings": <float>,
    "risk_assessment": {{
        "overall_risk": "low|medium|high",
        "key_risks": [<string>]
    }}
}}
"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config.GEMINI_TEMPERATURE,
                    max_output_tokens=config.GEMINI_MAX_TOKENS,
                )
            )
            
            result_text = response.text.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            logger.info("Supply chain optimization completed")
            return result
        
        except Exception as e:
            logger.error(f"Error in supply chain optimization: {e}")
            return self._mock_supply_chain_optimization()
    
    def _mock_defect_prediction(self) -> Dict[str, Any]:
        """Mock defect prediction (when Gemini is not available)"""
        import random
        return {
            "defect_probability": random.uniform(0.05, 0.25),
            "defect_types": ["surface_scratch", "dimensional_error"],
            "confidence": 0.85,
            "reasoning": "Mock prediction: Vibration levels slightly elevated",
            "recommendations": [
                "Reduce spindle speed by 5%",
                "Check tool wear",
                "Increase coolant flow"
            ]
        }
    
    def _mock_energy_optimization(self) -> Dict[str, Any]:
        """Mock energy optimization"""
        return {
            "optimizations": [
                {
                    "machine_id": "CNC-001",
                    "action": "Schedule heavy operations during off-peak hours",
                    "impact_kwh": 45.5,
                    "implementation_difficulty": "easy"
                }
            ],
            "estimated_savings_kwh": 120.5,
            "estimated_cost_savings": 25.30,
            "carbon_reduction_kg": 65.2,
            "priority_actions": ["Optimize machine idle time", "Enable power-saving mode"]
        }
    
    def _mock_supply_chain_optimization(self) -> Dict[str, Any]:
        """Mock supply chain optimization"""
        return {
            "supplier_recommendations": [
                {
                    "supplier_id": "SUP-001",
                    "recommendation": "Increase order volume for better pricing",
                    "reasoning": "High performance rating and competitive pricing"
                }
            ],
            "inventory_optimizations": [
                {
                    "material_id": "MAT-001",
                    "action": "reduce_stock",
                    "quantity": 100.0
                }
            ],
            "cost_savings": 5000.0,
            "risk_assessment": {
                "overall_risk": "low",
                "key_risks": ["Single supplier dependency for critical materials"]
            }
        }


# Global Gemini client instance
gemini_client = GeminiClient()

