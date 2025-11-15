"""Factory Operations API - Recovery, Inventory, Workflow, AGV Fallback, IoT"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.services.recovery_prioritization import RecoveryPrioritizationService
from app.services.inventory_management import InventoryManagementService
from app.services.production_workflow import ProductionWorkflowService
from app.services.agv_fallback import AGVFallbackService
from app.services.iot_usb_integration import IoTUSBIntegrationService

router = APIRouter(prefix="/factory", tags=["Factory Operations"])


# ============ Production Line Recovery ============

class RecoveryAnalysisRequest(BaseModel):
    affected_lines: List[str]
    agv_server_status: str = "down"  # "up" or "down"
    inventory_status: Optional[Dict[str, Any]] = None


@router.post("/recovery/analyze")
async def analyze_recovery_plan(
    request: RecoveryAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🔄 Production Line Recovery: Phân tích và đề xuất thứ tự khởi động lại dây chuyền
    
    **Giải quyết nỗi đau:** Khi dây chuyền sập, không biết khởi động lại thứ tự nào tối ưu
    
    **Features:**
    - Phân tích tình trạng hiện tại (máy, inventory, đơn hàng)
    - Tính toán priority score cho mỗi dây chuyền
    - Đề xuất recovery sequence với timeline
    - Recommendations dựa trên inventory location
    
    **Example Request:**
    ```json
    {
      "affected_lines": ["LINE-01", "LINE-02", "LINE-03"],
      "agv_server_status": "down",
      "inventory_status": null
    }
    ```
    """
    
    service = RecoveryPrioritizationService(db)
    result = await service.analyze_recovery_plan(
        affected_lines=request.affected_lines,
        agv_server_status=request.agv_server_status,
        inventory_status=request.inventory_status
    )
    
    return result


# ============ Inventory Management ============

