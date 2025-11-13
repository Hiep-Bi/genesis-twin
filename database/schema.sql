-- Genesis Twin Database Schema
-- PostgreSQL with TimescaleDB for time-series data

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Users table với role-based access
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'engineer', 'viewer', 'operator')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Refresh tokens for JWT
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE
);

-- Audit log - track all actions
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    details JSONB,
    ip_address INET,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Factory configuration
CREATE TABLE factories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Machine definitions
CREATE TABLE machines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    factory_id UUID REFERENCES factories(id) ON DELETE CASCADE,
    machine_code VARCHAR(50) UNIQUE NOT NULL,
    machine_type VARCHAR(50) NOT NULL, -- CNC, Robot, AGV, Assembly
    name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    year_installed INTEGER,
    specifications JSONB,
    position_x FLOAT,
    position_y FLOAT,
    position_z FLOAT,
    status VARCHAR(20) DEFAULT 'idle', -- idle, running, maintenance, error
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sensor definitions
CREATE TABLE sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id UUID REFERENCES machines(id) ON DELETE CASCADE,
    sensor_code VARCHAR(50) UNIQUE NOT NULL,
    sensor_type VARCHAR(50) NOT NULL, -- temperature, vibration, pressure, energy
    unit VARCHAR(20),
    min_value FLOAT,
    max_value FLOAT,
    threshold_warning FLOAT,
    threshold_critical FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Time-series: Sensor readings
