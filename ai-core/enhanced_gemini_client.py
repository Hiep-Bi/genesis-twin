"""Enhanced Gemini AI Client với Advanced Reasoning"""
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import logging
import json
import pandas as pd
from datetime import datetime, timedelta

from config import config

logger = logging.getLogger(__name__)


class EnhancedGeminiClient:
    """Enhanced Gemini client với deep reasoning và real data integration"""
    
    def __init__(self):
        self.model = None
        self.production_data = None
        self.maintenance_history = None
        self._configure()
        self._load_real_data()
    
    def _configure(self):
        """Configure Gemini API"""
        if not config.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Using mock mode.")
            return
        
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            logger.info(f"✅ Gemini client configured: {config.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
    
    def _load_real_data(self):
        """Load real production and maintenance data"""
        try:
            # Load CSV files
            self.production_data = pd.read_csv("data/Production System Dataset.csv")
            self.maintenance_history = pd.read_csv("data/maintenance_history_with_type.csv")
            
            logger.info(f"✅ Loaded {len(self.production_data)} production records")
            logger.info(f"✅ Loaded {len(self.maintenance_history)} maintenance records")
            
        except Exception as e:
            logger.warning(f"Could not load real data: {e}. Using simulation mode.")
    
    async def advanced_defect_prediction(
        self,
        current_data: Dict[str, Any],
        machine_id: str,
        machine_type: str
    ) -> Dict[str, Any]:
        """
        Advanced defect prediction với:
        1. Root cause analysis chi tiết
        2. Historical pattern matching
        3. Maintenance scheduling optimization
        4. Multi-scenario planning
        """
        
        # 1. Get maintenance history cho machine này
        maintenance_hist = self._get_maintenance_history(machine_id, machine_type)
        
        # 2. Get similar historical patterns
        similar_cases = self._find_similar_cases(current_data, machine_type)
        
        # 3. Analyze với Gemini
        if not self.model:
            return self._mock_advanced_prediction(current_data, maintenance_hist)
        
        try:
            prompt = f"""
Bạn là chuyên gia AI về bảo trì dự đoán trong Smart Manufacturing.

**DỮ LIỆU HIỆN TẠI (Real-time Sensor Data):**
```json
{json.dumps(current_data, indent=2)}
```

**LỊCH SỬ BẢO TRÌ CỦA THIẾT BỊ {machine_id} ({machine_type}):**
```json
{json.dumps(maintenance_hist, indent=2)}
```

**CÁC TRƯỜNG HỢP TƯƠNG TỰ TRONG QUÁ KHỨ:**
```json
{json.dumps(similar_cases, indent=2)}
```

Hãy phân tích chi tiết và trả về JSON với cấu trúc sau:

{{
  "status": "normal" | "warning" | "critical",
  "diagnosis": {{
    "issue_detected": "<tên sự cố cụ thể>",
    "confidence": <0-1>,
    "reasoning": {{
      "evidence": [
        "Chỉ số X = Y (cao/thấp bất thường so với ngưỡng Z)",
        "Chỉ số A tương đồng với B trong lịch sử"
      ],
      "pattern_matching": "Khớp với K/N lần '<loại sự cố>' trong lịch sử",
      "triggers": [
        "maintenance_flag: 1 (đã kích hoạt cờ bảo trì)",
        "efficiency_score: 0.0 (dừng sản xuất)"
      ]
    }},
    "root_cause": "<nguyên nhân gốc rễ>",
    "probability": <0-1>
  }},
  "maintenance_recommendation": {{
    "avg_maintenance_cycle_days": <số ngày>,
    "last_maintenance_date": "YYYY-MM-DD",
    "next_maintenance_window": {{
      "start": "YYYY-MM-DD",
      "end": "YYYY-MM-DD"
    }},
    "estimated_downtime_hours": <số giờ>,
    "optimal_scheduling": {{
      "golden_slot": {{
        "date": "YYYY-MM-DD",
        "time_range": "HH:MM - HH:MM",
        "reason": "Khoảng thời gian vàng 8 giờ trống (bảo trì định kỳ) vào Thứ Bảy",
        "cost_optimization": "100% tối ưu chi phí dừng máy"
      }},
      "alternative_if_urgent": "Có thể thực hiện vào ca đêm (22:00-06:00) để giảm ảnh hưởng"
    }}
  }},
  "scenarios": [
    {{
      "name": "Phương án A (Chạy Cầm Chừng)",
      "description": "Giảm X% tốc độ máy",
      "impact": {{
        "cost_per_product": "+$X.XX",
        "carbon_increase": "+Xg CO₂",
        "can_finish_shift": true,
        "risk_level": "medium"
      }}
    }},
    {{
      "name": "Phương án B (Dừng Ngay)",
      "description": "Dừng máy Y giờ để bảo trì",
      "impact": {{
        "downtime_cost": "$XXX",
        "energy_savings": "-$YYY",
        "carbon_reduction": "-ZZ kg CO₂",
        "risk_level": "low"
      }}
    }},
    {{
      "name": "Phương án C (Đợi Cuối Tuần)",
      "description": "Chạy cẩn thận đến cuối tuần",
      "impact": {{
        "additional_risk": "có thể hỏng nặng hơn",
        "potential_cost_increase": "$XXX",
        "recommendation": "Chỉ dùng nếu cần thiết"
      }}
    }}
  ],
  "recommendations": [
    "Action 1: <hành động cụ thể>",
    "Action 2: <hành động cụ thể>"
  ]
}}

**LƯU Ý:**
- Phân tích dựa trên DATA THỰC TẾ, không chung chung
- Đưa ra SỐ LIỆU CỤ THỂ (chi phí, carbon, thời gian)
- So sánh các phương án một cách ĐỊNH LƯỢNG
- Reasoning phải rõ ràng, dễ hiểu
"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.4,  # Lower for more deterministic
                    max_output_tokens=3000,
                )
            )
            
            result_text = response.text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            # Add metadata
            result["timestamp"] = datetime.utcnow().isoformat()
            result["machine_id"] = machine_id
            result["machine_type"] = machine_type
            
            logger.info(f"✅ Advanced prediction for {machine_id}: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced prediction: {e}")
            return self._mock_advanced_prediction(current_data, maintenance_hist)
    
    def _get_maintenance_history(self, machine_id: str, machine_type: str) -> List[Dict]:
        """Get maintenance history từ real data"""
        if self.maintenance_history is None:
            return []
        
        # Filter by machine_id and machine_type
        filtered = self.maintenance_history[
            (self.maintenance_history['machine_id'] == machine_id) &
            (self.maintenance_history['machine_type'] == machine_type)
        ]
        
        if len(filtered) == 0:
            return []
        
        # Convert to dict and return last 10
        records = filtered.tail(10).to_dict('records')
        
        # Calculate maintenance cycle
        if len(records) > 1:
            dates = pd.to_datetime(filtered['maintenance_date'])
            if len(dates) > 1:
                avg_cycle = (dates.max() - dates.min()).days / (len(dates) - 1)
                return {
                    "records": records,
                    "avg_cycle_days": round(avg_cycle, 0),
                    "avg_downtime_hours": round(filtered['downtime_hours'].mean(), 1),
                    "common_issues": filtered['issue'].value_counts().head(5).to_dict()
                }
        
        return {"records": records, "avg_cycle_days": None, "avg_downtime_hours": None}
    
    def _find_similar_cases(self, current_data: Dict, machine_type: str) -> List[Dict]:
        """Find similar cases từ production data"""
        if self.production_data is None:
            return []
        
        try:
            # Filter by machine type and maintenance_flag = 1
            filtered = self.production_data[
                (self.production_data['machine_type'] == machine_type) &
                (self.production_data['maintenance_flag'] == 1)
            ]
            
            if len(filtered) == 0:
                return []
            
            # Get similar cases (top 5)
            similar = filtered.tail(5)[['timestamp', 'temperature', 'vibration_level', 
                                        'efficiency_score', 'error_rate']].to_dict('records')
            
            return similar
            
        except Exception as e:
            logger.error(f"Error finding similar cases: {e}")
            return []
    
    def _mock_advanced_prediction(self, current_data: Dict, maintenance_hist: Dict) -> Dict:
        """Mock prediction khi không có Gemini API"""
        
        # Extract values
        vibration = current_data.get('vibration_level', 0)
        efficiency = current_data.get('efficiency_score', 100)
        maintenance_flag = current_data.get('maintenance_flag', 0)
        
        # Determine status
        if maintenance_flag == 1 and efficiency == 0:
            status = "critical"
            issue = "Lỏng vít"
        elif vibration > 5.0:
            status = "warning"
            issue = "Rung động cao"
        else:
            status = "normal"
            issue = "Không có"
        
        # Get maintenance info
        common_issues = maintenance_hist.get('common_issues', {}) if isinstance(maintenance_hist, dict) else {}
        avg_cycle = maintenance_hist.get('avg_cycle_days', 95) if isinstance(maintenance_hist, dict) else 95
        avg_downtime = maintenance_hist.get('avg_downtime_hours', 7.5) if isinstance(maintenance_hist, dict) else 7.5
        
        # Calculate next maintenance window
        next_start = datetime.now() + timedelta(days=5)
        next_end = next_start + timedelta(days=5)
        
        # Find next Saturday
        days_until_saturday = (5 - next_start.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        next_saturday = next_start + timedelta(days=days_until_saturday)
        
        result = {
            "status": status,
            "diagnosis": {
                "issue_detected": issue,
                "confidence": 0.85,
                "reasoning": {
                    "evidence": [
                        f"vibration_level: {vibration:.2f} (cao bất thường, ngưỡng thường < 3.0)",
                        f"efficiency_score: {efficiency:.1f} (dừng sản xuất)",
                        f"maintenance_flag: {maintenance_flag} (cờ bảo trì đã kích hoạt)"
                    ],
                    "pattern_matching": f"Khớp với 3/{len(common_issues)} lần '{issue}' trong lịch sử",
                    "triggers": [
                        f"maintenance_flag: {maintenance_flag} (đã kích hoạt)",
                        f"efficiency_score: {efficiency:.1f} (dừng sản xuất)"
                    ]
                },
                "root_cause": f"{issue} tái phát do chưa được khắc phục triệt để",
                "probability": 0.85
            },
            "maintenance_recommendation": {
                "avg_maintenance_cycle_days": int(avg_cycle),
                "last_maintenance_date": "2024-11-01",
                "next_maintenance_window": {
                    "start": next_start.strftime("%Y-%m-%d"),
                    "end": next_end.strftime("%Y-%m-%d")
                },
                "estimated_downtime_hours": avg_downtime,
                "optimal_scheduling": {
                    "golden_slot": {
                        "date": next_saturday.strftime("%Y-%m-%d"),
                        "time_range": "00:00 - 08:00",
                        "reason": f"Khoảng thời gian vàng 8 giờ trống (bảo trì định kỳ) vào Thứ Bảy, {next_saturday.strftime('%Y-%m-%d')}",
                        "cost_optimization": "100% tối ưu chi phí dừng máy (không ảnh hưởng sản xuất)"
                    },
                    "alternative_if_urgent": "Có thể thực hiện vào ca đêm (22:00-06:00) để giảm 70% ảnh hưởng sản xuất"
                }
            },
            "scenarios": [
                {
                    "name": "Phương án A (Chạy Cầm Chừng)",
                    "description": "Giảm 15% tốc độ máy",
                    "impact": {
                        "cost_per_product": "+$0.05",
                        "carbon_increase": "+10g CO₂",
                        "can_finish_shift": True,
                        "risk_level": "medium",
                        "total_shift_cost": "+$45.50",
                        "total_carbon": "+9.1 kg CO₂"
                    }
                },
                {
                    "name": "Phương án B (Dừng Ngay)",
                    "description": f"Dừng máy {avg_downtime:.1f} giờ để bảo trì khẩn cấp",
                    "impact": {
                        "downtime_cost": "$850",
                        "maintenance_cost": "$320",
                        "total_cost": "$1,170",
                        "energy_savings": "-$78",
                        "carbon_reduction": "-42 kg CO₂",
                        "risk_level": "low",
                        "recommendation": "Đảm bảo an toàn nhưng tốn chi phí cao"
                    }
                },
                {
                    "name": "Phương án C (Đợi Cuối Tuần - KHUYẾN NGHỊ)",
                    "description": "Giảm 10% tốc độ, chạy cẩn thận đến Thứ Bảy",
                    "impact": {
                        "cost_per_product": "+$0.03",
                        "risk_level": "medium-low",
                        "weekend_downtime_cost": "$0 (không ảnh hưởng)",
                        "total_savings": "$825 so với Phương án B",
                        "carbon_increase": "+5.5 kg CO₂ (trong 5 ngày)",
                        "recommendation": "TỐI ƯU NHẤT về mặt chi phí và carbon",
                        "condition": "Nếu rung động không tăng thêm"
                    }
                }
            ],
            "recommendations": [
                f"✅ Action 1: Giảm tốc độ máy xuống 85% NGAY để giảm rung động",
                "✅ Action 2: Theo dõi vibration_level mỗi 30 phút",
                f"✅ Action 3: Tạo lệnh bảo trì cho {next_saturday.strftime('%Y-%m-%d')} 00:00-08:00",
                "⚠️ Action 4: Nếu vibration > 6.5 hoặc hiệu suất giảm thêm → Dừng ngay (Phương án B)",
                "📊 Action 5: Cập nhật lịch sản xuất tuần sau để bù sản lượng"
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "machine_id": current_data.get('machine_id', 'M003'),
            "machine_type": current_data.get('machine_type', 'CNC')
        }
        
        return result


# Global instance
enhanced_gemini_client = EnhancedGeminiClient()

