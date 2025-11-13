# Genesis Twin - Zero-Impact Smart Factory OS

<div align="center">

![Genesis Twin](https://img.shields.io/badge/Genesis-Twin-00d9ff?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-00ff88?style=for-the-badge)
![AI Powered](https://img.shields.io/badge/AI-Google%20Gemini-ff006e?style=for-the-badge)

**Tối ưu hóa hôm nay. Kiến tạo ngày mai bền vững.**

[Demo](#-quick-start) · [Features](#-core-features) · [Architecture](#-architecture) · [API Docs](http://localhost:8000/docs)

</div>

---

## 🎯 Overview

**Genesis Twin** là hệ điều hành nhà máy thông minh hoàn chỉnh được xây dựng 100% bằng phần mềm và mô phỏng. Hệ thống tập trung vào 3 trụ cột:

- **🎯 ZERO-DEFECT PRODUCTION** - Tối ưu chi phí & lợi nhuận
- **🌍 ZERO-CARBON MANUFACTURING** - Giảm phát thải & phát triển bền vững
- **🚚 ZERO-DISRUPTION SUPPLY CHAIN** - Vận hành linh hoạt

### ✨ What Makes Us Different

| Feature | Traditional Systems | Genesis Twin |
|---------|-------------------|--------------|
| AI Capability | Predict only | ✅ **Predict + Auto-adjust** |
| Orchestration | Isolated optimization | ✅ **Holistic coordination** |
| ESG | Post-hoc reporting | ✅ **Real-time scoring** |
| Traceability | Basic tracking | ✅ **Digital Birth Certificate** |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React + MUI)                    │
│               Real-time Dashboard & Control                  │
└────────────────────────┬────────────────────────────────────┘
                         │ WebSocket + REST API
┌────────────────────────┴────────────────────────────────────┐
│                  BACKEND (FastAPI)                          │
│          JWT Auth · WebSocket · API Gateway                  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   AI CORE    │  │ DIGITAL TWIN │  │ DATA LAYER   │
│              │  │              │  │              │
│ Gemini API   │  │ Real-time    │  │ PostgreSQL   │
│ Predictions  │  │ Simulation   │  │ TimescaleDB  │
│ Optimization │  │ Physics      │  │ Redis Cache  │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🚀 Core Features

### 1. 🤖 Autonomous Control Loop
- **Auto-detect** anomalies from sensor data
- **Auto-adjust** machine parameters (spindle speed, coolant flow)
- **Safety validation** before execution
- **Closed-loop feedback** monitoring

### 2. 🚚 Orchestration Engine
- **AGV fleet management** (10 AGVs tracked)
- **Intelligent task assignment** (priority + distance + battery)
- **Route optimization** (A* algorithm)
- **Machine coordination** for optimal throughput

### 3. 🌍 Real-time ESG Optimizer
- **Holistic ESG scoring** (Environmental + Social + Governance)
- **Pareto optimization** for Cost/Productivity/Carbon balance
- **5 pre-defined scenarios** with recommendations
- **AAA to C rating** system

### 4. 📱 QR Code Traceability
- **Digital Birth Certificate** for every product
- **Complete journey** (Receiving → Shipping)
- **Environmental impact** tracking per product
- **Print QR codes** for physical labels

### 5. 🔮 Enhanced AI Predictions
- **Root cause analysis** (explains "why" diagnosis)
- **Smart scheduling** with "Golden Time Slot"
- **Multi-scenario planning** with cost/carbon impacts

### 6. ⚡ Energy & Cost Optimization
- **Real-time power consumption** monitoring
- **Peak/off-peak** analysis
- **Carbon footprint** tracking
- **Cost recommendations**

---

## 📦 Project Structure

```
genesis-twin/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   ├── core/              # Config, security, database
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   └── websockets/        # Real-time communication
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   └── services/          # API & WebSocket clients
│   ├── Dockerfile
│   └── package.json
│
├── ai-core/                    # AI Prediction Engine
│   ├── data/                  # Historical data (CSV)
│   ├── enhanced_gemini_client.py
│   ├── prediction_engine.py
│   └── requirements.txt
│
├── digital-twin/               # Real-time Simulation
│   ├── simulator.py
│   └── requirements.txt
│
├── data-generator/             # Mock Data Generators
│   ├── sensor_simulator.py
│   ├── qr_scanner_sim.py
│   └── requirements.txt
│
├── database/                   # Database Schema
│   └── schema.sql
│
├── scripts/                    # Test & Utility Scripts
│   ├── test_advanced_features.py
│   └── test_advanced_ai.json
│
└── docker-compose.yml          # One-command deployment
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Python 3.11+ & Node.js 18+

### 1. Clone & Setup
```bash
git clone https://github.com/your-username/genesis-twin.git
cd genesis-twin
```

### 2. Configure Environment
```bash
# Copy and edit .env file
cp backend/.env.example backend/.env
# Add your Gemini API key
```

### 3. Start All Services
```bash
docker-compose up -d
```

### 4. Access Applications
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Digital Twin:** http://localhost:8001

### 5. Login
- **Username:** `admin@genesis.ai`
- **Password:** `admin123`

---

## 🧪 Testing

### Automated Test Suite
```bash
cd scripts
python test_advanced_features.py
```

### Manual Testing
1. Navigate to **QR Scanner** → Enter `PRD-20250113-ABC789`
2. Go to **Advanced AI** → Test all 3 tabs
3. Check **Dashboard** → View real-time alerts

---

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### QR Traceability
- `GET /api/v1/traceability/trace/{qr_code}` - Trace product journey
- `POST /api/v1/traceability/generate-qr` - Generate QR code
- `GET /api/v1/traceability/qr-image/{qr_code}` - Get QR image

### Autonomous Control
- `POST /api/v1/advanced/autonomous-control/detect-adjust` - Auto-adjust machine
- `GET /api/v1/advanced/autonomous-control/active` - Get active controls

### Orchestration
- `POST /api/v1/advanced/orchestration/assign-agv` - Assign AGV task
- `GET /api/v1/advanced/orchestration/fleet-status` - Get fleet status

### ESG Optimizer
- `POST /api/v1/advanced/esg/calculate-score` - Calculate ESG score
- `GET /api/v1/advanced/esg/simulate-scenarios` - Get optimized scenarios

**Full API Documentation:** http://localhost:8000/docs

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL + TimescaleDB** - Time-series database
- **Redis** - Caching & pub/sub
- **SQLAlchemy** - ORM
- **Google Gemini API** - AI predictions

### Frontend
- **React** - UI library
- **Material-UI** - Component library
- **Chart.js** - Data visualization
- **WebSocket** - Real-time updates

### DevOps
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy

---

## 📈 System Metrics

- ✅ **28 API Endpoints**
- ✅ **8 Frontend Pages**
- ✅ **5 Backend Services**
- ✅ **3 Major Algorithms** (Autonomous control, A* routing, Pareto optimization)
- ✅ **~2,850 lines** of production code

---

## 🔐 Security

- ✅ JWT Authentication
- ✅ Role-based Access Control (RBAC)
- ✅ Password hashing (bcrypt)
- ✅ CORS protection
- ✅ SQL injection protection (SQLAlchemy ORM)

---

## 📝 Environment Variables

Create `backend/.env`:
```env
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/genesis_twin

# Redis
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI
GEMINI_API_KEY=your-gemini-api-key-here

# App
ENVIRONMENT=production
DEBUG=False
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Google Gemini API for AI predictions
- Material-UI for beautiful components
- FastAPI for the amazing web framework
- The open-source community

---

## 📞 Contact

- **Project Link:** https://github.com/your-username/genesis-twin
- **Issues:** https://github.com/your-username/genesis-twin/issues

---

<div align="center">

**Built with ❤️ using FastAPI, React, and Google Gemini AI**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

</div>
