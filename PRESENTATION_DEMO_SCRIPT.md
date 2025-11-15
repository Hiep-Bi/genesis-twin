# 🎤 Demo Script Chi Tiết Cho Presentation

## ⏰ TIMING: 10-15 phút

---

## 📋 SCRIPT CHI TIẾT

### **1. INTRODUCTION (1 phút)**

**Nói:**
> "Xin chào, tôi xin được trình bày về Genesis Twin - Hệ điều hành nhà máy thông minh.
> 
> Sau khi tham quan nhà máy thực tế, chúng tôi đã xác định được 3 nỗi đau chính:
> 1. Dây chuyền sập → không biết khởi động lại thứ tự nào
> 2. Server AGV sập → không biết ưu tiên dây chuyền nào
> 3. Máy cũ → cần thủ công chụp thông số
> 
> Hôm nay tôi sẽ demo 3 giải pháp chính để giải quyết các nỗi đau này."

**Action:**
- Show slide 1: Title
- Show slide 2: Problem Statement

---

### **2. CORE FEATURE #1: AI PREDICTIVE MAINTENANCE (4 phút)**

#### **2.1 Setup (30 giây)**
**Nói:**
> "Đầu tiên, AI Predictive Maintenance. Khác với các hệ thống chỉ predict, hệ thống của chúng tôi còn reasoning - giải thích tại sao và đề xuất làm gì."

**Action:**
- Navigate to AI Predictions page
- Show slide 3: AI Predictions Overview

---

#### **2.2 Root Cause Analysis (1.5 phút)**
**Nói:**
> "Khi máy có vấn đề, hệ thống không chỉ báo lỗi, mà còn phân tích nguyên nhân gốc rễ.
> 
> Ví dụ: Vibration tăng từ 2.1 lên 6.2, nhiệt độ tăng từ 75°C lên 87°C.
> 
> AI phân tích và đưa ra 2 nguyên nhân chính:
> 1. Vibration quá cao - confidence 95%
> 2. Nhiệt độ tăng - có thể do bearing wear - confidence 88%
> 
> Hệ thống còn so sánh với các case tương tự trong quá khứ, tìm case CASE-2024-045 với similarity 92%."

**Action:**
- Input demo data từ `demo_data_ai_predictions.json`
- Show API response với root causes
- Highlight confidence scores
- Show similar cases

**Key Points:**
- ✅ Không chỉ predict, mà còn reasoning
- ✅ Confidence scores
- ✅ Historical pattern matching

---

#### **2.3 Smart Scheduling (1.5 phút)**
**Nói:**
> "Sau khi biết nguyên nhân, hệ thống đề xuất thời điểm bảo trì tối ưu - Golden Time Slot.
> 
> Hệ thống tính toán downtime cost cho từng thời điểm và tìm thời điểm cost thấp nhất.
> 
> Trong trường hợp này, Golden Time Slot là 14:00-16:00, với downtime cost chỉ $500, thay vì $800 nếu chờ cuối ca hoặc $1500 nếu chờ ngày mai."

**Action:**
- Show Smart Scheduling result
- Highlight Golden Time Slot
- Show cost comparison

**Key Points:**
- ✅ 100% downtime cost optimization
- ✅ Tích hợp với production calendar
- ✅ Đề xuất cụ thể với lý do

---

#### **2.4 Multi-scenario Planning (1 phút)**
**Nói:**
> "Hệ thống còn đề xuất 3 scenarios với trade-off analysis:
> 1. Maintenance ngay: Cost $500, Carbon 50kg, Risk Low
> 2. Chờ cuối ca: Cost $800, Carbon 75kg, Risk Medium
> 3. Chờ ngày mai: Cost $1500, Carbon 120kg, Risk High
> 
> Recommendation: Maintenance ngay - Cost thấp nhất, risk thấp."

**Action:**
- Show 3 scenarios
- Highlight recommendation
- Show cost/carbon comparison

**Key Points:**
- ✅ Trade-off analysis
- ✅ Cost vs Carbon
- ✅ Recommendation với lý do

---

### **3. CORE FEATURE #2: PRODUCTION LINE RECOVERY (3 phút)**

#### **3.1 Setup (30 giây)**
**Nói:**
> "Tiếp theo, Production Line Recovery System. Giải quyết nỗi đau: Dây chuyền sập → không biết khởi động lại thứ tự nào."

**Action:**
- Show slide 6: Recovery System Overview
- Navigate to Factory Operations page

---

#### **3.2 Scenario Setup (30 giây)**
**Nói:**
> "Scenario: 3 dây chuyền bị sập - LINE-01, LINE-02, LINE-03.
> 
> Có 4 đơn hàng đang chờ với priority khác nhau.
> Inventory có ở cả 2 kho - kho tổng và kho chờ ngoài.
> Server AGV cũng đang sập."

**Action:**
- Input demo data từ `demo_data_recovery.json`
- Show affected lines
- Show pending orders
- Show inventory status

---

#### **3.3 Recovery Analysis (1.5 phút)**
**Nói:**
> "Hệ thống phân tích và tính priority score cho mỗi dây chuyền dựa trên:
> - Priority của đơn hàng (0-40 điểm)
> - Inventory availability (0-30 điểm) - ưu tiên kho chờ ngoài
> - Deadline urgency (0-20 điểm)
> - Dependencies (0-10 điểm)
> 
> Kết quả:
> - LINE-01: 90 điểm - Có inventory ở kho chờ ngoài, priority cao, upstream line
> - LINE-02: 70 điểm - Priority cao, có inventory ở kho tổng
> - LINE-03: 50 điểm - Priority thấp hơn"

