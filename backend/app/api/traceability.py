"""QR Code Traceability API - Complete product journey tracking"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/traceability", tags=["Traceability & QR"])


class QRTraceResponse(BaseModel):
    """Complete traceability response"""
    qr_code: str
    trace_type: str  # product or material
    digital_birth_certificate: Dict[str, Any]
    production_history: Dict[str, Any]
    materials_used: List[Dict[str, Any]]
    quality_checks: List[Dict[str, Any]]
    journey: List[Dict[str, Any]]
    environmental_impact: Dict[str, Any]


class QRGenerateRequest(BaseModel):
    """Request to generate QR code for product"""
    product_code: str
    serial_number: str
    machine_id: str
    production_order_id: Optional[str] = None


@router.get("/trace/{qr_code}", response_model=Dict[str, Any])
async def trace_by_qr_code(
    qr_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🔍 Tra cứu toàn bộ lịch sử sản phẩm qua QR code
    
    **Features:**
    - Complete journey từ receiving → shipping
    - Material traceability (upstream)
    - Quality inspection history
    - Environmental impact (energy, carbon)
    - Digital Birth Certificate
    
    **Example:** 
    - QR Code: `PRD-20250113-ABC789`
    - Returns: Full product lifecycle data
    """
    
    # Check if QR is for product or material
    if qr_code.startswith("PRD-"):
        return await _trace_product(qr_code, db)
    elif qr_code.startswith("MAT-"):
        return await _trace_material(qr_code, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code not found or invalid format: {qr_code}"
        )


async def _trace_product(qr_code: str, db: Session) -> Dict[str, Any]:
    """Trace product with complete history"""
    
    # Query product
    product_query = text("""
        SELECT p.*, po.order_number, m.machine_code, m.machine_type
        FROM products p
        LEFT JOIN production_orders po ON p.production_order_id = po.id
        LEFT JOIN machines m ON p.machine_id = m.id
        WHERE p.qr_code = :qr_code
    """)
    
    result = db.execute(product_query, {"qr_code": qr_code}).fetchone()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with QR code {qr_code} not found"
        )
    
    # Get journey from inventory_transactions
    journey_query = text("""
        SELECT transaction_type, location, timestamp, scanned_by_robot, metadata
        FROM inventory_transactions
        WHERE qr_code = :qr_code
        ORDER BY timestamp ASC
    """)
    
    journey_results = db.execute(journey_query, {"qr_code": qr_code}).fetchall()
    
    # Map transaction types to journey steps
    step_mapping = {
        "material_received": {"step": "Receiving", "icon": "📦"},
        "material_consumed": {"step": "Warehousing", "icon": "🏭"},
        "product_manufactured": {"step": "Machining", "icon": "⚙️"},
        "quality_inspected": {"step": "QC", "icon": "✓"},
        "product_shipped": {"step": "Shipping", "icon": "🚚"}
    }
    
    journey = []
    for row in journey_results:
        step_info = step_mapping.get(row[0], {"step": row[0], "icon": "📍"})
        journey.append({
            "step": step_info["step"],
            "icon": step_info["icon"],
            "location": row[1],
            "timestamp": row[2].isoformat() if row[2] else None,
            "scanned_by": row[3],
            "metadata": row[4]
        })
    
    # Build Digital Birth Certificate
    digital_birth_certificate = {
        "qr_code": qr_code,
        "born_at": result[6].isoformat() if result[6] else None,  # manufactured_at
        "birthplace": {
            "machine": f"{result[11]} ({result[12]})",  # machine_code, machine_type
            "production_order": result[9],  # order_number
            "factory": "Genesis Factory 01"
        },
        "dna": {
            "product_code": result[2],  # product_code
            "serial_number": result[3],  # serial_number
            "quality_status": result[5]  # quality_status
        },
        "health_records": [
            {
                "checkup": "Quality Inspection",
                "result": result[5],  # quality_status
                "date": result[7].isoformat() if result[7] else None,  # inspected_at
                "defects": result[6] if result[6] else []  # defect_types
            }
        ]
    }
    
    # Calculate environmental impact (mock for now)
    environmental_impact = {
        "energy_consumed_kwh": 0.5,
        "carbon_footprint_kg": 0.25,
        "water_used_liters": 2.5,
        "waste_generated_kg": 0.05
    }
    
    return {
        "qr_code": qr_code,
        "trace_type": "product",
        "digital_birth_certificate": digital_birth_certificate,
        "journey": journey,
        "environmental_impact": environmental_impact,
        "production_history": {
            "machine_id": str(result[4]) if result[4] else None,
            "machine_code": result[11],
            "machine_type": result[12],
            "production_order": result[9],
            "manufactured_at": result[6].isoformat() if result[6] else None
        },
        "quality_status": result[5],
        "total_steps": len(journey),
        "current_location": journey[-1]["location"] if journey else "Unknown"
    }


