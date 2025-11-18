"""Prediction Engine - orchestrates AI predictions"""
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from config import config

logger = logging.getLogger(__name__)


class PredictionEngine:
    """Orchestrate AI predictions and optimizations"""
    
    def __init__(self, gemini_client):
        self.gemini = gemini_client
        self.sensor_history: Dict[str, List[float]] = {}
        self.anomaly_buffer: Dict[str, List[Dict]] = {}
    
    async def predict_defect(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict product defects based on sensor data
        
        Args:
            sensor_data: Current sensor reading
        
        Returns:
            Prediction result with defect probability and recommendations
        """
        sensor_id = sensor_data.get("sensor_id")
        value = sensor_data.get("value")
        
        # Track sensor history
        if sensor_id not in self.sensor_history:
            self.sensor_history[sensor_id] = []
        
        self.sensor_history[sensor_id].append(value)
        
        # Keep only recent history
        if len(self.sensor_history[sensor_id]) > config.ANOMALY_DETECTION_WINDOW:
            self.sensor_history[sensor_id].pop(0)
        
        # Prepare data for Gemini
        machine_info = {
            "machine_id": sensor_data.get("machine_id"),
            "machine_type": sensor_data.get("machine_type", "CNC"),
            "current_operation": sensor_data.get("operation", "milling")
        }
        
        historical_data = []
        if sensor_id in self.sensor_history and len(self.sensor_history[sensor_id]) > 10:
            recent_values = self.sensor_history[sensor_id][-10:]
            historical_data = [
                {"value": v, "sensor_type": sensor_data.get("sensor_type")}
                for v in recent_values
            ]
        
        # Call Gemini for prediction
        prediction = await self.gemini.predict_defect(
            sensor_data,
            machine_info,
            historical_data
        )
        
        # Add statistical analysis
        prediction["statistical_anomaly"] = self._detect_anomaly(sensor_id, value)
        
        return prediction
    
    async def optimize_energy(self, machine_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize energy consumption
        
        Args:
            machine_state: Current machine state and energy data
        
        Returns:
            Energy optimization recommendations
        """
        current_energy_data = {
            "machine_id": machine_state.get("machine_id"),
            "power_kw": machine_state.get("power_kw", 0),
            "status": machine_state.get("status"),
            "utilization": machine_state.get("utilization", 0)
        }
        
        production_schedule = {
            "current_shift": "day",
            "next_operations": ["milling", "drilling"],
            "priority": "normal"
        }
        
        # Mock energy costs (would come from real-time pricing API)
        energy_costs = {
            "peak": 0.25,      # $/kWh during peak hours
            "off_peak": 0.12,  # $/kWh during off-peak
            "current": 0.18    # $/kWh current rate
        }
        
        # Call Gemini for optimization
        optimization = await self.gemini.optimize_energy(
            current_energy_data,
            production_schedule,
            energy_costs
        )
        
        return optimization
    
    def _detect_anomaly(self, sensor_id: str, value: float) -> bool:
        """
        Simple statistical anomaly detection
        
        Uses Z-score method to detect anomalies
        """
        if sensor_id not in self.sensor_history:
            return False
        
        history = self.sensor_history[sensor_id]
        
        if len(history) < 30:  # Need enough data
            return False
        
        # Calculate mean and std
        mean = np.mean(history)
        std = np.std(history)
        
        if std == 0:
            return False
        
        # Calculate Z-score
        z_score = abs((value - mean) / std)
        
        # Anomaly if Z-score > 3 (3 standard deviations)
        return z_score > 3.0
    
    def get_prediction_metrics(self) -> Dict[str, Any]:
        """Get metrics about prediction engine performance"""
        return {
            "sensors_tracked": len(self.sensor_history),
            "total_data_points": sum(len(h) for h in self.sensor_history.values()),
            "anomalies_detected": sum(
                len(a) for a in self.anomaly_buffer.values()
            )
        }

