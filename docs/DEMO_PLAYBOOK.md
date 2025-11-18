# 🎬 Demo Playbook – 10 phút cho 3 nỗi đau

## 0. Chuẩn bị nhanh (5 phút trước demo)
- `docker-compose up -d postgres redis backend frontend ai-core`
- Seed config nếu cần: `cd scripts && python seed_config_data.py`
- Nạp demo data (optional): `python scripts/load_demo_data.py` *(nếu đã có)*
- Mở 3 tab terminal đã sẵn sàng với các lệnh dưới đây
- Kiểm tra token đăng nhập (`admin@genesis.ai / admin123`)
- Note khi mở đầu: “Tất cả tín hiệu đi qua IoT Hub gateway → lọc/aggregate → dashboard không giật lag, dữ liệu ở lại on-prem.”

---

## 1️⃣ Enhanced AI Predictions (Root Cause + Reasoning)

### Commands
```bash
# Terminal 1 – gọi API với demo data
curl -X POST http://localhost:8000/api/v1/ai/predictions/advanced-defect \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d @scripts/demo_data_ai_predictions.json | jq '.predictions[0]'
```

### Talking points (45s)
1. **“Input”**: 2 snapshot sensor data (M003) → rung động tăng, efficiency = 0.
2. **“Process”**: AI lọc qua rule-based model → chỉ khi abnormal mới gọi LLM.
3. **“Output”**: 
   - Root cause + reasoning + evidence
   - Golden time slot (thứ Bảy 00:00-08:00)
   - 3 scenarios cost vs carbon
   - Accuracy proof: 89.2% (Precision 87.5%, Recall 91.0%) – slide 5.

---

## 2️⃣ Production Line Recovery System

### Commands
```bash
curl -X POST http://localhost:8000/api/v1/factory/recovery/analyze \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d @scripts/demo_data_recovery.json | jq '.recommendations[0]'
```

### Talking points (45s)
1. **Scenario**: 3 lines sập (L01, L02, L05), inventory nằm ở 2 kho.
2. **Logic**: 
   - Mapping product → line code bằng config table
   - Priority score = Order urgency + Inventory availability + Dependencies
   - Timeline & staffing gợi ý
3. **Output**:
   - Thứ tự restart
   - Estimated recovery time
   - Action checklist (nhân lực, vật tư)

---

## 3️⃣ AGV Fallback & Inventory Intelligence

### Commands
```bash
curl -X POST http://localhost:8000/api/v1/factory/agv-fallback/handle-failure \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d @scripts/demo_data_agv_fallback.json | jq '.prioritized_lines[0]'
```

### Talking points (45s)
1. **Scenario**: Server AGV down 60 phút, kho ngoài chỉ đủ cho vài line.
2. **Logic**:
   - Check material availability theo location
   - Ưu tiên line có đủ trong kho chờ ngoài (manual push)
   - Đề xuất fallback instructions (manual vs đợi AGV)
3. **Output**:
   - Bảng ưu tiên line
   - Material breakdown
   - Fallback playbook (who/what/when)

---

## 4️⃣ Chứng minh 3 “GOOD” điểm

| Good | Slide | Demo reference |
|------|-------|----------------|
| **Space tích hợp** | Slide 3 / 14 | Recovery gọi inventory, AGV, AI trong cùng hệ |
| **Data nội bộ** | Slide 14 | AI có chế độ GPT local (unsloth) – không ra ngoài |
| **Độ chính xác** | Slide 5 | Model evaluator (accuracy 89.2%, ROC-AUC 0.94) |

---

## 5️⃣ Emergency backup
- Nếu API trả lỗi auth → refresh token qua `/auth/login`.
- Nếu AI core chưa chạy → restart `docker-compose restart ai-core`.
- Nếu cần “offline story” → mention GPT local + rule-based filter.

---

**Notes:** Luôn mở Postman/HTTPie dự phòng. Khi trả lời Q&A, dẫn lại 3 good points + nỗi đau tương ứng. 

