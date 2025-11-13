"""AI Core Main Entry Point"""
import asyncio
import redis
import json
import logging
from datetime import datetime

from config import config
from gemini_client import gemini_client
from prediction_engine import PredictionEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AICore:
    """Main AI Core orchestrator"""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.prediction_engine = PredictionEngine(gemini_client)
        self.running = False
    
    def connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                config.REDIS_URL,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Connected to Redis")
            
            # Setup pub/sub
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(
                config.CHANNEL_SENSOR_DATA,
                config.CHANNEL_MACHINE_STATE
            )
            logger.info("Subscribed to data channels")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def process_sensor_data(self, data: dict):
        """Process incoming sensor data"""
        try:
            sensor_id = data.get("sensor_id")
            value = data.get("value")
            timestamp = data.get("timestamp")
            
            logger.debug(f"Processing sensor data: {sensor_id} = {value}")
            
            # Run defect prediction if needed
            if data.get("sensor_type") == "vibration":
                prediction = await self.prediction_engine.predict_defect(data)
                
                if prediction["defect_probability"] > config.DEFECT_CONFIDENCE_THRESHOLD:
                    # Publish alert
                    alert = {
                        "type": "defect_prediction",
                        "severity": "warning",
                        "sensor_id": sensor_id,
                        "prediction": prediction,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    self.redis_client.publish(
                        config.CHANNEL_ALERTS,
                        json.dumps(alert)
                    )
                    
                    logger.warning(f"Defect alert: {prediction['defect_probability']:.2%} probability")
        
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
    
    async def process_machine_state(self, data: dict):
        """Process machine state updates"""
        try:
            machine_id = data.get("machine_id")
            status = data.get("status")
            
            logger.debug(f"Processing machine state: {machine_id} = {status}")
            
            # Run energy optimization periodically
            if status == "running":
                optimization = await self.prediction_engine.optimize_energy(data)
                
                # Store optimization recommendations
                self.redis_client.setex(
                    f"optimization:energy:{machine_id}",
                    300,  # 5 minutes TTL
                    json.dumps(optimization)
                )
        
        except Exception as e:
            logger.error(f"Error processing machine state: {e}")
    
    async def listen_for_messages(self):
        """Listen for Redis pub/sub messages"""
        logger.info("Listening for messages...")
        
        while self.running:
            try:
                message = self.pubsub.get_message(timeout=1.0)
                
                if message and message["type"] == "message":
                    channel = message["channel"]
                    data = json.loads(message["data"])
                    
                    if channel == config.CHANNEL_SENSOR_DATA:
                        await self.process_sensor_data(data)
                    
                    elif channel == config.CHANNEL_MACHINE_STATE:
                        await self.process_machine_state(data)
                
                await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
            
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                await asyncio.sleep(1)
    
    async def periodic_predictions(self):
        """Run periodic predictions and optimizations"""
        logger.info("Starting periodic prediction loop...")
        
        while self.running:
            try:
                # Run supply chain optimization every 5 minutes
                logger.info("Running periodic supply chain optimization...")
                
                # Get inventory data from Redis (mocked for now)
                inventory_data = {
                    "materials": [],
                    "low_stock_items": []
                }
                
                supplier_performance = {
                    "SUP-001": {"rating": 4.5, "on_time_delivery": 0.95}
                }
                
                demand_forecast = {
                    "next_week": 1000,
                    "next_month": 4500
                }
                
                optimization = await gemini_client.optimize_supply_chain(
                    inventory_data,
                    supplier_performance,
                    demand_forecast
                )
                
                # Store results
                self.redis_client.setex(
                    "optimization:supply_chain:latest",
                    300,
                    json.dumps(optimization)
                )
                
                logger.info("Periodic optimization completed")
                
            except Exception as e:
                logger.error(f"Error in periodic predictions: {e}")
            
            # Wait before next run
            await asyncio.sleep(config.PREDICTION_INTERVAL_SECONDS)
    
    async def run(self):
        """Main run loop"""
        self.running = True
        
        logger.info("🚀 Genesis Twin AI Core starting...")
        
        # Connect to Redis
        self.connect_redis()
        
        # Start tasks
        tasks = [
            asyncio.create_task(self.listen_for_messages()),
            asyncio.create_task(self.periodic_predictions()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down AI Core...")
            self.running = False
            
            # Cancel tasks
            for task in tasks:
                task.cancel()
            
            # Cleanup
            if self.pubsub:
                self.pubsub.unsubscribe()
                self.pubsub.close()
            
            logger.info("✅ AI Core shut down complete")


if __name__ == "__main__":
    ai_core = AICore()
    asyncio.run(ai_core.run())

