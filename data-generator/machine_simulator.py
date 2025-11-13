"""Machine state simulator"""
import random
from typing import List, Dict, Any
from datetime import datetime


class MachineSimulator:
    """Simulate machine states and production metrics"""
    
    MACHINE_TYPES = ["CNC", "Robot", "AGV", "Assembly", "Injection"]
    STATES = ["idle", "running", "maintenance", "error"]
    
    def __init__(self, num_machines: int = 50):
        self.num_machines = num_machines
        self.machines = self._initialize_machines()
        self.machine_states = {}
    
    def _initialize_machines(self) -> List[Dict[str, Any]]:
        """Initialize machine configurations"""
        machines = []
        
        for i in range(self.num_machines):
            machine = {
                "machine_id": f"MACHINE-{i:03d}",
                "machine_code": f"{random.choice(self.MACHINE_TYPES)}-{i:03d}",
                "machine_type": random.choice(self.MACHINE_TYPES),
                "name": f"Machine {i+1}",
            }
            
            machines.append(machine)
            
            # Initialize state
            self.machine_states[machine["machine_id"]] = {
                "status": random.choice(["idle", "running", "running"]),  # More likely running
                "oee": random.uniform(0.7, 0.95),
                "production_count": 0,
                "defect_count": 0,
                "uptime_minutes": 0
            }
        
        return machines
    
    def generate_states(self) -> List[Dict[str, Any]]:
        """Generate current states for all machines"""
        states = []
        
        for machine in self.machines:
            machine_id = machine["machine_id"]
            state = self.machine_states[machine_id]
            
            # Randomly change state (5% chance)
            if random.random() < 0.05:
                state["status"] = random.choice(self.STATES)
            
            # If running, accumulate metrics
            if state["status"] == "running":
                state["production_count"] += random.randint(0, 5)
                
                # Occasionally produce defect (3% chance)
                if random.random() < 0.03:
                    state["defect_count"] += 1
                
                state["uptime_minutes"] += 1
                
                # OEE varies slightly
                state["oee"] += random.gauss(0, 0.02)
                state["oee"] = max(0.5, min(1.0, state["oee"]))
            
            # Calculate availability, performance, quality
            availability = state["oee"] * random.uniform(0.95, 1.0)
            performance = state["oee"] * random.uniform(0.90, 1.0)
            
            quality = 1.0
            if state["production_count"] > 0:
                quality = 1.0 - (state["defect_count"] / state["production_count"])
            
            # Create state message
            state_msg = {
                "machine_id": machine_id,
                "machine_code": machine["machine_code"],
                "machine_type": machine["machine_type"],
                "status": state["status"],
                "timestamp": datetime.utcnow().isoformat(),
                "oee": round(state["oee"], 3),
                "availability": round(availability, 3),
                "performance": round(performance, 3),
                "quality": round(quality, 3),
                "production_count": state["production_count"],
                "defect_count": state["defect_count"],
                "uptime_minutes": state["uptime_minutes"],
                "power_kw": self._calculate_power(state["status"]),
                "utilization": random.uniform(0.6, 0.95) if state["status"] == "running" else 0
            }
            
            states.append(state_msg)
        
        return states
    
    def _calculate_power(self, status: str) -> float:
        """Calculate power consumption based on machine status"""
        if status == "running":
            return random.uniform(30, 80)
        elif status == "idle":
            return random.uniform(5, 15)
        else:
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about machine simulation"""
        status_counts = {}
        for state in self.machine_states.values():
            status = state["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_machines": self.num_machines,
            "running": status_counts.get("running", 0),
            "idle": status_counts.get("idle", 0),
            "maintenance": status_counts.get("maintenance", 0),
            "error": status_counts.get("error", 0)
        }

