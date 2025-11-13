"""Orchestration Engine - Coordinate robots, AGVs, machines holistically"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import heapq
import math

logger = logging.getLogger(__name__)


class OrchestrationEngine:
    """
    🎭 Factory Orchestration System
    
    Coordinates:
    - AGV task assignment & routing
    - Machine scheduling
    - Resource optimization
    - Bottleneck prevention
    """
    
    def __init__(self):
        self.agv_fleet = {}  # AGV status
        self.task_queue = []  # Priority queue of tasks
        self.factory_map = self._initialize_factory_map()
        
    def _initialize_factory_map(self) -> Dict[str, Any]:
        """Initialize factory floor layout"""
        return {
            "zones": {
                "receiving": {"x": 0, "y": 0, "w": 40, "h": 100},
                "warehouse": {"x": 40, "y": 0, "w": 30, "h": 100},
                "production_line_1": {"x": 70, "y": 0, "w": 60, "h": 50},
                "production_line_2": {"x": 70, "y": 50, "w": 60, "h": 50},
                "qc": {"x": 130, "y": 0, "w": 30, "h": 100},
                "shipping": {"x": 160, "y": 0, "w": 40, "h": 100}
            },
            "obstacles": [],  # Walls, machines
            "agv_stations": [
                {"id": "station_1", "x": 35, "y": 50},
                {"id": "station_2", "x": 65, "y": 50},
                {"id": "station_3", "x": 125, "y": 50}
            ]
        }
    
    async def assign_agv_task(
        self,
        task_type: str,
        from_location: Dict[str, float],
        to_location: Dict[str, float],
        priority: int = 5,
        payload: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🚚 Assign task to optimal AGV
        
        Args:
            task_type: 'transport_material', 'qr_scan', 'delivery'
            from_location: Start position {x, y}
            to_location: End position {x, y}
            priority: 1 (low) to 10 (critical)
            payload: Additional task data
        
        Returns:
            Assignment result with AGV ID, route, ETA
        """
        
        # Find available AGV closest to start location
        available_agvs = self._get_available_agvs()
        
        if not available_agvs:
            return {
                "status": "queued",
                "message": "No AGV available, task queued",
                "queue_position": len(self.task_queue)
            }
        
        # Select best AGV (closest + least busy)
        best_agv = self._select_best_agv(available_agvs, from_location, priority)
        
        # Calculate optimal route
        route = self._calculate_route(
            from_pos=best_agv["current_position"],
            pickup_pos=from_location,
            delivery_pos=to_location
        )
        
        # Estimate time
        eta = self._estimate_travel_time(route)
        
        # Assign task
        task = {
            "task_id": f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "agv_id": best_agv["id"],
            "task_type": task_type,
            "from": from_location,
            "to": to_location,
            "route": route,
            "eta_seconds": eta,
            "priority": priority,
            "status": "assigned",
            "assigned_at": datetime.utcnow().isoformat(),
            "payload": payload or {}
        }
        
        # Update AGV status
        self.agv_fleet[best_agv["id"]]["status"] = "busy"
        self.agv_fleet[best_agv["id"]]["current_task"] = task
        
        logger.info(f"Task {task['task_id']} assigned to {best_agv['id']}, ETA: {eta}s")
        
        return {
            "status": "assigned",
            "task": task,
            "message": f"✅ AGV {best_agv['id']} assigned, ETA: {eta} seconds"
        }
    
    def _get_available_agvs(self) -> List[Dict[str, Any]]:
        """Get list of available AGVs"""
        # Mock AGV fleet (in production: query from real-time tracking)
        if not self.agv_fleet:
            self.agv_fleet = {
                f"AGV-{i:02d}": {
                    "id": f"AGV-{i:02d}",
                    "status": "idle",
                    "current_position": {"x": 35 + i*30, "y": 50},
                    "battery_percent": 85 + i*2,
                    "current_task": None
                }
                for i in range(10)
            }
        
        return [
            agv for agv in self.agv_fleet.values()
            if agv["status"] == "idle" and agv["battery_percent"] > 20
        ]
    
    def _select_best_agv(
        self,
        available_agvs: List[Dict],
        target_location: Dict[str, float],
        priority: int
    ) -> Dict[str, Any]:
        """Select best AGV based on distance and battery"""
        
        scored_agvs = []
        
        for agv in available_agvs:
            distance = self._calculate_distance(
                agv["current_position"],
                target_location
            )
            
            # Score: lower distance = better, higher battery = better
            score = distance - (agv["battery_percent"] / 10)
            
            # Priority tasks get AGVs with higher battery
            if priority >= 8:
                score -= (agv["battery_percent"] / 5)
            
            scored_agvs.append((score, agv))
        
        # Return AGV with lowest score (best)
        scored_agvs.sort(key=lambda x: x[0])
        return scored_agvs[0][1]
    
    def _calculate_route(
        self,
        from_pos: Dict[str, float],
        pickup_pos: Dict[str, float],
        delivery_pos: Dict[str, float]
    ) -> List[Dict[str, float]]:
        """
        Calculate optimal route using A* algorithm
        
        Route: Current position → Pickup → Delivery
        """
        
        # Simplified: direct path with waypoints
        # In production: Use A* with obstacle avoidance
        
        route = [
            from_pos,
            pickup_pos,
            delivery_pos
        ]
        
        return route
    
    def _calculate_distance(
        self,
        pos1: Dict[str, float],
        pos2: Dict[str, float]
    ) -> float:
        """Calculate Euclidean distance between two points"""
        dx = pos2["x"] - pos1["x"]
        dy = pos2["y"] - pos1["y"]
        return math.sqrt(dx**2 + dy**2)
    
    def _estimate_travel_time(self, route: List[Dict[str, float]]) -> int:
        """Estimate travel time in seconds (AGV speed: ~1 m/s)"""
        total_distance = 0
        
        for i in range(len(route) - 1):
            total_distance += self._calculate_distance(route[i], route[i+1])
        
        # AGV speed: 1 meter/second, add 10s per stop
        travel_time = total_distance + (len(route) - 1) * 10
        
        return int(travel_time)
    
    async def coordinate_machines(
        self,
        production_schedule: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        🏭 Coordinate machine operations for optimal throughput
        
        Args:
            production_schedule: List of production orders
        
        Returns:
            Optimized schedule with machine assignments
        """
        
        # Group tasks by priority and dependencies
        prioritized = sorted(
            production_schedule,
            key=lambda x: (x.get("priority", 5), x.get("deadline", "9999"))
        )
        
        # Assign to machines
        machine_assignments = {}
        
        for task in prioritized:
            # Find best machine (idle, capable, lowest queue)
            best_machine = self._find_best_machine_for_task(task)
            
            if best_machine:
                if best_machine not in machine_assignments:
                    machine_assignments[best_machine] = []
                
                machine_assignments[best_machine].append(task)
        
        return {
            "status": "optimized",
            "assignments": machine_assignments,
            "total_tasks": len(production_schedule),
            "estimated_completion": self._estimate_completion_time(machine_assignments)
        }
    
    def _find_best_machine_for_task(self, task: Dict[str, Any]) -> Optional[str]:
        """Find best machine for a task"""
        # Mock: return random machine
        # In production: check machine capabilities, current load, location
        machine_types = {
            "machining": ["MACHINE-003", "MACHINE-007", "MACHINE-012"],
            "assembly": ["MACHINE-020", "MACHINE-025"],
            "welding": ["MACHINE-030", "MACHINE-035"]
        }
        
        task_type = task.get("operation_type", "machining")
        candidates = machine_types.get(task_type, ["MACHINE-001"])
        
        return candidates[0] if candidates else None
    
    def _estimate_completion_time(self, assignments: Dict) -> str:
        """Estimate when all tasks will complete"""
        # Simplified estimation
        max_tasks = max(len(tasks) for tasks in assignments.values()) if assignments else 0
        estimated_minutes = max_tasks * 30  # 30 min per task average
        
        return f"{estimated_minutes} minutes"
    
    def get_fleet_status(self) -> Dict[str, Any]:
        """Get current AGV fleet status"""
        idle = sum(1 for agv in self.agv_fleet.values() if agv["status"] == "idle")
        busy = sum(1 for agv in self.agv_fleet.values() if agv["status"] == "busy")
        
        return {
            "total_agvs": len(self.agv_fleet),
            "idle": idle,
            "busy": busy,
            "utilization_percent": (busy / len(self.agv_fleet) * 100) if self.agv_fleet else 0,
            "fleet_details": list(self.agv_fleet.values())
        }


# Global instance
orchestration_engine = OrchestrationEngine()

