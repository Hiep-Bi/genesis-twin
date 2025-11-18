"""AI Predictions API - Advanced defect prediction với reasoning"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Ensure ai-core package can be imported regardless of working directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]
AI_CORE_PATH = PROJECT_ROOT / "ai-core"
if AI_CORE_PATH.exists() and str(AI_CORE_PATH) not in sys.path:
    sys.path.append(str(AI_CORE_PATH))

try:
    from enhanced_gemini_client import enhanced_gemini_client  # type: ignore[attr-defined]
    ENHANCED_GEMINI_SOURCE = "ai-core"
except ModuleNotFoundError:  # pragma: no cover - runtime safeguard
    from app.services.mock_enhanced_gemini_client import (  # type: ignore
        enhanced_gemini_client,
    )

    ENHANCED_GEMINI_SOURCE = "mock"
    logger.warning(
        "enhanced_gemini_client module not found; using mock fallback predictions."
    )

router = APIRouter(prefix="/ai/predictions", tags=["AI Predictions"])


class SensorDataInput(BaseModel):
    """Input data cho AI prediction"""
    timestamp: str
    machine_id: str
    machine_type: str
    temperature: float
    vibration_level: float
    power_consumption: float
    pressure: float
    material_flow_rate: float
    cycle_time: float
    error_rate: float
    downtime: int
    maintenance_flag: int
    efficiency_score: float
    production_status: int


class AdvancedPredictionResponse(BaseModel):
    """Response với advanced reasoning"""
    status: str
    diagnosis: Dict[str, Any]
    maintenance_recommendation: Dict[str, Any]
    scenarios: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: str
    machine_id: str
    machine_type: str


class AIPredictionResponse(BaseModel):
    id: UUID
    prediction_type: str
    target_id: Optional[UUID]
    prediction_data: Dict[str, Any]
    confidence_score: Optional[float]
    actual_outcome: Optional[Dict[str, Any]]
    accuracy: Optional[float]
    created_at: datetime
    prediction_time: Optional[datetime]
    outcome_time: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/history", response_model=List[AIPredictionResponse])
async def list_ai_predictions(
    prediction_type: Optional[str] = Query(None),
    target_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List historical AI predictions
    """
    from app.models.ai_prediction import AIPrediction
    query = db.query(AIPrediction)

    if prediction_type:
        query = query.filter(AIPrediction.prediction_type == prediction_type)
    if target_id:
        query = query.filter(AIPrediction.target_id == target_id)

    predictions = query.offset(skip).limit(limit).all()
    return predictions


