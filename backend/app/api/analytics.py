"""Analytics endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, List, Any
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class DashboardMetrics(BaseModel):
    """Dashboard KPIs"""
    oee: float
    energy_consumption_kwh: float
    carbon_emissions_kg: float
    production_count: int
    defect_count: int
    machines_running: int
    machines_total: int


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time dashboard metrics"""
    
    # Try cache first
    cache_key = "dashboard:metrics:realtime"
    cached = redis_client.get(cache_key)
    if cached:
        return cached
    
    # Calculate metrics from database
    metrics = {
        "oee": 85.5,  # Mock data - would calculate from machine_states
        "energy_consumption_kwh": 1234.5,
        "carbon_emissions_kg": 456.7,
        "production_count": 1000,
        "defect_count": 25,
        "machines_running": 35,
        "machines_total": 50
    }
    
    # Cache for 10 seconds
    redis_client.set(cache_key, metrics, ttl=10)
    
    return metrics


@router.get("/energy/trend")
async def get_energy_trend(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get energy consumption trend"""
    # Mock data - would query from energy_consumption table
    return {
        "labels": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
        "data": [120.5, 98.3, 145.7, 178.2, 156.4, 132.8],
        "unit": "kWh"
    }


@router.get("/production/oee")
async def get_oee_by_machine(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get OEE by machine"""
    # Mock data
    return [
        {"machine_code": "CNC-001", "oee": 87.5},
        {"machine_code": "CNC-002", "oee": 92.3},
        {"machine_code": "ROBOT-001", "oee": 78.9},
        {"machine_code": "AGV-001", "oee": 95.1}
    ]

