"""AGV Fallback System

Giải quyết nỗi đau: Khi server AGV sập, hệ thống vẫn có thể:
1. Đề xuất ưu tiên dây chuyền dựa trên inventory location
2. Sử dụng inventory từ kho chờ ngoài trước
3. Fallback mode với manual coordination
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class AGVFallbackService:
    """
    🚨 AGV Fallback & Recovery System
    
    Khi server AGV sập:
    1. Phân tích inventory location (kho tổng vs kho chờ ngoài)
    2. Đề xuất ưu tiên dây chuyền dựa trên inventory sẵn có
    3. Tính toán thời gian recovery và resource requirements
    4. Fallback mode: Manual coordination instructions
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def handle_agv_server_failure(
        self,
        estimated_recovery_time_minutes: int = 60,
        affected_lines: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Xử lý khi server AGV sập
        
        Args:
            estimated_recovery_time_minutes: Thời gian ước tính khôi phục server
            affected_lines: Danh sách dây chuyền bị ảnh hưởng (None = tất cả)
        
        Returns:
            Fallback plan với recommendations
        """
        
        # 1. Phân tích inventory status
        from app.services.inventory_management import InventoryManagementService
        inventory_service = InventoryManagementService(self.db)
        inventory_status = await inventory_service.get_inventory_status()
        
        # 2. Phân tích production orders đang chờ
        orders_query = text("""
            SELECT 
                po.order_number,
                po.product_code,
                po.quantity,
                po.priority,
                po.scheduled_end
            FROM production_orders po
            WHERE po.status IN ('pending', 'in_progress')
            ORDER BY po.priority DESC, po.scheduled_end ASC
        """)
        
        orders = self.db.execute(orders_query).fetchall()
        
        # 3. Tính toán ưu tiên dựa trên inventory location
        prioritized_lines = await self._prioritize_lines_by_inventory(
            orders,
            inventory_status,
            affected_lines
        )
        
        # 4. Tính toán resource requirements
        resource_analysis = await self._analyze_resource_requirements(
            prioritized_lines,
            inventory_status,
            estimated_recovery_time_minutes
        )
        
        # 5. Tạo fallback instructions
        fallback_instructions = await self._generate_fallback_instructions(
            prioritized_lines,
            inventory_status,
            estimated_recovery_time_minutes
        )
        
        return {
            "status": "fallback_plan_ready",
            "agv_server_status": "down",
            "estimated_recovery_time_minutes": estimated_recovery_time_minutes,
            "inventory_analysis": {
                "main_warehouse": inventory_status["summary"]["main_warehouse"],
                "external_staging": inventory_status["summary"]["external_staging"],
                "recommendation": "Ưu tiên sử dụng inventory từ kho chờ ngoài trước"
            },
            "prioritized_lines": prioritized_lines,
            "resource_requirements": resource_analysis,
            "fallback_instructions": fallback_instructions,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _prioritize_lines_by_inventory(
        self,
        orders: List,
        inventory_status: Dict[str, Any],
        affected_lines: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Ưu tiên dây chuyền dựa trên inventory location"""
        
        line_priorities = []
        
        # Group orders by production line (sử dụng config table)
        lines = {}
        for order in orders:
            product_code = order[1]
            line_code = await self._get_line_code_from_product(product_code)
            
            if affected_lines and line_code not in affected_lines:
                continue
            
            if line_code not in lines:
                lines[line_code] = {
                    "line_code": line_code,
                    "orders": [],
                    "total_quantity": 0,
                    "max_priority": 0
                }
            
            lines[line_code]["orders"].append({
                "order_number": order[0],
                "product_code": order[1],
                "quantity": order[2],
                "priority": order[3],
                "deadline": order[4].isoformat() if order[4] else None
            })
            lines[line_code]["total_quantity"] += order[2]
            lines[line_code]["max_priority"] = max(
                lines[line_code]["max_priority"],
                order[3]
            )
        
        # Tính priority score cho mỗi line (sử dụng config table)
        for line_code, line_data in lines.items():
            score = 0
            reasons = []
            
            # 1. Priority của đơn hàng (0-40 điểm)
            score += line_data["max_priority"] * 4
            reasons.append(
                f"Priority: {line_data['max_priority']}, "
                f"{len(line_data['orders'])} đơn hàng, "
                f"{line_data['total_quantity']} sản phẩm"
            )
            
            # 2. Inventory ở kho chờ ngoài (0-40 điểm) - QUAN TRỌNG NHẤT
            # Sử dụng config table để check material availability
            material_availability = await self._check_line_material_availability(
                line_code,
                inventory_status
            )
            
            if material_availability["has_external_inventory"]:
                score += 40
                reasons.append(
                    f"✅ Có inventory ở kho chờ ngoài "
                    f"({material_availability['available_materials_count']}/{material_availability['total_materials_count']} vật liệu) - "
                    f"Ưu tiên cao vì không cần AGV từ kho tổng"
                )
            elif material_availability["all_materials_available"]:
                score += 20
                reasons.append(
                    f"⚠️ Chỉ có inventory ở kho tổng "
                    f"({material_availability['available_materials_count']}/{material_availability['total_materials_count']} vật liệu) - "
                    f"Cần AGV nhưng server đang sập"
                )
            elif not material_availability["critical_materials_available"]:
                score -= 20  # Penalty lớn nếu thiếu critical materials
                reasons.append(
                    f"❌ Thiếu critical materials - không thể khởi động"
                )
            
            # 3. Deadline urgency (0-20 điểm)
            urgent_orders = [
                o for o in line_data["orders"]
                if o.get("deadline") and
                datetime.fromisoformat(o["deadline"]) < datetime.utcnow() + timedelta(days=1)
            ]
            if urgent_orders:
                score += 20
                reasons.append(f"{len(urgent_orders)} đơn hàng gấp (deadline < 24h)")
            
            line_priorities.append({
                "line_code": line_code,
                "priority_score": score,
                "reasons": reasons,
                "orders_count": len(line_data["orders"]),
                "total_quantity": line_data["total_quantity"],
                "has_external_inventory": material_availability["has_external_inventory"],
                "material_availability": material_availability,
                "recommendation": (
                    "✅ Khởi động ngay (có inventory ở kho chờ ngoài)"
                    if material_availability["has_external_inventory"]
                    else "⚠️ Chờ AGV recovery hoặc manual transport"
                    if material_availability["all_materials_available"]
                    else "❌ Không thể khởi động (thiếu critical materials)"
                )
            })
        
        # Sắp xếp theo priority score
        line_priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return line_priorities
    
    async def _get_line_code_from_product(self, product_code: str) -> Optional[str]:
        """Get line code from product code using config table"""
        query = text("""
            SELECT line_code
            FROM production_line_mapping
            WHERE :product_code LIKE REPLACE(product_code_pattern, '*', '%')
            ORDER BY LENGTH(product_code_pattern) DESC
            LIMIT 1
        """)
        
        result = self.db.execute(query, {"product_code": product_code}).fetchone()
        if result:
            return result[0]
        
        # Fallback: simplified parsing
        parts = product_code.split("-")
        for part in parts:
            if "line" in part.lower():
                return part.upper()
        return parts[0] if parts else "LINE-UNKNOWN"
    
    async def _check_line_material_availability(
        self,
        line_code: str,
        inventory_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check material availability for a line using config table"""
        query = text("""
            SELECT 
                lmr.material_code,
                lmr.required_quantity_per_unit,
                lmr.is_critical,
                lmr.preferred_location
            FROM line_material_requirements lmr
            WHERE lmr.line_code = :line_code
        """)
        
        requirements = self.db.execute(query, {"line_code": line_code}).fetchall()
        
        external_staging = inventory_status.get("inventory_by_location", {}).get("external_staging", {})
        main_warehouse = inventory_status.get("inventory_by_location", {}).get("main_warehouse", {})
        
        available_materials = []
        critical_materials_available = True
        has_external = False
        
        for req in requirements:
            material_code = req[0]
            required_qty = req[1]
            is_critical = req[2]
            preferred = req[3]
            
            # Check availability
            available = False
            location = None
            
            if preferred == "external_staging" and material_code in external_staging:
                available_qty = external_staging[material_code].get("quantity", 0)
                if available_qty >= required_qty:
                    available = True
                    location = "external_staging"
                    has_external = True
            elif material_code in main_warehouse:
                available_qty = main_warehouse[material_code].get("quantity", 0)
                if available_qty >= required_qty:
                    available = True
                    location = "main_warehouse"
            
            if available:
                available_materials.append(material_code)
            elif is_critical:
                critical_materials_available = False
        
        return {
            "has_external_inventory": has_external,
            "all_materials_available": len(available_materials) == len(requirements),
            "critical_materials_available": critical_materials_available,
            "available_materials_count": len(available_materials),
            "total_materials_count": len(requirements)
        }
    
    async def _analyze_resource_requirements(
        self,
        prioritized_lines: List[Dict[str, Any]],
        inventory_status: Dict[str, Any],
        recovery_time_minutes: int
    ) -> Dict[str, Any]:
        """Phân tích resource requirements"""
        
        lines_with_external_inventory = [
            line for line in prioritized_lines
            if line["has_external_inventory"]
        ]
        
        lines_needing_agv = [
            line for line in prioritized_lines
            if not line["has_external_inventory"]
        ]
        
        return {
            "lines_can_start_immediately": len(lines_with_external_inventory),
            "lines_need_agv": len(lines_needing_agv),
            "estimated_manual_transport_time": (
                len(lines_needing_agv) * 30  # 30 phút per line
            ),
            "recommendation": (
                f"Khởi động {len(lines_with_external_inventory)} dây chuyền ngay "
                f"(có inventory sẵn). "
                f"{len(lines_needing_agv)} dây chuyền cần chờ AGV recovery "
                f"hoặc manual transport."
            )
        }
    
    async def _generate_fallback_instructions(
        self,
        prioritized_lines: List[Dict[str, Any]],
        inventory_status: Dict[str, Any],
        recovery_time_minutes: int
    ) -> List[Dict[str, Any]]:
        """Tạo fallback instructions cho manual coordination"""
        
        instructions = []
        
        # Instruction 1: Ưu tiên dây chuyền có inventory ở kho chờ ngoài
        lines_with_external = [
            line for line in prioritized_lines
            if line["has_external_inventory"]
        ]
        
        if lines_with_external:
            instructions.append({
                "step": 1,
                "title": "Khởi động dây chuyền có inventory sẵn",
                "description": (
                    f"Ưu tiên khởi động {len(lines_with_external)} dây chuyền sau "
                    f"(có inventory ở kho chờ ngoài, không cần AGV):"
                ),
                "lines": [line["line_code"] for line in lines_with_external[:3]],
                "action": "Khởi động theo thứ tự ưu tiên",
                "estimated_time": "Ngay lập tức"
            })
        
        # Instruction 2: Xử lý dây chuyền cần AGV
        lines_needing_agv = [
            line for line in prioritized_lines
            if not line["has_external_inventory"]
        ]
        
        if lines_needing_agv:
            instructions.append({
                "step": 2,
                "title": "Xử lý dây chuyền cần inventory từ kho tổng",
                "description": (
                    f"{len(lines_needing_agv)} dây chuyền cần inventory từ kho tổng. "
                    f"Server AGV ước tính recovery trong {recovery_time_minutes} phút."
                ),
                "options": [
                    {
                        "option": "A",
                        "description": f"Chờ AGV recovery ({recovery_time_minutes} phút)",
                        "pros": "Tự động, không tốn nhân lực",
                        "cons": f"Chậm {recovery_time_minutes} phút"
                    },
                    {
                        "option": "B",
                        "description": "Manual transport từ kho tổng",
                        "pros": "Nhanh hơn, có thể bắt đầu ngay",
                        "cons": "Tốn nhân lực, cần điều phối"
                    }
                ],
                "lines": [line["line_code"] for line in lines_needing_agv[:3]]
            })
        
        # Instruction 3: Monitor và adjust
        instructions.append({
            "step": 3,
            "title": "Monitor recovery progress",
            "description": "Theo dõi tiến độ khôi phục server AGV và điều chỉnh plan nếu cần",
            "action": "Cập nhật trạng thái mỗi 15 phút"
        })
        
        return instructions

