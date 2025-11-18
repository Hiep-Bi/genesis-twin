# 🎤 Presentation Talk Track – Genesis Twin

> Dùng để thuyết trình 30 phút (10–12 phút slides + 8–10 phút demo + Q&A).  
> Gợi ý lời thoại súc tích, nhấn mạnh 3 “Good” points và 3 nỗi đau.

---

## 0. Opening & Setup (trước slide 1)
- “Chào anh chị, em là ___ từ Team 404. Chúng em mang tới Genesis Twin – hệ điều hành nhà máy thông minh zero-impact.”
- Nhấn mạnh IoT Hub ngay đầu: “Mọi sensor data đều đi qua IoT Hub gateway → lọc/aggregate → dashboard chạy mượt, dữ liệu ở lại on-prem.”

---

## Slide-by-slide Script

### Slide 1 – Title
- “Genesis Twin – Zero-Impact Smart Factory OS. Tối ưu hóa hôm nay, kiến tạo ngày mai bền vững.”
- Giới thiệu team, partner (DENSO, FPT).

### Slide 2 – Problem Statement
- “Từ chuyến khảo sát nhà máy: 3 nỗi đau thật – dây chuyền sập không biết restart thế nào; máy cũ phải ghi tay; server AGV sập thì không ai biết ưu tiên dây chuyền nào.”
- “Chúng ta tập trung giải quyết đúng 3 nỗi đau này.”

### Slide 3 – Project Overview (14+ Modules)
- “Genesis Twin là Operating System với 14+ module: AI predictions, recovery, AGV orchestration, workflow 7 bước, IoT Hub, ESG, QR traceability... tất cả cùng dashboard.”
- “Nền tảng duy nhất gom dữ liệu từ máy cũ (IoT USB), máy mới, inventory và AGV → **Good #1: space tích hợp duy nhất**.”

### Slide 4 – Solution Overview (3 Core Features)
- “Từ 14+ module đó, hôm nay demo 3 feature chính tương ứng 3 nỗi đau: AI reasoning, Recovery prioritization, AGV fallback.”
- “Các module còn lại hỗ trợ nền như security, data pipeline.”

### Slide 5 – AI Predictions Overview
- “AI của chúng em không chỉ dự đoán mà còn giải thích: root cause, golden time slot, multi-scenario cost/carbon.”
- “Rule-based pre-filter lọc 80–90% cases → chỉ tốn chi phí AI khi cần.”

### Slide 6 – Root Cause Analysis Demo (DEMO #1)
- Show terminal (curl /scripts/demo_data_ai_predictions.json).
- Script: “Input là snapshot sensor của máy M003. Rule-based thấy bất thường mới gọi AI. Output: root cause + bằng chứng + độ chính xác 89.2% (Precision 87.5%, Recall 91%). → **Good #3: độ chính xác chứng minh được**.”

### Slide 7 – Smart Scheduling
- “AI còn gợi ý Golden Time Slot – ví dụ 14:00-16:00 giảm downtime cost. Tạo timeline rõ ràng cho maintenance.”

### Slide 8 – Multi-scenario Planning
- “Luôn có 3 scenario cost vs carbon vs throughput. Ban điều hành chọn trade-off thay vì đoán.”

### Slide 9 – Recovery System Overview
- “Nỗi đau #1: dây chuyền sập hàng loạt. Recovery engine dựng priority score dựa trên đơn hàng, inventory hai kho, dependency.”

### Slide 10 – Recovery Analysis Demo (DEMO #2)
- Run `curl .../factory/recovery/analyze`.
- “Input: 3 line L01, L02, L05 đang down. Output: thứ tự restart, timeline, checklist nhân lực/vật tư. Lý do minh bạch vì lấy từ config tables + inventory realtime.”

### Slide 11 – AGV Fallback Overview
- “Nỗi đau #2: AGV server down, kho staging chỉ đủ vài line. Chúng ta cần quyết định dây chuyền nào chạy tay.”

### Slide 12 – AGV Fallback Demo (DEMO #3)
- Run `curl .../factory/agv-fallback/handle-failure`.
- “System xem tồn kho ở kho tổng vs kho ngoài, mapping vật tư → đề xuất line nào có thể chạy manual 60 phút, line nào đợi AGV. Có fallback instructions chi tiết.”

### Slide 13 – Other Features
- “Ngoài 3 demo chính: QR traceability (digital birth certificate), workflow 7 bước với QC, IoT USB cho máy cũ, AGV orchestration mở rộng sang shipping.”

### Slide 14 – Business Value
- “Kết quả dự kiến: giảm downtime 40%, recovery time -60%, inventory sử dụng +25%, chi phí vận hành -30%.”
- “Các số này được backtest bằng `ai-core/model_evaluator.py`.”

### Slide 15 – Architecture
- “Kiến trúc 100% on-prem: React → FastAPI → IoT Hub → Gemini API hoặc GPT local (Unsloth/gpt-oss-20b), TimescaleDB, Redis.”
- “Nhấn mạnh **Good #2: data không ra ngoài**, có chế độ GPT local + IoT Hub giảm 80-90% tín hiệu trước khi vào DB.”

### Slide 16 – Impact & Next Steps
- “3 nỗi đau đã được giải quyết, bộ code chạy được, demo script rõ ràng. Sẵn sàng pilot 4-6 tuần.”
- “Next step: test với data thật, expand AGV shipping, rollout IoT USB team.”

---

## Demo Flow Cue Card
1. `docker-compose up ...` (đã chạy). Nhắc IoT Hub + token.
2. **Demo 1:** `curl .../ai/predictions/advanced-defect ... | jq`.
3. **Demo 2:** `curl .../factory/recovery/analyze ...`.
4. **Demo 3:** `curl .../factory/agv-fallback/handle-failure ...`.
5. Mở dashboard http://localhost:3000 song song (để chứng minh có UI).

---

## Q&A Reminders
- **Batch vs realtime?** → IoT Hub + rule-based filter + WebSocket/Redis + TimescaleDB.
- **Chi phí AI?** → Rule-based giảm 80-90%, GPT local = $0.
- **Security?** → JWT, RBAC, rate limit, Pydantic validation, encryption, Docker isolation (nhắc slides security).
- **Feasibility?** → Config tables + seed data, scripts trong `/scripts`, AI accuracy log trong `/ai-core/model_evaluator.py`.

---

## Closing Line
“Genesis Twin không chỉ là bản demo slide, toàn bộ code + script chạy được, chứng minh từng bước từ input tới output. Với 14+ module nhưng tập trung 3 nỗi đau, chúng em tự tin triển khai pilot ngay sau hackathon.”