@router.get("/history/{prediction_id}", response_model=AIPredictionResponse)
async def get_ai_prediction(
    prediction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single AI prediction by ID
    """
    from app.models.ai_prediction import AIPrediction
    prediction = db.query(AIPrediction).filter(AIPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Prediction not found"
        )
    return prediction


@router.post("/advanced-defect", response_model=Dict[str, Any])
async def predict_defect_advanced(
    data: List[SensorDataInput],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Advanced defect prediction với:
    - Root cause analysis chi tiết
    - Historical pattern matching
    - Multi-scenario planning với cost/carbon analysis
    - Smart scheduling recommendations
    
    **Example Input:**
    ```json
    [
      {
        "timestamp": "2025-03-10 08:00:00",
        "machine_id": "M003",
        "machine_type": "Welder",
        "temperature": 78.30,
        "vibration_level": 2.04,
        "power_consumption": 23.06,
        "pressure": 5.09,
        "material_flow_rate": 20.01,
        "cycle_time": 118.15,
        "error_rate": 0.88,
        "downtime": 0,
        "maintenance_flag": 0,  #trong thực tế sẽ không có chỉ số này phải đi dự đoán 
        "efficiency_score": 11.68,
        "production_status": 0
      },
      {
        "timestamp": "2025-03-10 09:20:00",
        "machine_id": "M003",
        "machine_type": "CNC",
        "temperature": 87.37,
        "vibration_level": 5.90,
        "power_consumption": 26.43,
        "pressure": 5.41,
        "material_flow_rate": 16.58,
        "cycle_time": 115.68,
        "error_rate": 1.0,
        "downtime": 0,
        "maintenance_flag": 1,
        "efficiency_score": 0.0,
        "production_status": 0
      }
    ]
    ```
    """
    
    try:
        results = []
        
        # Try to import rule_base_prediction if available
        try:
            import sys
            from pathlib import Path
            PROJECT_ROOT = Path(__file__).resolve().parents[3]
            AI_CORE_PATH = PROJECT_ROOT / "ai-core"
            if AI_CORE_PATH.exists() and str(AI_CORE_PATH) not in sys.path:
                sys.path.append(str(AI_CORE_PATH))
            from rule_base_prediction import predict
            has_rule_base = True
        except ImportError:
            has_rule_base = False
            logger.warning("rule_base_prediction not available, skipping rule-based filtering")
        
        for sensor_data in data:
            # Convert to dict
            current_data = sensor_data.dict()
            
            # Apply rule-based filtering if available
            if has_rule_base:
                filtered_data = predict(current_data)
            else:
                # If no rule base, treat as potentially abnormal (will go through AI prediction)
                filtered_data = 1
            # Determine status first
            if filtered_data == 0:
                # Normal operation
                result = {
                    "status": "✅ Trạng thái ổn định",
                    "message": f"Thiết bị {sensor_data.machine_type} ({sensor_data.machine_id}) hoạt động bình thường tại thời điểm {sensor_data.timestamp}.",
                    "metrics": {
                        "temperature": sensor_data.temperature,
                        "vibration_level": sensor_data.vibration_level,
                        "efficiency_score": sensor_data.efficiency_score
                    }
                }
            else:
                # Abnormal - run advanced prediction
                prediction = await enhanced_gemini_client.advanced_defect_prediction(
                    current_data,
                    sensor_data.machine_id,
                    sensor_data.machine_type
                )
                
                # Format response
                result = format_advanced_response(prediction, sensor_data)
            
            results.append(result)
        
        return {
            "predictions": results,
            "total_analyzed": len(data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )



def format_advanced_response(prediction: Dict, sensor_data: SensorDataInput) -> Dict:
    """Format response theo yêu cầu của user"""
    
    diag = prediction.get('diagnosis', {})
    reasoning = diag.get('reasoning', {})
    maint = prediction.get('maintenance_recommendation', {})
    scenarios = prediction.get('scenarios', [])
    
    # Build reasoning text
    evidence_text = "\n    ".join(reasoning.get('evidence', []))
    
    # Format response
    response = f""" CẢNH BÁO BẤT THƯỜNG: Phát hiện sự cố trên thiết bị {sensor_data.machine_type} ({sensor_data.machine_id}) tại thời điểm {sensor_data.timestamp}.

    Lịch sử bảo trì gần đây cho thấy chu kỳ trung bình: {maint.get('avg_maintenance_cycle_days', 95)} ngày.

    Dự đoán nguyên nhân có thể là: {diag.get('issue_detected', 'Chưa xác định')}

    Lý do chẩn đoán:
        {evidence_text}
        {reasoning.get('pattern_matching', '')}

    Thời gian dừng máy bảo trì trung bình: {maint.get('estimated_downtime_hours', 7.0):.1f} giờ

    Đề xuất Kế hoạch (Tối ưu hóa):
        {maint.get('optimal_scheduling', {}).get('golden_slot', {}).get('reason', 'Chưa có kế hoạch')}
        {maint.get('optimal_scheduling', {}).get('golden_slot', {}).get('cost_optimization', '')}

    Đề xuất thay thế (Nếu khẩn cấp):
    """
    
    # Add scenarios
    for i, scenario in enumerate(scenarios, 1):
        response += f"\n    - {scenario.get('name', f'Phương án {i}')}: {scenario.get('description', '')}"
        impact = scenario.get('impact', {})
        
        # Format impact
        impact_lines = []
        for key, value in impact.items():
            if isinstance(value, (int, float)):
                impact_lines.append(f"{key}: {value}")
            elif isinstance(value, str):
                impact_lines.append(f"{key}: {value}")
        
        if impact_lines:
            response += "\n      Hậu quả: " + ", ".join(impact_lines)
    
    # Add recommendations
    response += "\n\n Các hành động khuyến nghị:"
    for rec in prediction.get('recommendations', []):
        response += f"\n    {rec}"
    
    return {
        "status": "warning",
        "result": response,
        "detailed_analysis": prediction,
        "confidence": diag.get('confidence', 0.0)
    }


@router.get("/test", response_model=Dict[str, str])
async def test_ai_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Test endpoint để kiểm tra AI service"""
    return {
        "status": "ok",
        "message": "AI Predictions API is running",
        "user": current_user.username
    }

