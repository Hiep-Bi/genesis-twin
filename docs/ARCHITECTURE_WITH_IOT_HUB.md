# 🏗️ Architecture với IoT Hub

## 📊 Kiến Trúc Mới (Có IoT Hub)

```
┌─────────────────────────────────────────────────────────────┐
│                    SENSORS & MACHINES                         │
│  (Máy móc, AGV, Robots - Gửi tín hiệu mỗi giây)            │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    🚪 IoT HUB (NEW!)                          │
│  - Nhận TẤT CẢ tín hiệu                                      │
│  - Lọc data lỗi                                             │
│  - Aggregate (tính trung bình)                              │
│  - Chỉ lưu data quan trọng (≥5% change)                    │
│  → Giảm 80-90% data lưu vào DB                              │
└────────────────────────┬──────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            ↓                         ↓
┌──────────────────────┐    ┌──────────────────────┐
│   DATABASE           │    │   REDIS (Pub/Sub)     │
│  (Chỉ lưu 10-20%     │    │  (Real-time data)     │
│   data quan trọng)   │    │  → WebSocket          │
└──────────────────────┘    └──────────┬───────────┘
                                       │
                                       ↓
                              ┌──────────────────────┐
                              │   DASHBOARD          │
                              │  (Mượt mà, không    │
                              │   giật lag)          │
                              └──────────────────────┘
```

---

## 🔄 Data Flow

### **1. Sensor → IoT Hub**

```
Máy móc gửi: 100 tín hiệu/giây
    ↓
IoT Hub nhận: TẤT CẢ
    ↓
IoT Hub xử lý:
  - Validate (loại bỏ data lỗi)
  - Aggregate (10 tín hiệu → 1 giá trị trung bình)
  - Check change (chỉ lưu nếu ≥5% thay đổi)
```

### **2. IoT Hub → Database**

```
IoT Hub quyết định:
  - Data có thay đổi ≥5%? → Lưu vào DB
  - Data không đổi? → Bỏ qua
    ↓
Database chỉ nhận: 10-20 tín hiệu/giây
  (Giảm 80-90% so với ban đầu)
```

### **3. IoT Hub → Dashboard (Real-time)**

```
IoT Hub forward: TẤT CẢ data (đã validate)
    ↓
Redis Pub/Sub: Phát sóng nhanh
    ↓
WebSocket: Kết nối trực tiếp
    ↓
Dashboard: Nhận real-time, render mượt mà
```

---

## 📈 Performance Metrics

| Metric | Trước (Không IoT Hub) | Sau (Có IoT Hub) | Improvement |
|--------|----------------------|------------------|-------------|
| **Data vào DB** | 100 tín hiệu/giây | 10-20 tín hiệu/giây | **↓ 80-90%** |
| **Storage** | 100GB/ngày | 10-20GB/ngày | **↓ 80-90%** |
| **Dashboard Latency** | 500-1000ms | <100ms | **↓ 80-90%** |
| **Lag/Jitter** | Có (thường xuyên) | Không | **✅ Fixed** |

---

## 🎯 Key Benefits

1. **✅ Giảm 80-90% Storage** → Tiết kiệm chi phí
2. **✅ Dashboard mượt mà** → Không giật lag
3. **✅ Real-time vẫn đảm bảo** → Data đến ngay lập tức
4. **✅ Scalable** → Có thể mở rộng không giới hạn

---

**Last Updated:** 2025-01-13