async def _trace_material(qr_code: str, db: Session) -> Dict[str, Any]:
    """Trace material with usage history"""
    
    # Query material transactions
    material_query = text("""
        SELECT it.*, m.name as material_name, m.material_code, s.name as supplier_name
        FROM inventory_transactions it
        LEFT JOIN materials m ON it.material_id = m.id
        LEFT JOIN suppliers s ON m.supplier_id = s.id
        WHERE it.qr_code = :qr_code
        ORDER BY it.timestamp ASC
    """)
    
    results = db.execute(material_query, {"qr_code": qr_code}).fetchall()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with QR code {qr_code} not found"
        )
    
    # Build journey
    journey = []
    for row in results:
        journey.append({
            "transaction_type": row[2],  # transaction_type
            "quantity": row[3],
            "location": row[6],
            "timestamp": row[7].isoformat() if row[7] else None,
            "scanned_by": row[5]
        })
    
    return {
        "qr_code": qr_code,
        "trace_type": "material",
        "material_info": {
            "material_code": results[0][10] if len(results) > 0 else None,
            "material_name": results[0][9] if len(results) > 0 else None,
            "supplier": results[0][11] if len(results) > 0 else None
        },
        "journey": journey,
        "total_transactions": len(journey)
    }


@router.post("/generate-qr", response_model=Dict[str, str])
async def generate_qr_code(
    request: QRGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🏭 Generate QR code cho sản phẩm mới
    
    **Auto-generates:**
    - Unique QR code: PRD-YYYYMMDD-XXXXXX
    - Creates product record in database
    - Links to production order & machine
    """
    import random
    import string
    from datetime import datetime
    
    # Generate QR code
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    qr_code = f"PRD-{date_part}-{random_part}"
    
    # Insert product (simplified - would use ORM models)
    insert_query = text("""
        INSERT INTO products (product_code, serial_number, qr_code, machine_id, manufactured_at)
        VALUES (:product_code, :serial_number, :qr_code, 
                (SELECT id FROM machines WHERE machine_code = :machine_id LIMIT 1),
                NOW())
        RETURNING id
    """)
    
    try:
        result = db.execute(insert_query, {
            "product_code": request.product_code,
            "serial_number": request.serial_number,
            "qr_code": qr_code,
            "machine_id": request.machine_id
        })
        db.commit()
        
        return {
            "qr_code": qr_code,
            "product_code": request.product_code,
            "serial_number": request.serial_number,
            "message": "QR code generated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {str(e)}"
        )


@router.get("/qr-image/{qr_code}")
async def get_qr_code_image(
    qr_code: str,
    size: int = 300
):
    """
    📱 Generate QR code image
    
    Returns PNG image of QR code for printing/display
    """
    try:
        import qrcode
        from io import BytesIO
        from fastapi.responses import StreamingResponse
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size))
        
        # Convert to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")
        
    except ImportError:
        # If qrcode library not installed, return mock response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="QR code generation requires 'qrcode' library. Install with: pip install qrcode[pil]"
        )

