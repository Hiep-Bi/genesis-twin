"""
IoT Hub - Gateway cho Sensor Data
Nhận toàn bộ tín hiệu từ sensors, filter, aggregate trước khi đưa vào DB
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import redis
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class IoTHub:
    """
    IoT Hub - Gateway trung tâm nhận data từ sensors
    
    Chức năng:
    1. Nhận toàn bộ tín hiệu từ sensors (máy móc, AGV, robots)
    2. Filter & validate data (loại bỏ data lỗi)
    3. Aggregate data (tính trung bình, max, min)
    4. Chỉ lưu data quan trọng vào DB (giảm 80-90% storage)
    5. Forward real-time data cho dashboard (WebSocket)
    """
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        
        # Configuration
        self.aggregation_window = 60  # seconds - aggregate data mỗi 1 phút
        self.min_change_threshold = 0.05  # 5% change mới lưu vào DB
        
        # In-memory buffer cho aggregation
        self.buffer = defaultdict(list)  # {machine_id: [data_points]}
        self.last_saved = {}  # {machine_id: last_saved_data}
        
        # Statistics
        self.stats = {
            'total_received': 0,
            'total_filtered': 0,
            'total_saved_to_db': 0,
            'total_forwarded': 0,
            'reduction_rate': 0.0
        }
    
    async def receive_sensor_data(self, sensor_data: Dict[str, Any]):
        """
        Nhận data từ sensor
        
        Args:
            sensor_data: {
                'machine_id': 'M001',
                'timestamp': '2025-01-13T10:00:00',
                'temperature': 75.5,
                'vibration_level': 2.3,
                ...
            }
        """
        self.stats['total_received'] += 1
        
        # Validate data
        if not self._validate_data(sensor_data):
            self.stats['total_filtered'] += 1
            logger.warning(f"Invalid data filtered: {sensor_data.get('machine_id')}")
            return
        
        machine_id = sensor_data.get('machine_id')
        if not machine_id:
            return
        
        # Add to buffer for aggregation
        self.buffer[machine_id].append({
            **sensor_data,
            'received_at': datetime.utcnow().isoformat()
        })
        
        # Forward real-time data to dashboard (always)
        await self._forward_realtime(sensor_data)
        
        # Check if need to aggregate and save
        if len(self.buffer[machine_id]) >= 10:  # Aggregate every 10 points
            await self._aggregate_and_save(machine_id)
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate sensor data - loại bỏ data lỗi
        """
        required_fields = ['machine_id', 'timestamp']
        if not all(field in data for field in required_fields):
            return False
        
        # Check numeric ranges
        if 'temperature' in data:
            temp = float(data.get('temperature', 0))
            if temp < -50 or temp > 200:  # Unrealistic temperature
                return False
        
        if 'vibration_level' in data:
            vib = float(data.get('vibration_level', 0))
            if vib < 0 or vib > 100:  # Unrealistic vibration
                return False
        
        return True
    
    async def _aggregate_and_save(self, machine_id: str):
        """
        Aggregate data và chỉ lưu vào DB nếu có thay đổi đáng kể
        """
        if machine_id not in self.buffer or len(self.buffer[machine_id]) == 0:
            return
        
        # Get buffer data
        data_points = self.buffer[machine_id]
        self.buffer[machine_id] = []  # Clear buffer
        
        # Aggregate (calculate average, max, min)
        aggregated = self._calculate_aggregates(data_points)
        
        # Check if significant change from last saved
        if self._has_significant_change(machine_id, aggregated):
            # Save to database
            await self._save_to_database(aggregated)
            self.last_saved[machine_id] = aggregated
            self.stats['total_saved_to_db'] += 1
        
        # Update reduction rate
        self._update_reduction_rate()
    
    def _calculate_aggregates(self, data_points: List[Dict]) -> Dict[str, Any]:
        """
        Tính toán aggregate values (avg, max, min)
        """
        if not data_points:
            return {}
        
        # Get numeric columns
        numeric_cols = ['temperature', 'vibration_level', 'power_consumption',
                       'pressure', 'material_flow_rate', 'cycle_time',
                       'error_rate', 'efficiency_score']
        
        aggregated = {
            'machine_id': data_points[0].get('machine_id'),
            'machine_type': data_points[0].get('machine_type'),
            'timestamp': data_points[-1].get('timestamp'),  # Latest timestamp
            'data_count': len(data_points),
            'aggregated_at': datetime.utcnow().isoformat()
        }
        
        # Calculate aggregates for each numeric column
        for col in numeric_cols:
            values = [float(d.get(col, 0)) for d in data_points if col in d]
            if values:
                aggregated[f'{col}_avg'] = sum(values) / len(values)
                aggregated[f'{col}_max'] = max(values)
                aggregated[f'{col}_min'] = min(values)
                aggregated[col] = aggregated[f'{col}_avg']  # Use avg as main value
        
        # Keep non-numeric fields from latest point
        for key, value in data_points[-1].items():
            if key not in numeric_cols and key not in ['timestamp', 'received_at']:
                aggregated[key] = value
        
        return aggregated
    
    def _has_significant_change(self, machine_id: str, new_data: Dict[str, Any]) -> bool:
        """
        Check if data has significant change (>= 5%) compared to last saved
        """
        if machine_id not in self.last_saved:
            return True  # First time, always save
        
        last_data = self.last_saved[machine_id]
        
        # Check key metrics
        key_metrics = ['temperature', 'vibration_level', 'efficiency_score', 'error_rate']
        
        for metric in key_metrics:
            if metric in new_data and metric in last_data:
                old_val = float(last_data[metric])
                new_val = float(new_data[metric])
                
                if old_val == 0:
                    return True  # Avoid division by zero
                
                change_pct = abs((new_val - old_val) / old_val)
                if change_pct >= self.min_change_threshold:
                    return True  # Significant change detected
        
        return False  # No significant change
    
    async def _save_to_database(self, aggregated_data: Dict[str, Any]):
        """
        Save aggregated data to database
        """
        try:
            from sqlalchemy import text
            
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
            """)
            
            # Map aggregated fields
            record = {
                'timestamp': aggregated_data.get('timestamp'),
                'machine_id': aggregated_data.get('machine_id'),
                'machine_type': aggregated_data.get('machine_type'),
                'temperature': aggregated_data.get('temperature', 0),
                'vibration_level': aggregated_data.get('vibration_level', 0),
                'power_consumption': aggregated_data.get('power_consumption', 0),
                'pressure': aggregated_data.get('pressure', 0),
                'material_flow_rate': aggregated_data.get('material_flow_rate', 0),
                'cycle_time': aggregated_data.get('cycle_time', 0),
                'error_rate': aggregated_data.get('error_rate', 0),
                'efficiency_score': aggregated_data.get('efficiency_score', 0),
                'production_status': aggregated_data.get('production_status', 0)
            }
            
            self.db.execute(query, record)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving to database: {e}")
    
    async def _forward_realtime(self, sensor_data: Dict[str, Any]):
        """
        Forward real-time data to dashboard (via Redis pub/sub)
        Không lưu vào DB, chỉ để hiển thị real-time
        """
        machine_id = sensor_data.get('machine_id')
        if not machine_id:
            return
        
        # Publish to Redis channel
        channel = f"genesis:realtime:{machine_id}"
        self.redis.publish(channel, json.dumps(sensor_data))
        
        # Also publish aggregated stats
        channel_stats = "genesis:realtime:stats"
        stats = {
            'machine_id': machine_id,
            'timestamp': datetime.utcnow().isoformat(),
            'temperature': sensor_data.get('temperature'),
            'vibration_level': sensor_data.get('vibration_level'),
            'efficiency_score': sensor_data.get('efficiency_score')
        }
        self.redis.publish(channel_stats, json.dumps(stats))
        
        self.stats['total_forwarded'] += 1
    
    def _update_reduction_rate(self):
        """Calculate data reduction rate"""
        if self.stats['total_received'] > 0:
            saved = self.stats['total_saved_to_db']
            received = self.stats['total_received']
            self.stats['reduction_rate'] = (1 - saved / received) * 100 if received > 0 else 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get IoT Hub statistics"""
        return {
            **self.stats,
            'buffer_size': sum(len(v) for v in self.buffer.values()),
            'active_machines': len(self.buffer),
            'efficiency': f"{self.stats['reduction_rate']:.1f}% data reduction"
        }
    
    async def periodic_flush(self):
        """
        Periodically flush buffer (even if not full)
        """
        while True:
            await asyncio.sleep(self.aggregation_window)
            
            for machine_id in list(self.buffer.keys()):
                if len(self.buffer[machine_id]) > 0:
                    await self._aggregate_and_save(machine_id)


# Global instance
iot_hub = None

def get_iot_hub(db: Session, redis_client: redis.Redis) -> IoTHub:
    """Get or create IoT Hub instance"""
    global iot_hub
    if iot_hub is None:
        iot_hub = IoTHub(db, redis_client)
    return iot_hub

