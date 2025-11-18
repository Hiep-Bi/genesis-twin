"""
Data Pipeline - Batch Processing & Streaming
Server nhận toàn bộ tín hiệu, backend chia nhỏ, user render
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
import json

logger = logging.getLogger(__name__)


class DataPipeline:
    """
    Data Pipeline cho xử lý dữ liệu lớn:
    - Nhận toàn bộ tín hiệu từ server
    - Chia nhỏ thành batches
    - Process và lưu vào database
    - Render cho user qua WebSocket
    """
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        
        # Batch processing config
        self.batch_size = 1000  # Process 1000 records at a time
        self.batch_timeout = 5  # seconds - flush batch after timeout
        self.buffer = deque(maxlen=10000)  # Buffer tối đa 10k records
        
        # Statistics
        self.stats = {
            'total_received': 0,
            'total_processed': 0,
            'total_batches': 0,
            'last_batch_time': None,
            'avg_processing_time': 0
        }
    
    async def receive_sensor_data(self, data: Dict[str, Any]):
        """
        Nhận sensor data từ server
        - Add vào buffer
        - Trigger batch processing nếu đủ
        """
        # Add timestamp
        data['received_at'] = datetime.utcnow().isoformat()
        
        # Add to buffer
        self.buffer.append(data)
        self.stats['total_received'] += 1
        
        # Check if batch is full
        if len(self.buffer) >= self.batch_size:
            await self.process_batch()
    
    async def process_batch(self):
        """
        Process một batch data:
        1. Extract batch từ buffer
        2. Validate và clean data
        3. Insert vào database (bulk insert)
        4. Publish to Redis for real-time updates
        5. Trigger AI prediction nếu cần
        """
        if len(self.buffer) == 0:
            return
        
        start_time = datetime.utcnow()
        
        # Extract batch
        batch = []
        for _ in range(min(self.batch_size, len(self.buffer))):
            if self.buffer:
                batch.append(self.buffer.popleft())
        
        if not batch:
            return
        
        try:
            # Convert to DataFrame for processing
            df = pd.DataFrame(batch)
            
            # Data cleaning
            df = self._clean_data(df)
            
            # Bulk insert to database
            await self._bulk_insert(df)
            
            # Publish to Redis for real-time updates
            await self._publish_updates(df)
            
            # Update stats
            self.stats['total_processed'] += len(batch)
            self.stats['total_batches'] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.stats['avg_processing_time'] = (
                (self.stats['avg_processing_time'] * (self.stats['total_batches'] - 1) + processing_time) 
                / self.stats['total_batches']
            )
            self.stats['last_batch_time'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ Processed batch: {len(batch)} records in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            # Re-add to buffer for retry
            for item in batch:
                self.buffer.appendleft(item)
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean và validate data
        """
        # Remove duplicates
        df = df.drop_duplicates(subset=['machine_id', 'timestamp'], keep='last')
        
        # Fill missing values
        numeric_cols = ['temperature', 'vibration_level', 'power_consumption', 
                        'pressure', 'material_flow_rate', 'cycle_time', 
                        'error_rate', 'efficiency_score']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(df[col].median())
        
        # Outlier detection (3-sigma rule)
        for col in numeric_cols:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    df[col] = df[col].clip(lower=mean - 3*std, upper=mean + 3*std)
        
        # Ensure required columns
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        else:
            df['timestamp'] = datetime.utcnow()
        
        return df
    
    async def _bulk_insert(self, df: pd.DataFrame):
        """
        Bulk insert vào database (efficient)
        """
        try:
            # Convert to list of dicts
            records = df.to_dict('records')
            
            # Bulk insert query
            query = text("""
                INSERT INTO sensor_readings (
                    timestamp, machine_id, machine_type,
                    temperature, vibration_level, power_consumption,
                    pressure, material_flow_rate, cycle_time,
                    error_rate, efficiency_score, production_status
                ) VALUES (
                    :timestamp, :machine_id, :machine_type,
                    :temperature, :vibration_level, :power_consumption,
                    :pressure, :material_flow_rate, :cycle_time,
                    :error_rate, :efficiency_score, :production_status
                )
                ON CONFLICT (timestamp, machine_id) DO UPDATE SET
                    temperature = EXCLUDED.temperature,
                    vibration_level = EXCLUDED.vibration_level,
                    power_consumption = EXCLUDED.power_consumption,
                    pressure = EXCLUDED.pressure,
                    material_flow_rate = EXCLUDED.material_flow_rate,
                    cycle_time = EXCLUDED.cycle_time,
                    error_rate = EXCLUDED.error_rate,
                    efficiency_score = EXCLUDED.efficiency_score,
                    production_status = EXCLUDED.production_status
            """)
            
            # Execute bulk insert
            self.db.execute(query, records)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def _publish_updates(self, df: pd.DataFrame):
        """
        Publish updates to Redis for real-time rendering
        """
        try:
            # Group by machine
            for machine_id in df['machine_id'].unique():
                machine_data = df[df['machine_id'] == machine_id].iloc[-1].to_dict()
                
                # Publish to Redis channel
                channel = f"genesis:sensor:{machine_id}"
                self.redis.publish(channel, json.dumps(machine_data))
            
            # Publish aggregated stats
            stats = {
                'total_machines': df['machine_id'].nunique(),
                'avg_temperature': float(df['temperature'].mean()),
                'avg_vibration': float(df['vibration_level'].mean()),
                'avg_efficiency': float(df['efficiency_score'].mean()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.redis.publish("genesis:stats:aggregated", json.dumps(stats))
            
        except Exception as e:
            logger.error(f"Error publishing updates: {e}")
    
    async def periodic_flush(self):
        """
        Periodically flush buffer (even if not full)
        """
        while True:
            await asyncio.sleep(self.batch_timeout)
            
            if len(self.buffer) > 0:
                logger.info(f"Flushing buffer: {len(self.buffer)} records")
                await self.process_batch()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            **self.stats,
            'buffer_size': len(self.buffer),
            'throughput': self.stats['total_processed'] / max(self.stats['avg_processing_time'], 0.001) if self.stats['avg_processing_time'] > 0 else 0
        }


class DataRenderer:
    """
    Render data cho user (WebSocket streaming)
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.pubsub = redis_client.pubsub()
    
    async def stream_to_user(self, user_id: str, channels: List[str]):
        """
        Stream data to user via WebSocket
        """
        # Subscribe to channels
        for channel in channels:
            self.pubsub.subscribe(channel)
        
        try:
            while True:
                message = self.pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    data = json.loads(message['data'])
                    yield {
                        'channel': message['channel'].decode(),
                        'data': data,
                        'timestamp': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            logger.error(f"Error streaming to user: {e}")
        finally:
            self.pubsub.unsubscribe()
    
    def get_latest_data(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """
        Get latest data for a machine (for initial render)
        """
        key = f"genesis:sensor:{machine_id}:latest"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

