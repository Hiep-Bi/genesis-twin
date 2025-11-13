# Genesis Twin - Project Structure Guide

## 📁 Directory Organization

```
genesis-twin/
│
├── 📂 backend/                     # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                   # REST API Endpoints
│   │   │   ├── auth.py           # Authentication (login, register)
│   │   │   ├── machines.py       # Machine management
│   │   │   ├── sensors.py        # Sensor data endpoints
│   │   │   ├── production.py     # Production tracking
│   │   │   ├── analytics.py      # Analytics & reports
│   │   │   ├── ai_predictions.py # Enhanced AI predictions
│   │   │   ├── traceability.py   # QR code traceability
│   │   │   └── advanced_features.py # Autonomous, Orchestration, ESG
│   │   │
│   │   ├── core/                  # Core Application Logic
│   │   │   ├── config.py         # Configuration management
│   │   │   ├── database.py       # Database connection
│   │   │   ├── security.py       # JWT, password hashing
│   │   │   └── redis_client.py   # Redis pub/sub client
│   │   │
│   │   ├── models/                # SQLAlchemy ORM Models
│   │   │   ├── user.py           # User model
│   │   │   ├── machine.py        # Machine model
│   │   │   ├── production.py     # Production models
│   │   │   └── supplier.py       # Supplier model
│   │   │
│   │   ├── services/              # Business Logic Services
│   │   │   ├── autonomous_control.py    # Auto-adjust machines
│   │   │   ├── orchestration_engine.py  # AGV coordination
│   │   │   └── esg_optimizer.py         # ESG scoring
│   │   │
│   │   ├── websockets/            # WebSocket Handlers
│   │   │   ├── manager.py        # Connection manager
│   │   │   └── ws_handler.py     # WebSocket routes
│   │   │
│   │   └── main.py                # FastAPI application entry
│   │
│   ├── Dockerfile                 # Backend container
│   └── requirements.txt           # Python dependencies
│
├── 📂 frontend/                    # React Frontend Application
│   ├── src/
│   │   ├── components/            # Reusable Components
│   │   │   ├── Auth/             # Auth components
│   │   │   │   └── ProtectedRoute.js
│   │   │   └── Layout/           # Layout components
│   │   │       └── MainLayout.js
│   │   │
│   │   ├── pages/                 # Page Components
│   │   │   ├── Login.js          # Login page
│   │   │   ├── Dashboard.js      # Main dashboard
│   │   │   ├── Machines.js       # Machine management
│   │   │   ├── Energy.js         # Energy monitoring
│   │   │   ├── Production.js     # Production tracking
│   │   │   ├── Analytics.js      # Analytics & reports
│   │   │   ├── QRScanner.js      # QR traceability
│   │   │   └── AdvancedFeatures.js # Advanced AI features
│   │   │
│   │   ├── services/              # API & WebSocket Services
│   │   │   ├── api.js            # Axios API client
│   │   │   ├── authContext.js    # Auth context provider
│   │   │   └── websocket.js      # WebSocket client
│   │   │
│   │   ├── App.js                 # Main App component
│   │   ├── index.js               # React entry point
│   │   └── index.css              # Global styles
│   │
│   ├── public/
│   │   └── index.html             # HTML template
│   ├── Dockerfile                 # Frontend container
│   └── package.json               # Node dependencies
│
├── 📂 ai-core/                     # AI Prediction Engine
│   ├── data/                      # Historical Data
│   │   ├── Production System Dataset.csv
│   │   └── maintenance_history_with_type.csv
│   │
│   ├── enhanced_gemini_client.py  # Enhanced AI predictions
│   ├── gemini_client.py           # Basic Gemini client
│   ├── prediction_engine.py       # Prediction engine logic
│   ├── config.py                  # AI Core config
│   ├── main.py                    # AI Core entry point
│   ├── Dockerfile                 # AI Core container
│   └── requirements.txt           # Python dependencies
│
├── 📂 digital-twin/                # Real-time Simulation Engine
│   ├── simulator.py               # Physics simulation
│   ├── Dockerfile                 # Digital Twin container
│   └── requirements.txt           # Python dependencies
│
├── 📂 data-generator/              # Mock Data Generators
│   ├── sensor_simulator.py        # Sensor data generation
│   ├── machine_simulator.py       # Machine state simulation
│   ├── qr_scanner_sim.py          # QR scan events
│   ├── energy_simulator.py        # Energy consumption
│   ├── generate_data.py           # Main data generator
│   ├── Dockerfile                 # Data Generator container
│   └── requirements.txt           # Python dependencies
│
├── 📂 database/                    # Database Schema
│   └── schema.sql                 # PostgreSQL schema
│
├── 📂 scripts/                     # Utility & Test Scripts
│   ├── test_advanced_features.py  # Automated test suite
│   └── test_advanced_ai.json      # Test data
│
├── docker-compose.yml              # Multi-container orchestration
├── .gitignore                      # Git ignore rules
├── .env.example                    # Environment variables template
└── README.md                       # Project documentation
```