CREATE TABLE sensor_readings (
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    sensor_id UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    value FLOAT NOT NULL,
    quality VARCHAR(20) DEFAULT 'good', -- good, uncertain, bad
    anomaly_score FLOAT DEFAULT 0.0
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('sensor_readings', 'timestamp');

-- Create indexes for faster queries
CREATE INDEX idx_sensor_readings_sensor_id ON sensor_readings(sensor_id, timestamp DESC);
CREATE INDEX idx_sensor_readings_timestamp ON sensor_readings(timestamp DESC);

-- Time-series: Machine states
CREATE TABLE machine_states (
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    oee FLOAT, -- Overall Equipment Effectiveness
    availability FLOAT,
    performance FLOAT,
    quality FLOAT,
    production_count INTEGER DEFAULT 0,
    defect_count INTEGER DEFAULT 0,
    downtime_minutes INTEGER DEFAULT 0
);

SELECT create_hypertable('machine_states', 'timestamp');
CREATE INDEX idx_machine_states_machine_id ON machine_states(machine_id, timestamp DESC);

-- Time-series: Energy consumption
CREATE TABLE energy_consumption (
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    machine_id UUID REFERENCES machines(id) ON DELETE CASCADE,
    energy_kwh FLOAT NOT NULL,
    power_kw FLOAT NOT NULL,
    carbon_emission_kg FLOAT NOT NULL,
    cost_usd FLOAT
);

SELECT create_hypertable('energy_consumption', 'timestamp');
CREATE INDEX idx_energy_consumption_machine_id ON energy_consumption(machine_id, timestamp DESC);

-- Production orders
CREATE TABLE production_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    product_code VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed, cancelled
    priority INTEGER DEFAULT 1,
    scheduled_start TIMESTAMP WITH TIME ZONE,
    scheduled_end TIMESTAMP WITH TIME ZONE,
    actual_start TIMESTAMP WITH TIME ZONE,
    actual_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products manufactured
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    production_order_id UUID REFERENCES production_orders(id),
    product_code VARCHAR(50) NOT NULL,
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    qr_code VARCHAR(255) UNIQUE NOT NULL,
    machine_id UUID REFERENCES machines(id),
    quality_status VARCHAR(20) DEFAULT 'pass', -- pass, fail, rework
    defect_types JSONB,
    manufactured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    inspected_at TIMESTAMP WITH TIME ZONE,
    shipped_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_products_qr_code ON products(qr_code);
CREATE INDEX idx_products_serial_number ON products(serial_number);

-- Suppliers
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    contact_info JSONB,
    rating FLOAT DEFAULT 0.0,
    performance_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Materials/Parts inventory
CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    material_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    supplier_id UUID REFERENCES suppliers(id),
    unit VARCHAR(20),
    unit_price FLOAT,
    carbon_footprint_per_unit FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory tracking với QR scanning
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    material_id UUID REFERENCES materials(id),
    transaction_type VARCHAR(20) NOT NULL, -- receive, consume, return, adjust
    quantity FLOAT NOT NULL,
    qr_code VARCHAR(255),
    scanned_by_robot VARCHAR(50),
    location VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_inventory_qr_code ON inventory_transactions(qr_code);
CREATE INDEX idx_inventory_timestamp ON inventory_transactions(timestamp DESC);

-- Maintenance records
CREATE TABLE maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id UUID REFERENCES machines(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(50) NOT NULL, -- preventive, corrective, predictive
    scheduled_date TIMESTAMP WITH TIME ZONE,
    completed_date TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    cost FLOAT,
    description TEXT,
    performed_by UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Predictions
CREATE TABLE ai_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_type VARCHAR(50) NOT NULL, -- defect, maintenance, energy, supply_chain
    target_id UUID, -- machine_id, product_id, etc.
    prediction_data JSONB NOT NULL,
    confidence_score FLOAT,
    actual_outcome JSONB,
    accuracy FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    prediction_time TIMESTAMP WITH TIME ZONE,
    outcome_time TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_predictions_type_time ON ai_predictions(prediction_type, created_at DESC);

-- Digital Twin States (snapshots)
CREATE TABLE digital_twin_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    factory_id UUID REFERENCES factories(id),
    state_data JSONB NOT NULL, -- Full state snapshot
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts & Notifications
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(50) NOT NULL, -- defect, energy_spike, maintenance, anomaly
    severity VARCHAR(20) NOT NULL, -- info, warning, critical
    title VARCHAR(255) NOT NULL,
    description TEXT,
    source_type VARCHAR(50), -- machine, sensor, ai_prediction
    source_id UUID,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_alerts_severity_time ON alerts(severity, created_at DESC);
CREATE INDEX idx_alerts_unresolved ON alerts(resolved, created_at DESC) WHERE NOT resolved;

-- Settings & Configuration
CREATE TABLE system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION!)
INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES (
    'admin',
    'admin@genesistwin.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5egi9Cd3WqKUy', -- bcrypt hash of 'admin123'
    'System Administrator',
    'admin'
);

-- Insert default factory
INSERT INTO factories (name, location, config)
VALUES (
    'Genesis Factory 01',
    'Virtual Manufacturing Complex',
    '{"area_sqm": 10000, "production_lines": 5, "max_capacity": 10000}'::jsonb
);

-- Create views for analytics
CREATE VIEW machine_performance AS
SELECT 
    m.id,
    m.machine_code,
    m.name,
    AVG(ms.oee) as avg_oee,
    AVG(ms.availability) as avg_availability,
    AVG(ms.performance) as avg_performance,
    AVG(ms.quality) as avg_quality,
    SUM(ms.production_count) as total_production,
    SUM(ms.defect_count) as total_defects
FROM machines m
LEFT JOIN machine_states ms ON m.id = ms.machine_id
WHERE ms.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY m.id, m.machine_code, m.name;

CREATE VIEW energy_summary AS
SELECT 
    m.id,
    m.machine_code,
    m.name,
    SUM(ec.energy_kwh) as total_energy_kwh,
    AVG(ec.power_kw) as avg_power_kw,
    SUM(ec.carbon_emission_kg) as total_carbon_kg,
    SUM(ec.cost_usd) as total_cost_usd
FROM machines m
LEFT JOIN energy_consumption ec ON m.id = ec.machine_id
WHERE ec.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY m.id, m.machine_code, m.name;

-- Continuous aggregates for performance (TimescaleDB feature)
CREATE MATERIALIZED VIEW machine_stats_hourly
WITH (timescaledb.continuous) AS
SELECT 
    machine_id,
    time_bucket('1 hour', timestamp) AS bucket,
    AVG(oee) as avg_oee,
    AVG(availability) as avg_availability,
    AVG(performance) as avg_performance,
    AVG(quality) as avg_quality,
    SUM(production_count) as total_production,
    SUM(defect_count) as total_defects
FROM machine_states
GROUP BY machine_id, bucket;

CREATE MATERIALIZED VIEW energy_stats_hourly
WITH (timescaledb.continuous) AS
SELECT 
    machine_id,
    time_bucket('1 hour', timestamp) AS bucket,
    SUM(energy_kwh) as total_energy,
    AVG(power_kw) as avg_power,
    SUM(carbon_emission_kg) as total_carbon
FROM energy_consumption
GROUP BY machine_id, bucket;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO genesis_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO genesis_user;

