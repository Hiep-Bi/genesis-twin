"""Energy consumption simulator"""
import random
from typing import List, Dict, Any
from datetime import datetime


class EnergySimulator:
    """Simulate energy consumption and carbon emissions"""
    
    # Carbon intensity (kg CO2 per kWh) - varies by time of day
    CARBON_INTENSITY = {
        "peak": 0.55,      # kg CO2/kWh during peak hours (coal/gas heavy)
        "off_peak": 0.35,  # kg CO2/kWh during off-peak (more renewables)
        "renewable": 0.10  # kg CO2/kWh from renewables
    }
    
    # Energy cost ($/kWh) by time of day
    ENERGY_COST = {
        "peak": 0.25,
        "off_peak": 0.12,
        "renewable": 0.18
    }
    
    def __init__(self, num_machines: int = 50):
        self.num_machines = num_machines
        self.machine_baselines = {}
        
        # Initialize baseline power consumption for each machine
        for i in range(num_machines):
            machine_id = f"MACHINE-{i:03d}"
            self.machine_baselines[machine_id] = {
                "idle_power": random.uniform(5, 15),
                "running_power": random.uniform(30, 80),
                "peak_power": random.uniform(80, 120)
            }
    
    def _get_time_period(self) -> str:
        """Determine current time period for pricing"""
        hour = datetime.now().hour
        
        # Peak hours: 8 AM - 8 PM
        if 8 <= hour < 20:
            return "peak"
        else:
            return "off_peak"
    
    def generate_consumption(self) -> List[Dict[str, Any]]:
        """Generate energy consumption for all machines"""
        time_period = self._get_time_period()
        energy_data = []
        
        for machine_id, baseline in self.machine_baselines.items():
            # Randomly determine machine state
            if random.random() < 0.7:  # 70% running
                base_power = baseline["running_power"]
                # Add some variation
                power_kw = base_power * random.uniform(0.9, 1.1)
            elif random.random() < 0.9:  # 20% idle
                power_kw = baseline["idle_power"] * random.uniform(0.8, 1.2)
            else:  # 10% peak
                power_kw = baseline["peak_power"] * random.uniform(0.95, 1.05)
            
            # Calculate energy consumed in this interval (assuming 1-second intervals)
            energy_kwh = power_kw / 3600  # Convert to kWh
            
            # Calculate carbon emissions
            carbon_intensity = self.CARBON_INTENSITY[time_period]
            carbon_kg = energy_kwh * carbon_intensity
            
            # Calculate cost
            cost_per_kwh = self.ENERGY_COST[time_period]
            cost_usd = energy_kwh * cost_per_kwh
            
            # Create energy data point
            data = {
                "machine_id": machine_id,
                "timestamp": datetime.utcnow().isoformat(),
                "power_kw": round(power_kw, 2),
                "energy_kwh": round(energy_kwh, 6),
                "carbon_kg": round(carbon_kg, 6),
                "cost_usd": round(cost_usd, 4),
                "time_period": time_period,
                "carbon_intensity": carbon_intensity
            }
            
            energy_data.append(data)
        
        return energy_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about energy simulation"""
        time_period = self._get_time_period()
        
        return {
            "num_machines": self.num_machines,
            "current_time_period": time_period,
            "carbon_intensity": self.CARBON_INTENSITY[time_period],
            "energy_cost": self.ENERGY_COST[time_period]
        }

