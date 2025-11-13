"""Autonomous Control Loop - Auto-adjust machine parameters"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class AutonomousControlLoop:
    """
    🤖 Autonomous Control System
    
    Features:
    1. Auto-detect anomalies
    2. Calculate optimal parameters
    3. Send adjustment commands to machines
    4. Monitor effectiveness
    5. Closed-loop feedback
    """
    
    def __init__(self):
        self.active_controls = {}  # Track active control loops
        self.adjustment_history = []
        
    async def detect_and_adjust(
        self,
        machine_id: str,
        sensor_data: Dict[str, Any],
        prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main control loop: Detect → Decide → Adjust → Monitor
        
        Args:
            machine_id: Machine identifier
            sensor_data: Current sensor readings
            prediction: AI prediction result
        
        Returns:
            Adjustment command and expected outcome
        """
        
        # Step 1: Analyze condition
        analysis = self._analyze_condition(sensor_data, prediction)
        
        if not analysis["requires_adjustment"]:
            return {"action": "none", "reason": "Machine operating normally"}
        
        # Step 2: Calculate optimal parameters
        adjustments = self._calculate_adjustments(
            machine_id,
            sensor_data,
            analysis
        )
        
        # Step 3: Validate adjustments (safety checks)
        validated = self._validate_adjustments(adjustments)
        
        if not validated["safe"]:
            logger.warning(f"Unsafe adjustment rejected for {machine_id}: {validated['reason']}")
            return {
                "action": "rejected",
                "reason": validated["reason"],
                "recommendation": "Manual intervention required"
            }
        
        # Step 4: Execute adjustment (send to PLC/SCADA)
        execution_result = await self._execute_adjustment(
            machine_id,
            adjustments
        )
        
        # Step 5: Start monitoring loop
        if execution_result["success"]:
            asyncio.create_task(
                self._monitor_adjustment(machine_id, adjustments)
            )
        
        return execution_result
    
    def _analyze_condition(
        self,
        sensor_data: Dict[str, Any],
        prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze if adjustment is needed"""
        
        vibration = sensor_data.get("vibration_level", 0)
        temperature = sensor_data.get("temperature", 0)
        efficiency = sensor_data.get("efficiency_score", 100)
        
        requires_adjustment = False
        issues = []
        
        # Check vibration
        if vibration > 5.0:
            requires_adjustment = True
            issues.append({
                "type": "high_vibration",
                "severity": "high" if vibration > 6.5 else "medium",
                "value": vibration,
                "threshold": 5.0
            })
        
        # Check temperature
        if temperature > 85.0:
            requires_adjustment = True
            issues.append({
                "type": "high_temperature",
                "severity": "high" if temperature > 90 else "medium",
                "value": temperature,
                "threshold": 85.0
            })
        
        # Check efficiency
        if efficiency < 10.0:
            requires_adjustment = True
            issues.append({
                "type": "low_efficiency",
                "severity": "critical" if efficiency == 0 else "high",
                "value": efficiency,
                "threshold": 10.0
            })
        
        return {
            "requires_adjustment": requires_adjustment,
            "issues": issues,
            "severity": self._calculate_overall_severity(issues)
        }
    
    def _calculate_adjustments(
        self,
        machine_id: str,
        sensor_data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate optimal parameter adjustments"""
        
        adjustments = {
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": {},
            "expected_impact": {}
        }
        
        for issue in analysis["issues"]:
            if issue["type"] == "high_vibration":
                # Reduce spindle speed to reduce vibration
                adjustments["parameters"]["spindle_speed_percent"] = 85
                adjustments["parameters"]["feed_rate_percent"] = 90
                adjustments["expected_impact"]["vibration_reduction"] = "15-20%"
                adjustments["expected_impact"]["production_impact"] = "-15%"
                
            elif issue["type"] == "high_temperature":
                # Increase coolant flow
                adjustments["parameters"]["coolant_flow_percent"] = 120
                adjustments["parameters"]["spindle_speed_percent"] = 95
                adjustments["expected_impact"]["temperature_reduction"] = "5-8°C"
                adjustments["expected_impact"]["production_impact"] = "-5%"
                
            elif issue["type"] == "low_efficiency":
                # Emergency slow down
                adjustments["parameters"]["spindle_speed_percent"] = 70
                adjustments["parameters"]["feed_rate_percent"] = 70
                adjustments["expected_impact"]["risk_reduction"] = "High"
                adjustments["expected_impact"]["allow_completion"] = True
        
        return adjustments
    
    def _validate_adjustments(self, adjustments: Dict[str, Any]) -> Dict[str, bool]:
        """Safety validation before execution"""
        
        params = adjustments.get("parameters", {})
        
        # Check speed limits
        spindle_speed = params.get("spindle_speed_percent", 100)
        if spindle_speed < 50 or spindle_speed > 120:
            return {
                "safe": False,
                "reason": f"Spindle speed {spindle_speed}% outside safe range (50-120%)"
            }
        
        # Check coolant limits
        coolant_flow = params.get("coolant_flow_percent", 100)
        if coolant_flow < 80 or coolant_flow > 150:
            return {
                "safe": False,
                "reason": f"Coolant flow {coolant_flow}% outside safe range (80-150%)"
            }
        
        return {"safe": True}
    
    async def _execute_adjustment(
        self,
        machine_id: str,
        adjustments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute adjustment by sending commands to PLC/SCADA
        
        In production: Send via Modbus/OPC UA/MQTT
        For demo: Simulate command execution
        """
        
        logger.info(f"Executing adjustment for {machine_id}: {adjustments['parameters']}")
        
        # Simulate PLC communication
        try:
            # In production, this would be:
            # await plc_client.write_parameters(machine_id, adjustments['parameters'])
            
            # For demo: simulate success
            await asyncio.sleep(0.5)  # Simulate network delay
            
            # Record adjustment
            adjustment_record = {
                "machine_id": machine_id,
                "timestamp": datetime.utcnow().isoformat(),
                "adjustments": adjustments,
                "status": "executed"
            }
            
            self.adjustment_history.append(adjustment_record)
            self.active_controls[machine_id] = adjustment_record
            
            return {
                "action": "adjusted",
                "success": True,
                "machine_id": machine_id,
                "parameters_changed": adjustments["parameters"],
                "expected_impact": adjustments["expected_impact"],
                "message": f"✅ Parameters adjusted successfully for {machine_id}",
                "monitoring": "Active - will verify effectiveness in 60 seconds"
            }
            
        except Exception as e:
            logger.error(f"Failed to execute adjustment: {e}")
            return {
                "action": "failed",
                "success": False,
                "error": str(e),
                "fallback": "Manual intervention required"
            }
    
    async def _monitor_adjustment(
        self,
        machine_id: str,
        adjustments: Dict[str, Any],
        duration_seconds: int = 300
    ):
        """
        Monitor effectiveness of adjustment (closed-loop feedback)
        
        Checks if adjustment solved the problem or needs refinement
        """
        
        logger.info(f"Starting monitoring for {machine_id} for {duration_seconds}s")
        
        start_time = datetime.utcnow()
        check_interval = 30  # Check every 30 seconds
        
        for i in range(duration_seconds // check_interval):
            await asyncio.sleep(check_interval)
            
            # In production: Query real sensor data
            # For demo: simulate improvement
            
            elapsed = (i + 1) * check_interval
            logger.info(f"Monitoring {machine_id}: {elapsed}s elapsed")
            
            # Simulate condition check
            if elapsed >= 60:
                # Assume adjustment was effective
                logger.info(f"✅ Adjustment successful for {machine_id}")
                
                if machine_id in self.active_controls:
                    self.active_controls[machine_id]["status"] = "effective"
                    self.active_controls[machine_id]["verified_at"] = datetime.utcnow().isoformat()
                
                break
    
    def _calculate_overall_severity(self, issues: List[Dict]) -> str:
        """Calculate overall severity from all issues"""
        if not issues:
            return "none"
        
        severities = [issue["severity"] for issue in issues]
        
        if "critical" in severities:
            return "critical"
        elif "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        else:
            return "low"
    
    def get_active_controls(self) -> List[Dict[str, Any]]:
        """Get all active control loops"""
        return list(self.active_controls.values())
    
    def get_adjustment_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent adjustment history"""
        return self.adjustment_history[-limit:]


# Global instance
autonomous_control = AutonomousControlLoop()

