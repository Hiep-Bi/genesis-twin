"""Production Workflow Service

Quản lý quy trình sản xuất 7 bước:
1. Nhập linh kiện (Receiving)
2. Gia công (Machining)
3. Rửa (Washing)
4. Lắp giáp (Assembly) - QC ở đây
5. Đóng hàng (Packaging)
6. Gửi hàng (Shipping)

Giải quyết: Track toàn bộ journey của sản phẩm qua 7 bước
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

logger = logging.getLogger(__name__)


class ProductionWorkflowService:
    """
    🏭 Production Workflow Management
    
    Quản lý quy trình 7 bước sản xuất:
    1. Receiving (Nhập linh kiện)
    2. Machining (Gia công)
    3. Washing (Rửa)
    4. Assembly (Lắp giáp) - QC checkpoint
    5. Packaging (Đóng hàng)
    6. Shipping (Gửi hàng)
    """
    
    WORKFLOW_STEPS = [
        {"step": 1, "name": "receiving", "display_name": "Nhập linh kiện", "icon": "📦"},
        {"step": 2, "name": "machining", "display_name": "Gia công", "icon": "⚙️"},
        {"step": 3, "name": "washing", "display_name": "Rửa", "icon": "💧"},
        {"step": 4, "name": "assembly", "display_name": "Lắp giáp", "icon": "🔧", "qc_checkpoint": True},
        {"step": 5, "name": "packaging", "display_name": "Đóng hàng", "icon": "📦"},
        {"step": 6, "name": "shipping", "display_name": "Gửi hàng", "icon": "🚚"}
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    async def track_product_journey(
        self,
        qr_code: str
    ) -> Dict[str, Any]:
        """
        Track journey của sản phẩm qua 7 bước
        
        Args:
            qr_code: QR code của sản phẩm
        
        Returns:
            Journey với status của từng bước
        """
        
        # Query product
        product_query = text("""
            SELECT 
                p.id,
                p.product_code,
                p.serial_number,
                p.quality_status,
                p.manufactured_at,
                p.inspected_at,
                p.shipped_at,
                po.order_number
            FROM products p
            LEFT JOIN production_orders po ON p.production_order_id = po.id
            WHERE p.qr_code = :qr_code
        """)
        
        product = self.db.execute(product_query, {"qr_code": qr_code}).fetchone()
        
        if not product:
            return {
                "status": "not_found",
                "message": f"Product with QR code {qr_code} not found"
            }
        
        # Query workflow steps từ inventory_transactions
        workflow_query = text("""
            SELECT 
                transaction_type,
                location,
                timestamp,
                scanned_by_robot,
                metadata
            FROM inventory_transactions
            WHERE qr_code = :qr_code
            ORDER BY timestamp ASC
        """)
        
        transactions = self.db.execute(workflow_query, {"qr_code": qr_code}).fetchall()
        
        # Map transactions to workflow steps
        journey = []
        current_step = 0
        
        for transaction in transactions:
            trans_type = transaction[0]
            location = transaction[1]
            timestamp = transaction[2]
            scanned_by = transaction[3]
            metadata = transaction[4]
            
            # Map transaction type to workflow step
            step_mapping = {
                "material_received": 1,  # Receiving
                "material_consumed": 2,   # Machining
                "product_manufactured": 2,  # Machining
                "washing_completed": 3,  # Washing
                "assembly_started": 4,   # Assembly
                "quality_inspected": 4,  # Assembly (QC)
                "packaging_completed": 5,  # Packaging
                "product_shipped": 6     # Shipping
            }
            
            step_num = step_mapping.get(trans_type, 0)
            
            if step_num > current_step:
                current_step = step_num
                step_info = self.WORKFLOW_STEPS[step_num - 1]
                
                journey.append({
                    "step": step_num,
                    "step_name": step_info["name"],
                    "display_name": step_info["display_name"],
                    "icon": step_info["icon"],
                    "status": "completed",
                    "location": location,
                    "timestamp": timestamp.isoformat() if timestamp else None,
                    "scanned_by": scanned_by,
                    "is_qc_checkpoint": step_info.get("qc_checkpoint", False),
                    "metadata": metadata
                })
        
        # Fill in missing steps
        completed_steps = {item["step"] for item in journey}
        for step_info in self.WORKFLOW_STEPS:
            if step_info["step"] not in completed_steps:
                journey.append({
                    "step": step_info["step"],
                    "step_name": step_info["name"],
                    "display_name": step_info["display_name"],
                    "icon": step_info["icon"],
                    "status": "pending",
                    "is_qc_checkpoint": step_info.get("qc_checkpoint", False)
                })
        
        # Sort by step number
        journey.sort(key=lambda x: x["step"])
        
        # Calculate progress
        completed_count = sum(1 for item in journey if item["status"] == "completed")
        progress_percent = (completed_count / len(self.WORKFLOW_STEPS)) * 100
        
        # Check QC status
        qc_step = next(
            (item for item in journey if item.get("is_qc_checkpoint")),
            None
        )
        qc_status = "pending"
        if qc_step and qc_step["status"] == "completed":
            qc_status = product[3] if product else "pending"  # quality_status
        
        return {
            "status": "success",
            "product": {
                "qr_code": qr_code,
                "product_code": product[1],
                "serial_number": product[2],
                "order_number": product[7]
            },
            "journey": journey,
            "progress": {
                "completed_steps": completed_count,
                "total_steps": len(self.WORKFLOW_STEPS),
                "progress_percent": progress_percent,
                "current_step": max((item["step"] for item in journey if item["status"] == "completed"), default=0)
            },
            "qc_status": {
                "step": 4,
                "status": qc_status,
                "inspected_at": product[5].isoformat() if product[5] else None
            }
        }
    
    async def record_workflow_step(
        self,
        qr_code: str,
        step_name: str,
        location: str,
        quality_status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ghi nhận completion của một workflow step
        
        Args:
            qr_code: QR code của sản phẩm
            step_name: Tên bước (receiving, machining, washing, assembly, packaging, shipping)
            location: Vị trí thực hiện
            quality_status: Trạng thái QC (nếu là bước assembly)
            metadata: Thông tin bổ sung
        """
        
        # Map step name to transaction type
        transaction_type_map = {
            "receiving": "material_received",
            "machining": "product_manufactured",
            "washing": "washing_completed",
            "assembly": "assembly_started",
            "packaging": "packaging_completed",
            "shipping": "product_shipped"
        }
        
        transaction_type = transaction_type_map.get(step_name)
        if not transaction_type:
            return {
                "status": "error",
                "message": f"Invalid step name: {step_name}"
            }
        
        # Get product ID
        product_query = text("SELECT id FROM products WHERE qr_code = :qr_code")
        product = self.db.execute(product_query, {"qr_code": qr_code}).fetchone()
        
        if not product:
            return {
                "status": "error",
                "message": f"Product with QR code {qr_code} not found"
            }
        
        # Insert transaction
        insert_query = text("""
            INSERT INTO inventory_transactions (
                material_id,
                transaction_type,
                quantity,
                location,
                qr_code,
                scanned_by_robot,
                metadata,
                timestamp
            ) VALUES (
                NULL,
                :transaction_type,
                1,
                :location,
                :qr_code,
                'SYSTEM',
                :metadata::jsonb,
                NOW()
            )
            RETURNING id
        """)
        
        result = self.db.execute(
            insert_query,
            {
                "transaction_type": transaction_type,
                "location": location,
                "qr_code": qr_code,
                "metadata": str(metadata) if metadata else None
            }
        ).fetchone()
        
        # Update product quality status nếu là QC step
        if step_name == "assembly" and quality_status:
            update_query = text("""
                UPDATE products
                SET quality_status = :quality_status,
                    inspected_at = NOW()
                WHERE qr_code = :qr_code
            """)
            self.db.execute(
                update_query,
                {"quality_status": quality_status, "qr_code": qr_code}
            )
        
        # Update shipped_at nếu là shipping step
        if step_name == "shipping":
            update_query = text("""
                UPDATE products
                SET shipped_at = NOW()
                WHERE qr_code = :qr_code
            """)
            self.db.execute(update_query, {"qr_code": qr_code})
        
        self.db.commit()
        
        return {
            "status": "success",
            "transaction_id": str(result[0]),
            "step": step_name,
            "message": f"Recorded {step_name} step for product {qr_code}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_workflow_statistics(
        self,
        order_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy thống kê workflow
        
        Args:
            order_number: Mã đơn hàng (None = tất cả)
        """
        
        if order_number:
            filter_clause = "AND po.order_number = :order_number"
            params = {"order_number": order_number}
        else:
            filter_clause = ""
            params = {}
        
        query = text(f"""
            SELECT 
                COUNT(DISTINCT p.id) as total_products,
                COUNT(DISTINCT CASE WHEN p.shipped_at IS NOT NULL THEN p.id END) as shipped_count,
                COUNT(DISTINCT CASE WHEN p.inspected_at IS NOT NULL AND p.quality_status = 'pass' THEN p.id END) as qc_passed,
                COUNT(DISTINCT CASE WHEN p.inspected_at IS NOT NULL AND p.quality_status = 'fail' THEN p.id END) as qc_failed
            FROM products p
            LEFT JOIN production_orders po ON p.production_order_id = po.id
            WHERE 1=1 {filter_clause}
        """)
        
        result = self.db.execute(query, params).fetchone()
        
        total = result[0] or 0
        shipped = result[1] or 0
        qc_passed = result[2] or 0
        qc_failed = result[3] or 0
        
        return {
            "status": "success",
            "statistics": {
                "total_products": total,
                "shipped": shipped,
                "shipped_percent": (shipped / total * 100) if total > 0 else 0,
                "qc_passed": qc_passed,
                "qc_failed": qc_failed,
                "qc_pass_rate": (qc_passed / (qc_passed + qc_failed) * 100) if (qc_passed + qc_failed) > 0 else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }

