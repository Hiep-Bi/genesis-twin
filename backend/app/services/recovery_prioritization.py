"""Production Line Recovery Prioritization System

Giải quyết nỗi đau: Khi dây chuyền sập, không biết khởi động lại thứ tự nào tối ưu
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class RecoveryPrioritizationService:
    """
    🔄 Production Line Recovery System
    
    Khi dây chuyền sập, hệ thống sẽ:
    1. Phân tích tình trạng hiện tại (máy nào sập, inventory, đơn hàng)
    2. Tính toán thứ tự khởi động tối ưu dựa trên:
       - Priority của đơn hàng
       - Inventory availability (kho tổng vs kho chờ ngoài)
       - Dependencies giữa các dây chuyền
       - Thời gian recovery ước tính
    3. Đề xuất kế hoạch khởi động lại với timeline
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def analyze_recovery_plan(
        self,
        affected_lines: List[str],
        agv_server_status: str = "down",  # "up" or "down"
        inventory_status: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Phân tích và đề xuất kế hoạch khởi động lại
        
        Args:
            affected_lines: Danh sách mã dây chuyền bị sập
            agv_server_status: Trạng thái server AGV ("up" or "down")
            inventory_status: Trạng thái inventory (nếu None sẽ query từ DB)
        
        Returns:
            Recovery plan với thứ tự ưu tiên, timeline, và lý do
        """
        
        # 1. Thu thập thông tin hiện tại
        current_state = await self._gather_current_state(
            affected_lines,
            agv_server_status,
            inventory_status
        )
        
        # 2. Tính toán priority score cho mỗi dây chuyền
        line_priorities = await self._calculate_line_priorities(
            affected_lines,
            current_state
        )
        
        # 3. Xây dựng recovery sequence
        recovery_sequence = await self._build_recovery_sequence(
            line_priorities,
            current_state
        )
        
        # 4. Tính toán timeline và resource requirements
        recovery_plan = await self._build_recovery_plan(
            recovery_sequence,
            current_state
        )
        
        return recovery_plan
    
    async def _gather_current_state(
        self,
        affected_lines: List[str],
        agv_server_status: str,
        inventory_status: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Thu thập trạng thái hiện tại của nhà máy"""
        
        # Query production orders đang chờ
        orders_query = text("""
            SELECT 
                po.id,
                po.order_number,
                po.product_code,
                po.quantity,
                po.priority,
                po.scheduled_end,
                po.status
            FROM production_orders po
            WHERE po.status IN ('pending', 'in_progress')
            ORDER BY po.priority DESC, po.scheduled_end ASC
        """)
        
        orders = self.db.execute(orders_query).fetchall()
        
        # Query inventory nếu chưa có
        if inventory_status is None:
            inventory_query = text("""
                SELECT 
                    location,
                    material_code,
                    SUM(quantity) as total_quantity
                FROM inventory_transactions
                WHERE transaction_type = 'receive'
                GROUP BY location, material_code
            """)
            
            inventory = self.db.execute(inventory_query).fetchall()
            
            inventory_status = {
                "main_warehouse": {},
                "external_staging": {}  # Kho chờ ngoài
            }
            
            for row in inventory:
                location = row[0]
                material_code = row[1]
                quantity = row[2]
                
                if "staging" in location.lower() or "external" in location.lower():
                    inventory_status["external_staging"][material_code] = quantity
                else:
                    inventory_status["main_warehouse"][material_code] = quantity
        
        # Query machine status
        machines_query = text("""
            SELECT 
                m.machine_code,
                m.machine_type,
                m.status,
                m.position_x,
                m.position_y
            FROM machines m
            WHERE m.machine_code LIKE ANY(:line_patterns)
        """)
        
        line_patterns = [f"{line}%" for line in affected_lines]
        machines = self.db.execute(
            machines_query,
            {"line_patterns": line_patterns}
        ).fetchall()
        
        return {
            "affected_lines": affected_lines,
            "pending_orders": [
                {
                    "id": str(row[0]),
                    "order_number": row[1],
                    "product_code": row[2],
                    "quantity": row[3],
                    "priority": row[4],
                    "deadline": row[5].isoformat() if row[5] else None,
                    "status": row[6]
                }
                for row in orders
            ],
            "inventory": inventory_status,
            "agv_server_status": agv_server_status,
            "machines": [
                {
                    "machine_code": row[0],
                    "machine_type": row[1],
                    "status": row[2],
                    "position": {"x": row[3], "y": row[4]}
                }
                for row in machines
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
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
        return parts[0] if parts else None
    
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
            "has_external_inventory": any(
                req[3] == "external_staging" and req[0] in available_materials
                for req in requirements
            ),
            "all_materials_available": len(available_materials) == len(requirements),
            "critical_materials_available": critical_materials_available,
            "available_materials_count": len(available_materials),
            "total_materials_count": len(requirements)
        }
    
    async def _calculate_line_priorities(
        self,
        affected_lines: List[str],
        current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Tính toán priority score cho mỗi dây chuyền"""
        
        line_scores = []
        
        for line_code in affected_lines:
            score = 0
            reasons = []
            
            # 1. Priority của đơn hàng đang chờ (0-40 điểm)
            # Map product codes to line codes using config
            line_orders = []
            for order in current_state["pending_orders"]:
                mapped_line = await self._get_line_code_from_product(order.get("product_code", ""))
                if mapped_line == line_code:
                    line_orders.append(order)
            
            if line_orders:
                max_order_priority = max(o["priority"] for o in line_orders)
                total_quantity = sum(o["quantity"] for o in line_orders)
                
                score += max_order_priority * 4  # Priority 1-10 -> 4-40 điểm
                reasons.append(
                    f"Có {len(line_orders)} đơn hàng đang chờ "
                    f"(priority: {max_order_priority}, tổng: {total_quantity} sản phẩm)"
                )
            
            # 2. Inventory availability (0-30 điểm) - Sử dụng config table
            material_availability = await self._check_line_material_availability(
                line_code,
                current_state["inventory"]
            )
            
            if material_availability["has_external_inventory"]:
                score += 30
                reasons.append(
                    f"✅ Có inventory ở kho chờ ngoài "
                    f"({material_availability['available_materials_count']}/{material_availability['total_materials_count']} vật liệu)"
                )
            elif material_availability["all_materials_available"]:
                score += 15
                reasons.append(
                    f"⚠️ Có đủ inventory ở kho tổng "
                    f"({material_availability['available_materials_count']}/{material_availability['total_materials_count']} vật liệu)"
                )
            elif not material_availability["critical_materials_available"]:
                score -= 10  # Penalty nếu thiếu critical materials
                reasons.append(
                    f"❌ Thiếu critical materials - không thể khởi động"
                )
            
            # 3. Deadline urgency (0-20 điểm)
            urgent_orders = [
                o for o in line_orders
                if o.get("deadline") and 
                datetime.fromisoformat(o["deadline"]) < datetime.utcnow() + timedelta(days=1)
            ]
            
            if urgent_orders:
                score += 20
                reasons.append(f"Có {len(urgent_orders)} đơn hàng gấp (deadline < 24h)")
            
            # 4. Dependencies (0-10 điểm) - Sử dụng config table
            dependency_query = text("""
                SELECT is_upstream, dependencies
                FROM production_line_mapping
                WHERE line_code = :line_code
            """)
            
            dep_result = self.db.execute(dependency_query, {"line_code": line_code}).fetchone()
            if dep_result:
                is_upstream = dep_result[0]
                dependencies = dep_result[1] if dep_result[1] else []
                
                if is_upstream:
                    score += 10
                    reasons.append("Dây chuyền upstream (ảnh hưởng đến các line khác)")
                elif dependencies:
                    score += 5
                    reasons.append(f"Có {len(dependencies)} dây chuyền phụ thuộc")
            
            line_scores.append({
                "line_code": line_code,
                "priority_score": score,
                "reasons": reasons,
                "estimated_recovery_time_minutes": 30 + len(line_orders) * 5,
                "material_availability": material_availability,
                "can_start_immediately": (
                    material_availability["has_external_inventory"] and
                    material_availability["critical_materials_available"]
                )
            })
        
        # Sắp xếp theo priority score giảm dần
        line_scores.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return line_scores
    
    async def _build_recovery_sequence(
        self,
        line_priorities: List[Dict[str, Any]],
        current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Xây dựng thứ tự khởi động lại"""
        
        sequence = []
        current_time = datetime.utcnow()
        
        for idx, line_data in enumerate(line_priorities):
            start_time = current_time + timedelta(
                minutes=sum(
                    l["estimated_recovery_time_minutes"]
                    for l in line_priorities[:idx]
                )
            )
            
            sequence.append({
                "step": idx + 1,
                "line_code": line_data["line_code"],
                "priority_score": line_data["priority_score"],
                "reasons": line_data["reasons"],
                "estimated_start": start_time.isoformat(),
                "estimated_duration_minutes": line_data["estimated_recovery_time_minutes"],
                "estimated_completion": (
                    start_time + timedelta(
                        minutes=line_data["estimated_recovery_time_minutes"]
                    )
                ).isoformat()
            })
        
        return sequence
    
    async def _build_recovery_plan(
        self,
        recovery_sequence: List[Dict[str, Any]],
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Xây dựng kế hoạch recovery hoàn chỉnh"""
        
        total_recovery_time = sum(
            step["estimated_duration_minutes"]
            for step in recovery_sequence
        )
        
        # Recommendations
        recommendations = []
        
        if current_state["agv_server_status"] == "down":
            recommendations.append({
                "type": "critical",
                "title": "Server AGV đang sập",
                "action": "Sử dụng inventory từ kho chờ ngoài trước, "
                         "ưu tiên dây chuyền có inventory sẵn",
                "estimated_agv_recovery": "60 phút"
            })
        
        if current_state["inventory"].get("external_staging"):
            recommendations.append({
                "type": "info",
                "title": "Kho chờ ngoài có inventory",
                "action": "Khởi động các dây chuyền có inventory ở kho chờ ngoài trước "
                         "để tận dụng nguồn cung sẵn có",
            })
        
        return {
            "status": "recovery_plan_ready",
            "affected_lines_count": len(current_state["affected_lines"]),
            "total_recovery_time_minutes": total_recovery_time,
            "recovery_sequence": recovery_sequence,
            "recommendations": recommendations,
            "current_state_summary": {
                "pending_orders": len(current_state["pending_orders"]),
                "agv_server": current_state["agv_server_status"],
                "inventory_locations": {
                    "main_warehouse": len(
                        current_state["inventory"].get("main_warehouse", {})
                    ),
                    "external_staging": len(
                        current_state["inventory"].get("external_staging", {})
                    )
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }

