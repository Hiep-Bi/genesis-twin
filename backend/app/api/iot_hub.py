"""
IoT Hub API - Gateway endpoint cho sensors
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

from app.core.database import get_db
from app.core.redis_client import redis_client
from app.services.iot_hub import get_iot_hub

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/iot-hub", tags=["IoT Hub"])


class SensorDataInput(BaseModel):
    """Sensor data input"""
    machine_id: str
    machine_type: str
    timestamp: str
    temperature: float
    vibration_level: float
    power_consumption: float
    pressure: float
    material_flow_rate: float
    cycle_time: float
    error_rate: float
    efficiency_score: float
    production_status: int


@router.post("/receive", response_model=Dict[str, Any])
async def receive_sensor_data(
    data: SensorDataInput,
    db: Session = Depends(get_db)
):
    """
    Nhận sensor data từ IoT devices
    
    IoT Hub sẽ:
    1. Validate data (loại bỏ data lỗi)
    2. Aggregate data (tính trung bình)
    3. Chỉ lưu vào DB nếu có thay đổi đáng kể (>=5%)
    4. Forward real-time data cho dashboard
    """
    try:
        hub = get_iot_hub(db, redis_client)
        await hub.receive_sensor_data(data.dict())
        
        return {
            "status": "received",
            "message": "Data received and processed by IoT Hub",
            "machine_id": data.machine_id
        }
    except Exception as e:
        logger.error(f"Error receiving sensor data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process sensor data: {str(e)}"
        )


@router.post("/receive-batch", response_model=Dict[str, Any])
async def receive_sensor_data_batch(
    data_list: List[SensorDataInput],
    db: Session = Depends(get_db)
):
    """
    Nhận nhiều sensor data cùng lúc (batch)
    """
    try:
        hub = get_iot_hub(db, redis_client)
        
        for data in data_list:
            await hub.receive_sensor_data(data.dict())
        
        return {
            "status": "received",
            "message": f"Processed {len(data_list)} sensor data points",
            "processed": len(data_list)
        }
    except Exception as e:
        logger.error(f"Error receiving batch sensor data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch sensor data: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_iot_hub_stats(
    db: Session = Depends(get_db)
):
    """
    Get IoT Hub statistics
    """
    try:
        hub = get_iot_hub(db, redis_client)
        stats = hub.get_stats()
        
        return {
            **stats,
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error getting IoT Hub stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