@router.get("/inventory/status")
async def get_inventory_status(
    material_codes: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📦 Inventory Status: Lấy trạng thái inventory theo location
    
    **Features:**
    - Breakdown theo kho tổng (main_warehouse) và kho chờ ngoài (external_staging)
    - Summary statistics
    - Material availability
    
    **Query Params:**
    - material_codes: Danh sách mã vật liệu cần check (optional)
    """
    
    service = InventoryManagementService(db)
    result = await service.get_inventory_status(material_codes=material_codes)
    
    return result


@router.get("/inventory/check-availability")
async def check_material_availability(
    material_code: str = Query(...),
    required_quantity: float = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Check Material Availability: Kiểm tra availability của vật liệu ở các location
    
    **Returns:**
    - Availability ở từng location
    - Recommendations (ưu tiên kho chờ ngoài nếu đủ)
    """
    
    service = InventoryManagementService(db)
    result = await service.check_material_availability(
        material_code=material_code,
        required_quantity=required_quantity
    )
    
    return result


class InventoryTransactionRequest(BaseModel):
    material_code: str
    transaction_type: str  # "receive", "consume", "return", "adjust"
    quantity: float
    location: str
    qr_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/inventory/transaction")
async def record_inventory_transaction(
    request: InventoryTransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📝 Record Inventory Transaction: Ghi nhận giao dịch inventory"""
    
    service = InventoryManagementService(db)
    result = await service.record_inventory_transaction(
        material_code=request.material_code,
        transaction_type=request.transaction_type,
        quantity=request.quantity,
        location=request.location,
        qr_code=request.qr_code,
        metadata=request.metadata
    )
    
    return result


# ============ Production Workflow ============

@router.get("/workflow/track/{qr_code}")
async def track_product_journey(
    qr_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🏭 Track Product Journey: Track journey của sản phẩm qua 7 bước
    
    **7 Steps:**
    1. Nhập linh kiện (Receiving)
    2. Gia công (Machining)
    3. Rửa (Washing)
    4. Lắp giáp (Assembly) - QC checkpoint
    5. Đóng hàng (Packaging)
    6. Gửi hàng (Shipping)
    """
    
    service = ProductionWorkflowService(db)
    result = await service.track_product_journey(qr_code=qr_code)
    
    return result


class WorkflowStepRequest(BaseModel):
    qr_code: str
    step_name: str  # "receiving", "machining", "washing", "assembly", "packaging", "shipping"
    location: str
    quality_status: Optional[str] = None  # "pass", "fail", "rework" (for assembly step)
    metadata: Optional[Dict[str, Any]] = None


@router.post("/workflow/record-step")
async def record_workflow_step(
    request: WorkflowStepRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📝 Record Workflow Step: Ghi nhận completion của một workflow step"""
    
    service = ProductionWorkflowService(db)
    result = await service.record_workflow_step(
        qr_code=request.qr_code,
        step_name=request.step_name,
        location=request.location,
        quality_status=request.quality_status,
        metadata=request.metadata
    )
    
    return result


@router.get("/workflow/statistics")
async def get_workflow_statistics(
    order_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Workflow Statistics: Lấy thống kê workflow"""
    
    service = ProductionWorkflowService(db)
    result = await service.get_workflow_statistics(order_number=order_number)
    
    return result


# ============ AGV Fallback ============

class AGVFallbackRequest(BaseModel):
    estimated_recovery_time_minutes: int = 60
    affected_lines: Optional[List[str]] = None


@router.post("/agv-fallback/handle-failure")
async def handle_agv_server_failure(
    request: AGVFallbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🚨 AGV Fallback: Xử lý khi server AGV sập
    
    **Giải quyết nỗi đau:** Server AGV sập → không biết ưu tiên dây chuyền nào
    
    **Features:**
    - Phân tích inventory location (kho tổng vs kho chờ ngoài)
    - Đề xuất ưu tiên dây chuyền dựa trên inventory sẵn có
    - Fallback instructions cho manual coordination
    - Resource requirements analysis
    """
    
    service = AGVFallbackService(db)
    result = await service.handle_agv_server_failure(
        estimated_recovery_time_minutes=request.estimated_recovery_time_minutes,
        affected_lines=request.affected_lines
    )
    
    return result


# ============ IoT USB Integration ============

class IoTDataRequest(BaseModel):
    device_id: str
    machine_code: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None


@router.post("/iot/receive-data")
async def receive_iot_data(
    request: IoTDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🔌 IoT USB Integration: Nhận và xử lý data từ IoT USB device
    
    **Giải quyết nỗi đau:** Máy cũ cần người thủ công chụp thông số đầu ca/cuối ca
    
    **Features:**
    - Nhận data từ IoT USB devices
    - Parse và validate
    - Lưu sensor readings và machine state
    - Tích hợp với existing monitoring
    
    **Example Request:**
    ```json
    {
      "device_id": "IOT-USB-001",
      "machine_code": "MACHINE-OLD-001",
      "data": {
        "sensor_readings": [
          {
            "sensor_code": "TEMP-001",
            "value": 75.5,
            "sensor_type": "temperature",
            "unit": "°C"
          }
        ],
        "machine_state": {
          "status": "running",
          "oee": 0.85,
          "production_count": 100
        }
      }
    }
    ```
    """
    
    from datetime import datetime
    
    service = IoTUSBIntegrationService(db)
    
    timestamp = None
    if request.timestamp:
        timestamp = datetime.fromisoformat(request.timestamp)
    
    result = await service.receive_iot_data(
        device_id=request.device_id,
        machine_code=request.machine_code,
        data=request.data,
        timestamp=timestamp
    )
    
    return result


@router.get("/iot/device-status")
async def get_iot_device_status(
    device_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 IoT Device Status: Lấy trạng thái IoT devices"""
    
    service = IoTUSBIntegrationService(db)
    result = await service.get_iot_device_status(device_id=device_id)
    
    return result

