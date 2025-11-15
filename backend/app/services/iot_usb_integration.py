"""IoT USB Integration Service

Giải quyết nỗi đau: Máy cũ cần người thủ công chụp thông số đầu ca/cuối ca
→ Hỗ trợ IoT USB device để tự động gửi data lên server

Features:
- Nhận data từ IoT USB devices
- Parse và validate data
- Lưu vào database
- Tích hợp với existing machine monitoring
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

logger = logging.getLogger(__name__)


class IoTUSBIntegrationService:
    """
    🔌 IoT USB Integration Service
    
    Hỗ trợ máy cũ (legacy machines) thu thập dữ liệu tự động:
    - Nhận data từ IoT USB devices
    - Parse và validate
    - Lưu vào database
    - Tích hợp với machine monitoring system
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def receive_iot_data(
        self,
        device_id: str,
        machine_code: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Nhận và xử lý data từ IoT USB device
        
        Args:
            device_id: ID của IoT USB device
            machine_code: Mã máy được kết nối
            data: Dữ liệu từ device (sensor readings, parameters, etc.)
            timestamp: Thời gian ghi nhận (None = now)
        
        Returns:
            Processing result
        """
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # 1. Validate machine exists
        machine_query = text("""
            SELECT id, machine_code, machine_type, status
            FROM machines
            WHERE machine_code = :machine_code
        """)
        
        machine = self.db.execute(machine_query, {"machine_code": machine_code}).fetchone()
        
        if not machine:
            return {
                "status": "error",
                "message": f"Machine {machine_code} not found"
            }
        
        machine_id = machine[0]
        
        # 2. Parse và validate data
        validated_data = await self._validate_iot_data(data, machine_code)
        
        if not validated_data["valid"]:
            return {
                "status": "error",
                "message": "Invalid data format",
                "errors": validated_data["errors"]
            }
        
        # 3. Lưu sensor readings
        sensor_readings = validated_data.get("sensor_readings", [])
        saved_readings = []
        
        for reading in sensor_readings:
            sensor_code = reading.get("sensor_code")
            value = reading.get("value")
            sensor_type = reading.get("sensor_type", "unknown")
            
            # Get or create sensor
            sensor_query = text("""
                SELECT id FROM sensors
                WHERE sensor_code = :sensor_code
            """)
            sensor = self.db.execute(sensor_query, {"sensor_code": sensor_code}).fetchone()
            
            if not sensor:
                # Create sensor
                create_sensor_query = text("""
                    INSERT INTO sensors (
                        machine_id,
                        sensor_code,
                        sensor_type,
                        unit,
                        created_at
                    ) VALUES (
                        :machine_id,
                        :sensor_code,
                        :sensor_type,
                        :unit,
                        NOW()
                    )
                    RETURNING id
                """)
                sensor_result = self.db.execute(
                    create_sensor_query,
                    {
                        "machine_id": machine_id,
                        "sensor_code": sensor_code,
                        "sensor_type": sensor_type,
                        "unit": reading.get("unit", "")
                    }
                ).fetchone()
                sensor_id = sensor_result[0]
            else:
                sensor_id = sensor[0]
            
            # Insert sensor reading
            insert_reading_query = text("""
                INSERT INTO sensor_readings (
                    timestamp,
                    sensor_id,
                    value,
                    quality,
                    anomaly_score
                ) VALUES (
                    :timestamp,
                    :sensor_id,
                    :value,
                    :quality,
                    :anomaly_score
                )
                RETURNING timestamp
            """)
            
            result = self.db.execute(
                insert_reading_query,
                {
                    "timestamp": timestamp,
                    "sensor_id": sensor_id,
                    "value": value,
                    "quality": reading.get("quality", "good"),
                    "anomaly_score": reading.get("anomaly_score", 0.0)
                }
            ).fetchone()
            
            saved_readings.append({
                "sensor_code": sensor_code,
                "value": value,
                "timestamp": result[0].isoformat() if result else timestamp.isoformat()
            })
        
        # 4. Update machine state nếu có
        machine_state = validated_data.get("machine_state")
        if machine_state:
            state_query = text("""
                INSERT INTO machine_states (
                    timestamp,
                    machine_id,
                    status,
                    oee,
                    availability,
                    performance,
                    quality,
                    production_count,
                    defect_count,
                    downtime_minutes
                ) VALUES (
                    :timestamp,
                    :machine_id,
                    :status,
                    :oee,
                    :availability,
                    :performance,
                    :quality,
                    :production_count,
                    :defect_count,
                    :downtime_minutes
                )
            """)
            
            self.db.execute(
                state_query,
                {
                    "timestamp": timestamp,
                    "machine_id": machine_id,
                    "status": machine_state.get("status", "running"),
                    "oee": machine_state.get("oee"),
                    "availability": machine_state.get("availability"),
                    "performance": machine_state.get("performance"),
                    "quality": machine_state.get("quality"),
                    "production_count": machine_state.get("production_count", 0),
                    "defect_count": machine_state.get("defect_count", 0),
                    "downtime_minutes": machine_state.get("downtime_minutes", 0)
                }
            )
        
        # 5. Log IoT device activity
        log_query = text("""
            INSERT INTO audit_logs (
                action,
                resource,
                details,
                timestamp
            ) VALUES (
                'iot_data_received',
                :machine_code,
                :details::jsonb,
                :timestamp
            )
        """)
        
        self.db.execute(
            log_query,
            {
                "machine_code": machine_code,
                "details": json.dumps({
                    "device_id": device_id,
                    "sensor_readings_count": len(saved_readings),
                    "machine_state": machine_state is not None
                }),
                "timestamp": timestamp
            }
        )
        
        self.db.commit()
        
        return {
            "status": "success",
            "device_id": device_id,
            "machine_code": machine_code,
            "sensor_readings_saved": len(saved_readings),
            "readings": saved_readings,
            "machine_state_updated": machine_state is not None,
            "timestamp": timestamp.isoformat()
        }
    
    async def _validate_iot_data(
        self,
        data: Dict[str, Any],
        machine_code: str
    ) -> Dict[str, Any]:
        """Validate và parse IoT data"""
        
        errors = []
        sensor_readings = []
        machine_state = None
        
        # Expected format:
        # {
        #   "sensor_readings": [
        #     {"sensor_code": "TEMP-001", "value": 75.5, "sensor_type": "temperature", "unit": "°C"},
        #     ...
        #   ],
        #   "machine_state": {
        #     "status": "running",
        #     "oee": 0.85,
        #     "production_count": 100,
        #     ...
        #   }
        # }
        
        # Validate sensor_readings
        if "sensor_readings" in data:
            readings = data["sensor_readings"]
            if not isinstance(readings, list):
                errors.append("sensor_readings must be a list")
            else:
                for idx, reading in enumerate(readings):
                    if not isinstance(reading, dict):
                        errors.append(f"sensor_readings[{idx}] must be a dict")
                        continue
                    
                    if "sensor_code" not in reading:
                        errors.append(f"sensor_readings[{idx}] missing sensor_code")
                    if "value" not in reading:
                        errors.append(f"sensor_readings[{idx}] missing value")
                    
                    if "sensor_code" in reading and "value" in reading:
                        sensor_readings.append({
                            "sensor_code": reading["sensor_code"],
                            "value": float(reading["value"]),
                            "sensor_type": reading.get("sensor_type", "unknown"),
                            "unit": reading.get("unit", ""),
                            "quality": reading.get("quality", "good"),
                            "anomaly_score": float(reading.get("anomaly_score", 0.0))
                        })
        
        # Validate machine_state
        if "machine_state" in data:
            state = data["machine_state"]
            if not isinstance(state, dict):
                errors.append("machine_state must be a dict")
            else:
                machine_state = {
                    "status": state.get("status", "running"),
                    "oee": float(state.get("oee", 0.0)) if state.get("oee") else None,
                    "availability": float(state.get("availability", 0.0)) if state.get("availability") else None,
                    "performance": float(state.get("performance", 0.0)) if state.get("performance") else None,
                    "quality": float(state.get("quality", 0.0)) if state.get("quality") else None,
                    "production_count": int(state.get("production_count", 0)),
                    "defect_count": int(state.get("defect_count", 0)),
                    "downtime_minutes": int(state.get("downtime_minutes", 0))
                }
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "sensor_readings": sensor_readings,
            "machine_state": machine_state
        }
    
    async def get_iot_device_status(
        self,
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy trạng thái IoT devices
        
        Args:
            device_id: ID của device (None = tất cả)
        """
        
        query = text("""
            SELECT 
                details->>'device_id' as device_id,
                resource as machine_code,
                MAX(timestamp) as last_seen,
                COUNT(*) as data_points_count
            FROM audit_logs
            WHERE action = 'iot_data_received'
            AND (:device_id IS NULL OR details->>'device_id' = :device_id)
            GROUP BY device_id, resource
            ORDER BY last_seen DESC
        """)
        
        results = self.db.execute(query, {"device_id": device_id}).fetchall()
        
        devices = []
        for row in results:
            last_seen = row[2]
            time_since_last_seen = None
            if last_seen:
                time_since_last_seen = (datetime.utcnow() - last_seen).total_seconds() / 60  # minutes
            
            devices.append({
                "device_id": row[0],
                "machine_code": row[1],
                "last_seen": last_seen.isoformat() if last_seen else None,
                "time_since_last_seen_minutes": time_since_last_seen,
                "data_points_count": row[3],
                "status": (
                    "online" if time_since_last_seen and time_since_last_seen < 10
                    else "offline" if time_since_last_seen and time_since_last_seen > 60
                    else "unknown"
                )
            })
        
        return {
            "status": "success",
            "devices": devices,
            "total_devices": len(devices),
            "online_count": sum(1 for d in devices if d["status"] == "online"),
            "timestamp": datetime.utcnow().isoformat()
        }

