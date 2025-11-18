"""
MLOps API - Model Retraining & Evaluation
Endpoints cho retraining, evaluation, và model management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import sys
import os
import logging

# Add ai-core to path (absolute)
AI_CORE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ai-core"))
if AI_CORE_PATH not in sys.path:
    sys.path.append(AI_CORE_PATH)

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user

try:
    from mlops_retrain import ModelRetrainer
    from model_evaluator import ModelEvaluator
except ModuleNotFoundError as mlops_err:
    logger.warning("MLOps dependencies not found (%s). Endpoints will raise 503.", mlops_err)

    class ModelRetrainer:  # type: ignore
        def retrain(self, *args, **kwargs):
            raise RuntimeError("MLOps dependencies not installed inside backend container.")

        def get_model_info(self):
            return {"version": 0, "metrics": {}, "trained_at": "unknown"}

    class ModelEvaluator:  # type: ignore
        def evaluate(self, *args, **kwargs):
            raise RuntimeError("MLOps dependencies not installed inside backend container.")

        def generate_report(self, *args, **kwargs):
            return "MLOps not available"

router = APIRouter(prefix="/mlops", tags=["MLOps"])


class RetrainRequest(BaseModel):
    """Request để retrain model"""
    model_type: str = "random_forest"  # "random_forest" or "gradient_boosting"
    min_improvement: float = 0.02  # Minimum 2% improvement to deploy


class EvaluationRequest(BaseModel):
    """Request để evaluate model"""
    test_data: List[Dict[str, Any]]  # Test data với features và labels


@router.post("/retrain", response_model=Dict[str, Any])
async def retrain_model(
    request: RetrainRequest = RetrainRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔄 Retrain model với data mới
    
    **Logic:**
    1. Load production data từ database
    2. Prepare training data
    3. Train new model
    4. Evaluate và so sánh với model cũ
    5. Deploy nếu tốt hơn (F1 improvement >= 2%)
    
    **Returns:**
    - success: bool
    - deployed: bool
    - metrics: accuracy, precision, recall, F1
    - comparison: so sánh với model cũ
    """
    try:
        # Get production data từ database
        from sqlalchemy import text
        
        # Query sensor data
        query = text("""
            SELECT 
                timestamp, machine_id, machine_type,
                temperature, vibration_level, power_consumption,
                pressure, material_flow_rate, cycle_time,
                error_rate, efficiency_score, production_status
            FROM sensor_readings
            WHERE timestamp >= NOW() - INTERVAL '30 days'
            ORDER BY timestamp DESC
            LIMIT 10000
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        if len(rows) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No production data found. Need at least 100 records."
            )
        
        # Convert to DataFrame
        production_data = pd.DataFrame([
            {
                'timestamp': row[0],
                'machine_id': row[1],
                'machine_type': row[2],
                'temperature': row[3],
                'vibration_level': row[4],
                'power_consumption': row[5],
                'pressure': row[6],
                'material_flow_rate': row[7],
                'cycle_time': row[8],
                'error_rate': row[9],
                'efficiency_score': row[10],
                'production_status': row[11]
            }
            for row in rows
        ])
        
        # Get maintenance data
        maint_query = text("""
            SELECT 
                machine_id, maintenance_date, downtime_hours, maintenance_type
            FROM maintenance_history
            WHERE maintenance_date >= NOW() - INTERVAL '90 days'
        """)
        
        maint_result = db.execute(maint_query)
        maint_rows = maint_result.fetchall()
        
        maintenance_data = None
        if len(maint_rows) > 0:
            maintenance_data = pd.DataFrame([
                {
                    'machine_id': row[0],
                    'maintenance_date': row[1],
                    'downtime_hours': row[2],
                    'maintenance_type': row[3]
                }
                for row in maint_rows
            ])
        
        # Retrain
        retrainer = ModelRetrainer()
        result = retrainer.retrain(
            production_data=production_data,
            maintenance_data=maintenance_data,
            model_type=request.model_type,
            min_improvement=request.min_improvement
        )
        
        return {
            **result,
            'data_info': {
                'production_records': len(production_data),
                'maintenance_records': len(maintenance_data) if maintenance_data is not None else 0,
                'date_range': {
                    'from': production_data['timestamp'].min().isoformat() if 'timestamp' in production_data.columns else None,
                    'to': production_data['timestamp'].max().isoformat() if 'timestamp' in production_data.columns else None
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retraining failed: {str(e)}"
        )


@router.post("/evaluate", response_model=Dict[str, Any])
async def evaluate_model(
    request: EvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📊 Evaluate model với test data
    
    **Input:**
    - test_data: List of dicts với features và labels
    
    **Returns:**
    - metrics: accuracy, precision, recall, F1, ROC-AUC
    - reasoning: Detailed explanations
    - business_impact: Cost analysis
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.test_data)
        
        # Check required columns
        required_features = [
            'temperature', 'vibration_level', 'power_consumption',
            'pressure', 'material_flow_rate', 'cycle_time',
            'error_rate', 'efficiency_score'
        ]
        
        missing = [col for col in required_features if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required features: {missing}"
            )
        
        # Get labels
        if 'label' not in df.columns and 'production_status' not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing label column. Need 'label' or 'production_status'"
            )
        
        y_test = df.get('label', df.get('production_status', None))
        if y_test is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract labels"
            )
        
        # Prepare features
        X_test = df[required_features].copy()
        X_test = X_test.fillna(X_test.mean())
        
        # Evaluate
        evaluator = ModelEvaluator()
        result = evaluator.evaluate(X_test, y_test)
        
        # Generate report
        report = evaluator.generate_report(result)
        
        return {
            **result,
            'report': report,
            'test_size': len(X_test)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.get("/model-info", response_model=Dict[str, Any])
async def get_model_info(
    current_user: User = Depends(get_current_user)
):
    """
    ℹ️ Get current model information
    """
    try:
        retrainer = ModelRetrainer()
        info = retrainer.get_model_info()
        
        return {
            **info,
            'status': 'active',
            'last_updated': info.get('trained_at', 'Unknown')
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}"
        )


@router.post("/upload-data", response_model=Dict[str, Any])
async def upload_training_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    📤 Upload training data (CSV) để retrain
    
    **File format:**
    - CSV với columns: timestamp, machine_id, machine_type, temperature, vibration_level, ...
    - Label column: production_status (0=normal, 1=abnormal)
    """
    try:
        # Read CSV
        df = pd.read_csv(file.file)
        
        # Validate
        required_cols = ['timestamp', 'machine_id', 'temperature', 'vibration_level']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing}"
            )
        
        # Save to data directory
        data_dir = os.path.join(os.path.dirname(__file__), '../../../ai-core/data')
        os.makedirs(data_dir, exist_ok=True)
        
        filename = f"uploaded_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(data_dir, filename)
        df.to_csv(filepath, index=False)
        
        return {
            'success': True,
            'filename': filename,
            'records': len(df),
            'columns': list(df.columns),
            'message': f"Data uploaded successfully. Use /mlops/retrain to train model."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