---

## 🔗 Service Communication

```
┌─────────────────┐
│   Frontend      │ (Port 3000)
│   React + MUI   │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│   Backend       │ (Port 8000)
│   FastAPI       │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬───────────┐
    ▼         ▼         ▼           ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌─────────┐
│AI Core │ │Redis │ │Postgres│ │Digital  │
│        │ │      │ │        │ │Twin     │
│(8001)  │ │(6379)│ │(5432)  │ │(8001)   │
└────────┘ └──────┘ └────────┘ └─────────┘
```

---

## 🚀 Key Components

### Backend (FastAPI)
- **Purpose**: REST API gateway, WebSocket server, business logic
- **Port**: 8000
- **Language**: Python 3.11+
- **Key Libraries**: FastAPI, SQLAlchemy, Redis, JWT

### Frontend (React)
- **Purpose**: User interface, real-time dashboard
- **Port**: 3000
- **Language**: JavaScript (React)
- **Key Libraries**: Material-UI, Chart.js, Axios, WebSocket

### AI Core (Gemini)
- **Purpose**: Predictive maintenance, root cause analysis
- **Port**: 8001 (optional)
- **Language**: Python 3.11+
- **Key Libraries**: Google Generative AI, Pandas, NumPy

### Digital Twin
- **Purpose**: Real-time factory simulation
- **Port**: 8001
- **Language**: Python 3.11+
- **Key Libraries**: NumPy, Physics simulation

### Database (PostgreSQL + TimescaleDB)
- **Purpose**: Persistent storage, time-series data
- **Port**: 5432
- **Extension**: TimescaleDB for time-series optimization

### Cache (Redis)
- **Purpose**: Caching, pub/sub for real-time updates
- **Port**: 6379

---

## 📝 Environment Variables

### Backend (.env)
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
GEMINI_API_KEY=your-gemini-api-key

# App
ENVIRONMENT=production
DEBUG=False
```

---

## 🛠️ Development Workflow

### 1. Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start

# AI Core
cd ai-core
pip install -r requirements.txt
python main.py
```

### 2. Docker Development
```bash
docker-compose up -d
docker-compose logs -f backend  # View logs
docker-compose restart backend  # Restart service
```

### 3. Testing
```bash
cd scripts
python test_advanced_features.py
```

---

## 📦 Deployment

### Production Deployment
1. Update `.env` with production values
2. Set `DEBUG=False` in backend config
3. Configure CORS origins
4. Set up HTTPS (Nginx + Let's Encrypt)
5. Use production database
6. Deploy with `docker-compose -f docker-compose.prod.yml up -d`

### Cloud Deployment (AWS/Azure/GCP)
- Use managed PostgreSQL (RDS, Azure Database, Cloud SQL)
- Use managed Redis (ElastiCache, Azure Cache, Memorystore)
- Deploy containers to ECS/Kubernetes/App Service
- Use CDN for frontend static files
- Set up load balancer for backend

---

## 🔐 Security Checklist

- [x] JWT authentication
- [x] Password hashing (bcrypt)
- [x] CORS configuration
- [x] SQL injection protection (SQLAlchemy ORM)
- [x] XSS protection (React auto-escaping)
- [ ] Rate limiting (add in production)
- [ ] HTTPS/TLS (required for production)
- [ ] API key rotation
- [ ] Database encryption at rest

---

## 📊 Monitoring & Logging

### Logs Location
- Backend: `backend/logs/`
- AI Core: `ai-core/logs/`
- Frontend: Browser console
- Docker: `docker-compose logs`

### Metrics to Monitor
- API response time (< 100ms)
- WebSocket latency (< 50ms)
- Database query time (< 50ms)
- AI prediction time (< 2s)
- Error rate (< 1%)
- CPU & Memory usage
- Active WebSocket connections

---

## 🚨 Troubleshooting

### Backend won't start
- Check DATABASE_URL in `.env`
- Verify PostgreSQL is running
- Check Redis connection

### Frontend can't connect
- Verify REACT_APP_API_URL is correct
- Check CORS settings in backend
- Ensure backend is running

### AI predictions fail
- Verify GEMINI_API_KEY is valid
- Check API rate limits
- Review ai-core logs

---

## 📚 Documentation Links

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub Wiki**: (Add your wiki link)
- **Postman Collection**: (Export and add link)

---

*Last Updated: 2025-01-13*