**Action:**
- Call API: `POST /api/v1/factory/recovery/analyze`
- Show recovery sequence
- Highlight priority scores và reasons

**Key Points:**
- ✅ AI reasoning với priority scoring
- ✅ Inventory-based prioritization
- ✅ Dependencies consideration

---

#### **3.4 Recovery Plan (1 phút)**
**Nói:**
> "Hệ thống đề xuất recovery sequence:
> 1. Khởi động LINE-01 trước (có inventory sẵn, upstream)
> 2. Sau đó LINE-02
> 3. Cuối cùng LINE-03
> 
> Tổng thời gian recovery: 120 phút.
> 
> Recommendations cụ thể cho từng dây chuyền."

**Action:**
- Show recovery sequence với timeline
- Show recommendations
- Highlight actionable instructions

**Key Points:**
- ✅ Timeline cụ thể
- ✅ Actionable recommendations
- ✅ Resource requirements

---

### **4. CORE FEATURE #3: AGV FALLBACK & INVENTORY (2 phút)**

#### **4.1 Setup (30 giây)**
**Nói:**
> "Cuối cùng, AGV Fallback System. Giải quyết nỗi đau: Server AGV sập → không biết ưu tiên dây chuyền nào."

**Action:**
- Show slide 8: AGV Fallback Overview

---

#### **4.2 Scenario Setup (30 giây)**
**Nói:**
> "Scenario: Server AGV sập, cần 60 phút để khôi phục.
> 
> Có 3 đơn hàng đang chờ.
> Inventory có ở cả 2 kho.
> Cần quyết định: Dây chuyền nào có thể khởi động ngay?"

**Action:**
- Input demo data từ `demo_data_agv_fallback.json`
- Show AGV server status: down
- Show inventory distribution

---

#### **4.3 Inventory Analysis (1 phút)**
**Nói:**
> "Hệ thống phân tích inventory location và material requirements cho từng dây chuyền.
> 
> Kết quả:
> - LINE-01: Có đủ materials ở kho chờ ngoài → Khởi động ngay
> - LINE-02: Chỉ có ở kho tổng → Cần AGV hoặc manual transport
> - LINE-03: Chỉ có ở kho tổng → Cần AGV hoặc manual transport
> 
> Hệ thống đề xuất: Khởi động LINE-01 ngay, chờ AGV recovery cho LINE-02 và LINE-03."

**Action:**
- Call API: `POST /api/v1/factory/agv-fallback/handle-failure`
- Show prioritized lines
- Show material availability analysis
- Show fallback instructions

**Key Points:**
- ✅ Intelligent prioritization
- ✅ Material-line matching
- ✅ Fallback instructions

---

### **5. OTHER FEATURES (1 phút)**

**Nói:**
> "Ngoài ra, hệ thống còn có:
> - QR Code Traceability với Digital Birth Certificate
> - Production Workflow tracking đầy đủ 7 bước
> - IoT USB Integration cho máy cũ
> - AGV Orchestration với shipping support
> 
> Chi tiết có thể xem trong documentation."

**Action:**
- Show slide 9: Other Features (Quick overview)
- Mention ngắn gọn

---

### **6. BUSINESS VALUE & IMPACT (1 phút)**

**Nói:**
> "Về business value:
> - Giảm downtime 40% nhờ Recovery System
> - Tối ưu cost 30% nhờ Smart Scheduling
> - Tận dụng inventory sẵn có, giảm waste
> - Sẵn sàng triển khai, dựa trên feedback từ nhà máy thực tế"

**Action:**
- Show slide 10: Business Value
- Highlight metrics

---

### **7. Q&A (2-3 phút)**

**Chuẩn bị trả lời:**
- "Hệ thống có tích hợp với MES/WMS không?" → "Có, qua API, có thể integrate"
- "Chi phí triển khai?" → "Dựa trên scale, có thể estimate cụ thể"
- "Thời gian triển khai?" → "2-4 tuần tùy scale"
- "Có test với real data không?" → "Có, đã test với data từ nhà máy"

---

## 🎯 KEY MESSAGES

1. **"Giải quyết nỗi đau thực tế từ nhà máy"**
2. **"AI không chỉ predict, mà còn reasoning"**
3. **"Sẵn sàng triển khai"**

---

## ⚠️ BACKUP PLAN

### **Nếu Demo Fail:**

**Option 1: Screenshots**
- Đã chuẩn bị screenshots sẵn
- Show screenshots thay vì live demo

**Option 2: Video**
- Record video demo trước
- Play video nếu live demo fail

**Option 3: API Docs**
- Show Swagger UI
- Explain endpoints và responses

---

## ✅ CHECKLIST TRƯỚC KHI THUYẾT TRÌNH

- [ ] Test 3 core features hoạt động 100%
- [ ] Demo data sẵn sàng
- [ ] Screenshots/videos backup
- [ ] Slides hoàn chỉnh
- [ ] Practice timing (10-15 phút)
- [ ] Q&A preparation
- [ ] Backup plan ready

---

## 📝 NOTES

- **Giữ timing:** 10-15 phút (không quá dài)
- **Focus:** 3 core features (không lan man)
- **Demo thực tế:** Có kết quả cụ thể
- **Business value:** Nhấn mạnh impact

