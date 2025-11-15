"""Inventory Management Service

Quản lý inventory với 2 kho:
- Kho tổng (main_warehouse)
- Kho chờ ngoài (external_staging)

Giải quyết nỗi đau: Khi server AGV sập, cần biết inventory ở đâu để ưu tiên dây chuyền
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class InventoryManagementService:
    """
    📦 Inventory Management System
    
    Quản lý inventory ở 2 vị trí:
    1. Main Warehouse (kho tổng)
    2. External Staging (kho chờ ngoài)
    
    Features:
    - Track inventory theo location
    - Tính toán availability cho production lines
    - Đề xuất ưu tiên dựa trên inventory location
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_inventory_status(
        self,
        material_codes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Lấy trạng thái inventory theo location
        
        Args:
            material_codes: Danh sách mã vật liệu cần check (None = tất cả)
        
        Returns:
            Inventory status với breakdown theo location
        """
        
        if material_codes:
            material_filter = "AND it.material_id IN (SELECT id FROM materials WHERE material_code = ANY(:codes))"
            params = {"codes": material_codes}
        else:
            material_filter = ""
            params = {}
        
        query = text(f"""
            SELECT 
                m.material_code,
                m.name,
                it.location,
                SUM(CASE WHEN it.transaction_type = 'receive' THEN it.quantity ELSE 0 END) -
                SUM(CASE WHEN it.transaction_type = 'consume' THEN it.quantity ELSE 0 END) as available_quantity,
                MAX(it.timestamp) as last_update
            FROM inventory_transactions it
            JOIN materials m ON it.material_id = m.id
            WHERE 1=1 {material_filter}
            GROUP BY m.material_code, m.name, it.location
            HAVING SUM(CASE WHEN it.transaction_type = 'receive' THEN it.quantity ELSE 0 END) -
                   SUM(CASE WHEN it.transaction_type = 'consume' THEN it.quantity ELSE 0 END) > 0
            ORDER BY m.material_code, it.location
        """)
        
        results = self.db.execute(query, params).fetchall()
        
        # Group by location
        inventory_by_location = {
            "main_warehouse": {},
            "external_staging": {},
            "other": {}
        }
        
        for row in results:
            material_code = row[0]
            material_name = row[1]
            location = row[2]
            quantity = float(row[3]) if row[3] else 0
            last_update = row[4]
            
            item = {
                "material_code": material_code,
                "material_name": material_name,
                "quantity": quantity,
                "last_update": last_update.isoformat() if last_update else None
            }
            
            # Phân loại location
            location_lower = location.lower() if location else ""
            if "staging" in location_lower or "external" in location_lower or "ngoài" in location_lower:
                inventory_by_location["external_staging"][material_code] = item
            elif "warehouse" in location_lower or "kho tổng" in location_lower or "main" in location_lower:
                inventory_by_location["main_warehouse"][material_code] = item
            else:
                inventory_by_location["other"][material_code] = item
        
        # Tính tổng
        total_materials = len(set(
            list(inventory_by_location["main_warehouse"].keys()) +
            list(inventory_by_location["external_staging"].keys()) +
            list(inventory_by_location["other"].keys())
        ))
        
        total_quantity_main = sum(
            item["quantity"]
            for item in inventory_by_location["main_warehouse"].values()
        )
        total_quantity_staging = sum(
            item["quantity"]
            for item in inventory_by_location["external_staging"].values()
        )
        
        return {
            "status": "success",
            "inventory_by_location": inventory_by_location,
            "summary": {
                "total_materials": total_materials,
                "main_warehouse": {
                    "materials_count": len(inventory_by_location["main_warehouse"]),
                    "total_quantity": total_quantity_main
                },
                "external_staging": {
                    "materials_count": len(inventory_by_location["external_staging"]),
                    "total_quantity": total_quantity_staging
                },
                "other": {
                    "materials_count": len(inventory_by_location["other"])
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def check_material_availability(
        self,
        material_code: str,
        required_quantity: float
    ) -> Dict[str, Any]:
        """
        Kiểm tra availability của vật liệu ở các location
        
        Returns:
            Availability info với recommendations
        """
        
        query = text("""
            SELECT 
                it.location,
                SUM(CASE WHEN it.transaction_type = 'receive' THEN it.quantity ELSE 0 END) -
                SUM(CASE WHEN it.transaction_type = 'consume' THEN it.quantity ELSE 0 END) as available_quantity
            FROM inventory_transactions it
            JOIN materials m ON it.material_id = m.id
            WHERE m.material_code = :material_code
            GROUP BY it.location
            HAVING SUM(CASE WHEN it.transaction_type = 'receive' THEN it.quantity ELSE 0 END) -
                   SUM(CASE WHEN it.transaction_type = 'consume' THEN it.quantity ELSE 0 END) > 0
        """)
        
        results = self.db.execute(query, {"material_code": material_code}).fetchall()
        
        availability = {}
        total_available = 0
        
        for row in results:
            location = row[0]
            quantity = float(row[1]) if row[1] else 0
            total_available += quantity
            
            location_type = "other"
            if "staging" in location.lower() or "external" in location.lower():
                location_type = "external_staging"
            elif "warehouse" in location.lower() or "main" in location.lower():
                location_type = "main_warehouse"
            
            availability[location] = {
                "location": location,
                "location_type": location_type,
                "available_quantity": quantity,
                "sufficient": quantity >= required_quantity
            }
        
        # Recommendations
        recommendations = []
        
        if total_available < required_quantity:
            recommendations.append({
                "type": "warning",
                "message": f"Insufficient inventory: {total_available} < {required_quantity}",
                "action": "Cần nhập thêm vật liệu hoặc điều chỉnh production plan"
            })
        else:
            # Ưu tiên kho chờ ngoài nếu đủ
            staging_available = sum(
                item["available_quantity"]
                for item in availability.values()
                if item["location_type"] == "external_staging"
            )
            
            if staging_available >= required_quantity:
                recommendations.append({
                    "type": "info",
                    "message": "Đủ inventory ở kho chờ ngoài",
                    "action": "Ưu tiên sử dụng kho chờ ngoài (gần production line hơn)"
                })
            else:
                recommendations.append({
                    "type": "info",
                    "message": "Cần kết hợp inventory từ cả 2 kho",
                    "action": "Sử dụng kho chờ ngoài trước, sau đó bổ sung từ kho tổng"
                })
        
        return {
            "material_code": material_code,
            "required_quantity": required_quantity,
            "total_available": total_available,
            "sufficient": total_available >= required_quantity,
            "availability_by_location": availability,
            "recommendations": recommendations
        }
    
    async def record_inventory_transaction(
        self,
        material_code: str,
        transaction_type: str,  # "receive", "consume", "return", "adjust"
        quantity: float,
        location: str,
        qr_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ghi nhận giao dịch inventory
        
        Args:
            material_code: Mã vật liệu
            transaction_type: Loại giao dịch
            quantity: Số lượng
            location: Vị trí (main_warehouse, external_staging, etc.)
            qr_code: QR code nếu có
            metadata: Thông tin bổ sung
        """
        
        # Get material ID
        material_query = text("SELECT id FROM materials WHERE material_code = :code")
        material_result = self.db.execute(material_query, {"code": material_code}).fetchone()
        
        if not material_result:
            return {
                "status": "error",
                "message": f"Material {material_code} not found"
            }
        
        material_id = material_result[0]
        
        # Insert transaction
        insert_query = text("""
            INSERT INTO inventory_transactions (
                material_id,
                transaction_type,
                quantity,
                location,
                qr_code,
                metadata,
                timestamp
            ) VALUES (
                :material_id,
                :transaction_type,
                :quantity,
                :location,
                :qr_code,
                :metadata::jsonb,
                NOW()
            )
            RETURNING id
        """)
        
        result = self.db.execute(
            insert_query,
            {
                "material_id": material_id,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "location": location,
                "qr_code": qr_code,
                "metadata": str(metadata) if metadata else None
            }
        ).fetchone()
        
        self.db.commit()
        
        return {
            "status": "success",
            "transaction_id": str(result[0]),
            "message": f"Recorded {transaction_type} of {quantity} {material_code} at {location}",
            "timestamp": datetime.utcnow().isoformat()
        }

