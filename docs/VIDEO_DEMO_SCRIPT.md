# 🎬 Video Demo Script (≤15 phút)

> Mục tiêu: nêu rõ **Input → Output**, **Environment + Devices**, **Data/Resource flow** trong 5 phân đoạn.  
> Bám sát DEMO_PLAYBOOK + Talk Track, bổ sung lời thoại chi tiết và data sample.

---

## 0. Yêu cầu & Chuẩn bị
- Tổng thời lượng: 12‑13 phút nói + 2‑3 phút buffer.  
- Khởi động stack: `docker compose up -d` (chạy tại thư mục gốc repo).  
- Stack đang chạy: `postgres`, `redis`, `backend`, `frontend`, `ai-core`. Chuẩn bị terminal đã sẵn `docker compose ps`.  
- Account: `admin@genesistwin.com / admin123`.  
- Dataset gốc (đưa vào slide phụ hoặc khi nói tới “Resource”):
  - `backend/ai-core/data/Production System Dataset.csv` – 2,400+ hàng sensor (temperature, vibration, error_rate...).  
  - `backend/ai-core/data/maintenance_history_with_type.csv` – lịch sử bảo trì (issue, action, downtime_hours).  
- Mock input nhanh cho UI: `scripts/mock_live_payload.json`. Copy số liệu sang form Analytics khi cần nhập tay.

---

## 1. Timeline & Talk Track

| Thời điểm | Nội dung | Hành động | Key Message |
| --- | --- | --- | --- |
| 00:00 – 01:00 | **Opening + Environment** | Camera quay terminal: `docker compose ps` → 5 containers “Up”. | “Demo chạy on-prem Docker trên laptop Windows, data không rời server (**Good #2**).” |
| 01:00 – 02:30 | **Devices & Dataset** | Mô tả 10 CNC + 10 AGV (hiện trên Dashboard/Advanced AI). Share 2 file CSV (mở nhanh bằng VS Code preview). | “Nguồn data từ CSV thật + IoT Hub streaming → Dashboard không lag.” |
| 02:30 – 05:00 | **Feature 1 – Advanced Defect Prediction** | a) Chạy `python scripts/demo_core_features.py --feature ai --email admin@genesistwin.com --password admin123` → zoom kết quả JSON (confidence, root causes). b) Chuyển sang UI Analytics, nhập số trong `mock_live_payload.json`, bấm Analyze. | “Input = sensor snapshot, rule-base lọc, AI reasoning 85% confidence, Golden Slot 29/11 00:00-08:00.” |
| 05:00 – 08:00 | **Feature 2 – Scenario & Recovery** | Hiển thị phần Scenario Analysis (ảnh 2) và narrative (ảnh 3). Song song chạy `python scripts/demo_core_features.py --feature recovery --email admin@genesistwin.com --password admin123`. | “3 phương án A/B/C với cost & carbon → đáp ứng yêu cầu Input→Output. Recovery engine dùng inventory, maintenance flag.” |
| 08:00 – 11:00 | **Feature 3 – AGV Fallback & Autonomous Control** | Vào tab `Advanced AI` → `Test AGV Assignment`, sau đó `Analytics > Simulate Failure`. Terminal chạy `python scripts/demo_core_features.py --feature agv --email admin@genesistwin.com --password admin123`. | “Thiết bị liên quan: 10 AGVs. System push fallback instructions & adjustments (feed_rate, coolant).” |
| 11:00 – 13:00 | **MLOps & Data Pipeline** | Postman/terminal: `curl -X POST http://localhost:8000/api/v1/mlops/retrain -H "Authorization: Bearer <token>" -F "dataset=@ai-core/data/Production System Dataset.csv" -F "maintenance=@ai-core/data/maintenance_history_with_type.csv"`. Đọc metrics trả về. | “Chứng minh retrain được, accuracy 0.91, precision 0.89. Data flow: IoT Hub → Redis/TimescaleDB.” |
| 13:00 – 14:30 | **Good Points Recap** | Quay Sidebar hiển thị 14+ modules. Nhấn mạnh 3 “Good”. | “Good #1: platform tích hợp. Good #2: data on-prem, GPT local. Good #3: accuracy có số.” |
| 14:30 – 15:00 | **Closing & CTA** | Slide Impact + Next steps. | “Sẵn sàng pilot, minh chứng input-output rõ ràng.” |

---

## 2. Lời thoại chi tiết (từng phân đoạn)

### 1) Opening & Environment
- “Chào ban giám khảo, đây là Genesis Twin – operating system cho nhà máy. Demo chạy trên laptop Windows 11, Docker Desktop. Tất cả container đang `Up` → chứng minh environment.”  
- “Khi ban tổ chức yêu cầu Input/Output + Device, chúng em show ngay terminal và dashboard real-time.”

### 2) Devices & Dataset
- “Phần này là list thiết bị: 10 CNC/Drill/Welder, 10 AGV. Dữ liệu sensor thật từ file `Production System Dataset.csv` (2.4k dòng), mỗi dòng có temperature, vibration, power, error_rate. Lịch sử bảo trì nằm ở `maintenance_history_with_type.csv`, gồm issue, action, downtime_hours – dùng để train rule + GPT local.”  
- “IoT Hub gom tín hiệu: batch vào TimescaleDB, realtime phát qua Redis pub/sub → tránh lag dashboard.”

