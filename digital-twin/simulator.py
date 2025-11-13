"""Digital Twin Simulator - Real-time factory simulation"""
import asyncio
import redis
import json
import numpy as np
from datetime import datetime
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class DigitalTwinEngine:
    """
    Digital Twin Engine - Real-time simulation of factory
    
    Simulates physics, machine interactions, and material flow
    """
    
    def __init__(self):
        self.redis_client = None
        self.factory_state = {}
        self.running = False
        
    def connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def initialize_factory(self):
        """Initialize factory digital twin state"""
        self.factory_state = {
            "layout": {
                "width": 200,  # meters
                "height": 100,  # meters
                "zones": [
                    {"name": "Receiving", "x": 0, "y": 0, "w": 40, "h": 100},
                    {"name": "Production Line 1", "x": 40, "y": 0, "w": 60, "h": 50},
                    {"name": "Production Line 2", "x": 40, "y": 50, "w": 60, "h": 50},
                    {"name": "Quality Control", "x": 100, "y": 0, "w": 40, "h": 100},
                    {"name": "Shipping", "x": 140, "y": 0, "w": 60, "h": 100},
                ]
            },
            "machines": {},
            "products_in_progress": [],
            "material_flow": {
                "input_rate": 10.0,  # units per minute
                "output_rate": 9.5,  # units per minute
                "wip": 50  # work in progress
            },
            "environment": {
                "temperature": 22.0,  # Celsius
                "humidity": 45.0,  # percent
                "air_quality": 95.0  # index
            }
        }
        
        logger.info("Factory digital twin initialized")
    
    async def simulate_physics(self):
        """Simulate physical interactions and material flow"""
        while self.running:
            try:
                # Simulate material flow
                wip = self.factory_state["material_flow"]["wip"]
                
                # Random variations
                input_variance = np.random.normal(0, 1)
                output_variance = np.random.normal(0, 0.5)
                
                new_input = max(0, 10.0 + input_variance)
                new_output = max(0, 9.5 + output_variance)
                
                wip += (new_input - new_output) / 60.0  # per second
                wip = max(0, min(200, wip))  # Clamp between 0 and 200
                
                self.factory_state["material_flow"]["wip"] = wip
                self.factory_state["material_flow"]["input_rate"] = new_input
                self.factory_state["material_flow"]["output_rate"] = new_output
                
                # Simulate environment
                env = self.factory_state["environment"]
                env["temperature"] += np.random.normal(0, 0.1)
                env["temperature"] = np.clip(env["temperature"], 20, 26)
                
                env["humidity"] += np.random.normal(0, 0.5)
                env["humidity"] = np.clip(env["humidity"], 35, 60)
                
                # Publish twin state
                twin_state = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "material_flow": self.factory_state["material_flow"],
                    "environment": self.factory_state["environment"]
                }
                
                self.redis_client.setex(
                    "digital_twin:state",
                    60,
                    json.dumps(twin_state)
                )
                
                logger.debug(f"Digital Twin: WIP={wip:.1f}, Input={new_input:.1f}, Output={new_output:.1f}")
                
            except Exception as e:
                logger.error(f"Error in physics simulation: {e}")
            
            await asyncio.sleep(1)
    
    async def simulate_machine_interactions(self):
        """Simulate machine-to-machine interactions"""
        while self.running:
            try:
                # Simulate upstream/downstream machine dependencies
                # e.g., if Machine A produces output, Machine B must have capacity
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in machine interaction simulation: {e}")
    
    async def predict_bottlenecks(self):
        """Predict production bottlenecks"""
        while self.running:
            try:
                wip = self.factory_state["material_flow"]["wip"]
                input_rate = self.factory_state["material_flow"]["input_rate"]
                output_rate = self.factory_state["material_flow"]["output_rate"]
                
                # Simple bottleneck detection
                if wip > 150:
                    logger.warning(f"⚠️ Bottleneck detected: WIP={wip:.1f} (high)")
                    
                    alert = {
                        "type": "bottleneck",
                        "severity": "warning",
                        "message": f"Work in progress is high: {wip:.1f} units",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    self.redis_client.publish("genesis:alerts", json.dumps(alert))
                
                if input_rate > output_rate * 1.2:
                    logger.warning(f"⚠️ Production capacity issue: Input rate exceeds output")
                
            except Exception as e:
                logger.error(f"Error in bottleneck prediction: {e}")
            
            await asyncio.sleep(30)
    
    async def run(self):
        """Main run loop"""
        self.running = True
        
        logger.info("🏭 Genesis Twin Digital Twin Engine starting...")
        
        self.connect_redis()
        self.initialize_factory()
        
        # Start simulation tasks
        tasks = [
            asyncio.create_task(self.simulate_physics()),
            asyncio.create_task(self.simulate_machine_interactions()),
            asyncio.create_task(self.predict_bottlenecks()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down Digital Twin Engine...")
            self.running = False
            
            for task in tasks:
                task.cancel()
            
            logger.info("✅ Digital Twin Engine shut down complete")


if __name__ == "__main__":
    engine = DigitalTwinEngine()
    asyncio.run(engine.run())

