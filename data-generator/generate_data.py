"""Data Generator - Simulate factory data"""
import asyncio
import redis
import json
import random
import time
from datetime import datetime
from typing import Dict, Any
import logging
import os

from sensor_simulator import SensorSimulator
from machine_simulator import MachineSimulator
from energy_simulator import EnergySimulator
from qr_scanner_sim import QRScannerSimulator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SIMULATION_INTERVAL_MS = int(os.getenv("SIMULATION_INTERVAL_MS", "1000"))
NUM_SENSORS = int(os.getenv("NUM_SENSORS", "1000"))
NUM_MACHINES = int(os.getenv("NUM_MACHINES", "50"))
NUM_ROBOTS = int(os.getenv("NUM_ROBOTS", "10"))


class DataGenerator:
    """Main data generator orchestrator"""
    
    def __init__(self):
        self.redis_client = None
        self.sensor_sim = SensorSimulator(NUM_SENSORS)
        self.machine_sim = MachineSimulator(NUM_MACHINES)
        self.energy_sim = EnergySimulator(NUM_MACHINES)
        self.qr_sim = QRScannerSimulator(NUM_ROBOTS)
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
    
    async def generate_sensor_data(self):
        """Generate and publish sensor data"""
        while self.running:
            try:
                # Generate data for all sensors
                sensor_readings = self.sensor_sim.generate_readings()
                
                # Publish each reading
                for reading in sensor_readings:
                    self.redis_client.publish(
                        "genesis:sensor:data",
                        json.dumps(reading)
                    )
                
                # Also store in time-series format
                timestamp = datetime.utcnow().isoformat()
                for reading in sensor_readings:
                    key = f"sensor:reading:{reading['sensor_id']}:{timestamp}"
                    self.redis_client.setex(key, 3600, json.dumps(reading))  # 1 hour TTL
                
                logger.debug(f"Published {len(sensor_readings)} sensor readings")
                
            except Exception as e:
                logger.error(f"Error generating sensor data: {e}")
            
            await asyncio.sleep(SIMULATION_INTERVAL_MS / 1000.0)
    
    async def generate_machine_states(self):
        """Generate and publish machine states"""
        while self.running:
            try:
                # Generate machine states
                machine_states = self.machine_sim.generate_states()
                
                # Publish each state
                for state in machine_states:
                    self.redis_client.publish(
                        "genesis:machine:state",
                        json.dumps(state)
                    )
                    
                    # Store current state in Redis
                    self.redis_client.setex(
                        f"machine:state:{state['machine_id']}",
                        300,  # 5 minutes TTL
                        json.dumps(state)
                    )
                
                logger.debug(f"Published {len(machine_states)} machine states")
                
            except Exception as e:
                logger.error(f"Error generating machine states: {e}")
            
            await asyncio.sleep(SIMULATION_INTERVAL_MS / 1000.0)
    
    async def generate_energy_data(self):
        """Generate and publish energy consumption data"""
        while self.running:
            try:
                # Generate energy data for all machines
                energy_data = self.energy_sim.generate_consumption()
                
                # Publish energy data
                for data in energy_data:
                    self.redis_client.publish(
                        "genesis:energy:data",
                        json.dumps(data)
                    )
                
                # Calculate factory-level aggregates
                total_energy = sum(d['energy_kwh'] for d in energy_data)
                total_carbon = sum(d['carbon_kg'] for d in energy_data)
                
                aggregate = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_energy_kwh": total_energy,
                    "total_carbon_kg": total_carbon,
                    "num_machines": len(energy_data)
                }
                
                self.redis_client.setex(
                    "factory:energy:current",
                    60,
                    json.dumps(aggregate)
                )
                
                logger.debug(f"Energy: {total_energy:.2f} kWh, Carbon: {total_carbon:.2f} kg")
                
            except Exception as e:
                logger.error(f"Error generating energy data: {e}")
            
            await asyncio.sleep(SIMULATION_INTERVAL_MS / 1000.0)
    
    async def generate_qr_scans(self):
        """Generate and publish QR scan events"""
        while self.running:
            try:
                # Generate occasional QR scans (not every interval)
                if random.random() < 0.1:  # 10% chance per interval
                    scan_event = self.qr_sim.generate_scan()
                    
                    self.redis_client.publish(
                        "genesis:qr:scan",
                        json.dumps(scan_event)
                    )
                    
                    logger.info(f"QR Scan: {scan_event['qr_code']} by {scan_event['robot_id']}")
                
            except Exception as e:
                logger.error(f"Error generating QR scans: {e}")
            
            await asyncio.sleep(SIMULATION_INTERVAL_MS / 1000.0)
    
    async def publish_statistics(self):
        """Publish statistics about data generation"""
        while self.running:
            try:
                stats = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "sensors": self.sensor_sim.get_stats(),
                    "machines": self.machine_sim.get_stats(),
                    "energy": self.energy_sim.get_stats(),
                    "qr_scans": self.qr_sim.get_stats()
                }
                
                self.redis_client.setex(
                    "genesis:stats:data_generator",
                    60,
                    json.dumps(stats)
                )
                
                logger.info(f"📊 Stats published: {stats['sensors']['active_sensors']} sensors, "
                           f"{stats['machines']['running']} machines running")
                
            except Exception as e:
                logger.error(f"Error publishing statistics: {e}")
            
            await asyncio.sleep(10)  # Every 10 seconds
    
    async def run(self):
        """Main run loop"""
        self.running = True
        
        logger.info("🏭 Genesis Twin Data Generator starting...")
        logger.info(f"Configuration:")
        logger.info(f"  - Sensors: {NUM_SENSORS}")
        logger.info(f"  - Machines: {NUM_MACHINES}")
        logger.info(f"  - Robots: {NUM_ROBOTS}")
        logger.info(f"  - Interval: {SIMULATION_INTERVAL_MS}ms")
        
        # Connect to Redis
        self.connect_redis()
        
        # Start all generators
        tasks = [
            asyncio.create_task(self.generate_sensor_data()),
            asyncio.create_task(self.generate_machine_states()),
            asyncio.create_task(self.generate_energy_data()),
            asyncio.create_task(self.generate_qr_scans()),
            asyncio.create_task(self.publish_statistics()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down data generator...")
            self.running = False
            
            for task in tasks:
                task.cancel()
            
            logger.info("✅ Data generator shut down complete")


if __name__ == "__main__":
    generator = DataGenerator()
    asyncio.run(generator.run())

