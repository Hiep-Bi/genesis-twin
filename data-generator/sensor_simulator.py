"""Sensor data simulator"""
import random
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import uuid


class SensorSimulator:
    """Simulate sensor readings for factory machines"""
    
    SENSOR_TYPES = {
        "temperature": {"unit": "°C", "min": 20, "max": 100, "normal": (40, 60)},
        "vibration": {"unit": "mm/s", "min": 0, "max": 50, "normal": (5, 15)},
        "pressure": {"unit": "bar", "min": 0, "max": 10, "normal": (2, 6)},
        "speed": {"unit": "rpm", "min": 0, "max": 5000, "normal": (1000, 3000)},
        "power": {"unit": "kW", "min": 0, "max": 100, "normal": (20, 60)},
    }
    
    def __init__(self, num_sensors: int = 1000):
        self.num_sensors = num_sensors
        self.sensors = self._initialize_sensors()
        self.sensor_states = {}  # Track current state for each sensor
    
    def _initialize_sensors(self) -> List[Dict[str, Any]]:
        """Initialize sensor configurations"""
        sensors = []
        
        for i in range(self.num_sensors):
            sensor_type = random.choice(list(self.SENSOR_TYPES.keys()))
            spec = self.SENSOR_TYPES[sensor_type]
            
            sensor = {
                "sensor_id": f"SENSOR-{i:04d}",
                "sensor_type": sensor_type,
                "machine_id": f"MACHINE-{i % 50:03d}",  # Distribute across machines
                "unit": spec["unit"],
                "min_value": spec["min"],
                "max_value": spec["max"],
                "normal_range": spec["normal"],
            }
            
            sensors.append(sensor)
            
            # Initialize state
            self.sensor_states[sensor["sensor_id"]] = {
                "value": random.uniform(*spec["normal"]),
                "trend": 0,  # -1: decreasing, 0: stable, 1: increasing
                "anomaly": False
            }
        
        return sensors
    
    def generate_readings(self) -> List[Dict[str, Any]]:
        """Generate current readings for all sensors"""
        readings = []
        
        for sensor in self.sensors:
            sensor_id = sensor["sensor_id"]
            state = self.sensor_states[sensor_id]
            spec = self.SENSOR_TYPES[sensor["sensor_type"]]
            
            # Generate new value based on previous value and trend
            current_value = state["value"]
            
            # Random walk with drift
            drift = state["trend"] * random.uniform(0, 2)
            noise = random.gauss(0, 1)
            new_value = current_value + drift + noise
            
            # Clamp to sensor range
            new_value = max(spec["min"], min(spec["max"], new_value))
            
            # Occasionally introduce anomalies (5% chance)
            anomaly = False
            if random.random() < 0.05:
                anomaly = True
                # Spike or drop
                if random.random() < 0.5:
                    new_value = random.uniform(spec["normal"][1], spec["max"])
                else:
                    new_value = random.uniform(spec["min"], spec["normal"][0"])
            
            # Update state
            state["value"] = new_value
            state["anomaly"] = anomaly
            
            # Occasionally change trend (10% chance)
            if random.random() < 0.1:
                state["trend"] = random.choice([-1, 0, 1])
            
            # Create reading
            reading = {
                "sensor_id": sensor_id,
                "machine_id": sensor["machine_id"],
                "sensor_type": sensor["sensor_type"],
                "value": round(new_value, 2),
                "unit": sensor["unit"],
                "timestamp": datetime.utcnow().isoformat(),
                "quality": "bad" if anomaly else "good",
                "anomaly_score": random.uniform(0.7, 1.0) if anomaly else random.uniform(0, 0.3)
            }
            
            readings.append(reading)
        
        return readings
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about sensor simulation"""
        anomalies = sum(1 for s in self.sensor_states.values() if s["anomaly"])
        
        return {
            "total_sensors": self.num_sensors,
            "active_sensors": len(self.sensors),
            "current_anomalies": anomalies,
            "types": list(self.SENSOR_TYPES.keys())
        }