### 3) Feature 1 – Advanced Defect Prediction
1. **Input (Terminal)**  
   - “Bước 1 em chạy script `python scripts/demo_core_features.py --feature ai --email ... --password ...`. File JSON `scripts/demo_data_ai_predictions.json` chứa 2 snapshot – sensor bình thường và bất thường.”  
2. **Process**  
   - “Rule-based (`ai-core/rule_base_prediction.py`) đọc `model.pkl`, nếu score = 1 thì gọi Gemini/GPT local (`EnhancedGPTClient`).”  
3. **Output**  
   - “Anh chị thấy kết quả: `diagnosis.root_causes`, `maintenance_recommendation`, `scenarios`. Confidence ~85%. Đây chính là phần Input→Output mà đề yêu cầu.”  
4. **UI Walkthrough**  
   - “Trên dashboard, em copy số liệu trong `scripts/mock_live_payload.json` (temperature 82, vibration 4.8...). Bấm Analyze → UI hiển thị đúng 85% confidence, Golden Slot, root cause matches 3 cases.”

### 4) Feature 2 – Scenario & Recovery
- “Input: API `/factory/recovery/analyze` nhận danh sách line đang downtime (file `scripts/demo_data_recovery.json`).”  
- “Process: service `backend/app/services/recovery_prioritization.py` lấy order urgency, inventory, maintenance flag.”  
- “Output: Priority list + Scenario cards (A/B/C). Lời thoại: ‘Chúng tôi cho ban điều hành 3 lựa chọn với cost, downtime, carbon – thay vì đoán.’”  
- “Nhắc: ‘Phần narrative tiếng Việt giải thích để sales team hiểu – đây là đáp án cho yêu cầu explanation không kỹ thuật.’”

### 5) Feature 3 – AGV Fallback & Autonomous Control
- “Input: `/factory/agv-fallback/handle-failure` (file `scripts/demo_data_agv_fallback.json`).”  
- “Process: `Factory Operations + AGV Orchestration` kiểm tra tồn kho, mapping vật tư, battery AGV, output fallback instructions.”  
- “Output: trong dashboard → card ‘Autonomous Control History’ cập nhật adjustments, tab Advanced AI hiển thị fleet status (Idle/Busy).”  
- “Lời thoại: ‘Nếu AGV server down, system tự chọn line nào chạy tay, line nào đợi – kèm JSON feed_rate/coolant adjustments.’”

### 6) MLOps & Data Pipeline Proof
- “Để đáp ứng mentor: em gọi `/api/v1/mlops/retrain` với 2 CSV. Đây là minh chứng retrain real-time. Output JSON hiển thị accuracy, precision, recall, F1, ROC AUC + model_version.”  
- “Giải thích data pipeline: IoT Hub service (`backend/app/services/iot_hub.py`) xử lý ingestion, validate, aggregate, flush sang TimescaleDB + Redis. Dữ liệu training mới được append, model_evaluator so sánh trước-sau.”

### 7) Recap Good Points
- “Good #1 – Space tích hợp: Sidebar 14+ module; Slide Overview.”  
- “Good #2 – Data on-prem: GPT local `unsloth/gpt-oss-20b`, Docker network nội bộ.”  
- “Good #3 – Accuracy: hiển thị metrics + 85% confidence.”  
- “Kết: ‘Genesis Twin chứng minh được logic input → output, environment rõ ràng, thiết bị mô phỏng sẵn sàng pilot.’”

---

## 3. Mock Data & Command Cheatsheet

| Use case | File / Command | Ghi chú |
| --- | --- | --- |
| AI prediction API | `python scripts/demo_core_features.py --feature ai --email admin@genesistwin.com --password admin123` | In ra JSON reasoning, root causes. |
| Recovery analysis | `python scripts/demo_core_features.py --feature recovery ...` | Xuất priority list + recommended actions. |
| AGV fallback | `python scripts/demo_core_features.py --feature agv ...` | Cho thấy fallback instructions & manual steps. |
| Manual UI input | `scripts/mock_live_payload.json` | Copy từng field vào trang Analytics để bấm Analyze. |
| MLOps retrain | `curl -X POST http://localhost:8000/api/v1/mlops/retrain ...` | Cho metrics accuracy/precision. |
| Token hỗ trợ curl | `python scripts/demo_core_features.py --email ... --password ... --token-only` *(tùy chọn nếu sửa script)* | Có thể tái sử dụng Bearer token. |

---

## 4. Checklist trước khi quay
1. `docker compose ps` = 5 containers Up.  
2. `seed_config_data.py` đã chạy, tài khoản admin ok.  
3. `scripts/demo_core_features.py` chạy thành công cả 3 feature (log lưu lại).  
4. Frontend http://localhost:3000 đăng nhập sẵn (giảm thời gian).  
5. Postman/curl chuẩn bị request retrain với token hợp lệ.  
6. Slide backup: liệt kê dataset path, devices list, IoT Hub diagram.  
7. OBS/Screencast set 60fps để capture chart animations.

---

**Ghi nhớ:** Bất cứ câu hỏi “Input-Output/Environment/Device/Data?” → chỉ vào tài liệu này + quay lại từng phân đoạn. Tất cả số liệu đều đã map tới file cụ thể trong repo, đảm bảo tính chứng thực khi demo.

