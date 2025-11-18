"""Fallback Enhanced Gemini client used when ai-core module is unavailable."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List


class MockEnhancedGeminiClient:
    """Provide deterministic mock predictions when Gemini client is unavailable."""

    async def advanced_defect_prediction(
        self,
        current_data: Dict[str, Any],
        machine_id: str,
        machine_type: str,
    ) -> Dict[str, Any]:
        return self._mock_advanced_prediction(current_data, machine_id, machine_type)

    def _mock_advanced_prediction(
        self,
        current_data: Dict[str, Any],
        machine_id: str,
        machine_type: str,
    ) -> Dict[str, Any]:
        vibration = current_data.get("vibration_level", 0.0)
        efficiency = current_data.get("efficiency_score", 100.0)
        maintenance_flag = current_data.get("maintenance_flag", 0)

        if maintenance_flag == 1 and efficiency == 0:
            status = "critical"
            issue = "Seized bearing"
        elif vibration > 5.0:
            status = "warning"
            issue = "High vibration"
        else:
            status = "normal"
            issue = "None"

        avg_cycle = 95
        avg_downtime = 7.5
        next_start = datetime.utcnow() + timedelta(days=5)
        next_end = next_start + timedelta(days=5)
        next_saturday = next_start + timedelta(days=(5 - next_start.weekday()) % 7)

        scenarios: List[Dict[str, Any]] = [
            {
                "name": "Phương án A (Chạy Cầm Chừng)",
                "description": "Reduce speed by 15%",
                "impact": {
                    "cost_per_product": "+$0.05",
                    "carbon_increase": "+10g CO₂",
                    "can_finish_shift": True,
                    "risk_level": "medium",
                },
            },
            {
                "name": "Phương án B (Dừng Ngay)",
                "description": f"Immediate stop for {avg_downtime:.1f} hours",
                "impact": {
                    "downtime_cost": "$850",
                    "maintenance_cost": "$320",
                    "total_cost": "$1,170",
                    "energy_savings": "-$78",
                    "carbon_reduction": "-42 kg CO₂",
                    "risk_level": "low",
                },
            },
            {
                "name": "Phương án C (Đợi Cuối Tuần)",
                "description": "Run carefully until weekend slot",
                "impact": {
                    "cost_per_product": "+$0.03",
                    "risk_level": "medium-low",
                    "weekend_downtime_cost": "$0",
                    "total_savings": "$825 vs emergency stop",
                    "carbon_increase": "+5.5 kg CO₂",
                },
            },
        ]

        recommendation_block = [
            "Giảm tốc độ máy xuống 85% để giảm rung động",
            "Theo dõi vibration_level mỗi 30 phút",
            f"Lên lịch bảo trì cho {next_saturday.strftime('%Y-%m-%d')} 00:00-08:00",
            "Nếu vibration > 6.5 hoặc efficiency giảm thêm → Dừng ngay",
        ]

        return {
            "status": status,
            "diagnosis": {
                "issue_detected": issue,
                "confidence": 0.85,
                "reasoning": {
                    "evidence": [
                        f"vibration_level: {vibration:.2f} (> 3.0 threshold)",
                        f"efficiency_score: {efficiency:.1f}",
                        f"maintenance_flag: {maintenance_flag}",
                    ],
                    "pattern_matching": "Matches 3 historical cases",
                    "triggers": ["maintenance_flag=1", "efficiency_score low"],
                },
                "root_cause": f"{issue} requires inspection",
                "probability": 0.82,
            },
            "maintenance_recommendation": {
                "avg_maintenance_cycle_days": avg_cycle,
                "last_maintenance_date": "2024-11-01",
                "next_maintenance_window": {
                    "start": next_start.strftime("%Y-%m-%d"),
                    "end": next_end.strftime("%Y-%m-%d"),
                },
                "estimated_downtime_hours": avg_downtime,
                "optimal_scheduling": {
                    "golden_slot": {
                        "date": next_saturday.strftime("%Y-%m-%d"),
                        "time_range": "00:00 - 08:00",
                        "reason": "Weekend slot no production impact",
                        "cost_optimization": "100% downtime cost avoidance",
                    },
                    "alternative_if_urgent": "Night shift (22:00-06:00)",
                },
            },
            "scenarios": scenarios,
            "recommendations": recommendation_block,
            "timestamp": datetime.utcnow().isoformat(),
            "machine_id": machine_id,
            "machine_type": machine_type,
        }


# Module-level instance for import compatibility
enhanced_gemini_client = MockEnhancedGeminiClient()


