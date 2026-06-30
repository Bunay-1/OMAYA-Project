-- TimescaleDB Initialization Script
-- Creates tables and hypertables for OMAYA Fleet Monitoring

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Machines metadata table
CREATE TABLE IF NOT EXISTS machines (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    zone VARCHAR(50),
    type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'operational',
    last_maintenance TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert some default machines
INSERT INTO machines (id, name, zone, type)
VALUES
    ('OMAYA-001', 'Mill A1', 'Zone A', 'CNC Mill'),
    ('OMAYA-002', 'Lathe B1', 'Zone B', 'CNC Lathe'),
    ('OMAYA-003', 'Drill C1', 'Zone C', 'CNC Drill')
ON CONFLICT (id) DO NOTHING;

-- Machine telemetry table (time-series data)
CREATE TABLE IF NOT EXISTS machine_telemetry (
    time TIMESTAMPTZ NOT NULL,
    machine_id VARCHAR(50) NOT NULL REFERENCES machines(id),
    temperature FLOAT,
    vibration FLOAT,
    spindle_speed INTEGER,
    tool_wear FLOAT,
    power_consumption FLOAT,
    cycle_count INTEGER,
    status VARCHAR(20),
    metadata JSONB
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('machine_telemetry', 'time', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_machine_telemetry_machine_time 
    ON machine_telemetry (machine_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_machine_telemetry_status 
    ON machine_telemetry (status, time DESC);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    machine_id VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    metadata JSONB
);

-- Convert alerts to hypertable
SELECT create_hypertable('alerts', 'time', if_not_exists => TRUE);

-- Create indexes for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_machine 
    ON alerts (machine_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_severity 
    ON alerts (severity, time DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_unresolved 
    ON alerts (resolved, time DESC) WHERE resolved = FALSE;

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    time TIMESTAMPTZ NOT NULL,
    machine_id VARCHAR(50) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    failure_probability FLOAT,
    rul_hours FLOAT,
    confidence FLOAT,
    model_version VARCHAR(50),
    factors JSONB
);

-- Convert to hypertable
SELECT create_hypertable('predictions', 'time', if_not_exists => TRUE);

-- Create index
CREATE INDEX IF NOT EXISTS idx_predictions_machine 
    ON predictions (machine_id, time DESC);

-- Maintenance records
CREATE TABLE IF NOT EXISTS maintenance_records (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    machine_id VARCHAR(50) NOT NULL,
    maintenance_type VARCHAR(50) NOT NULL,
    description TEXT,
    downtime_hours FLOAT,
    cost FLOAT,
    technician VARCHAR(100),
    parts_replaced JSONB,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ
);

-- Convert to hypertable
SELECT create_hypertable('maintenance_records', 'time', if_not_exists => TRUE);

-- Create index
CREATE INDEX IF NOT EXISTS idx_maintenance_machine 
    ON maintenance_records (machine_id, time DESC);

-- Continuous Aggregates for efficient querying

-- 5-minute aggregates for telemetry
CREATE MATERIALIZED VIEW IF NOT EXISTS machine_telemetry_5m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    machine_id,
    AVG(temperature) AS avg_temperature,
    MAX(temperature) AS max_temperature,
    AVG(vibration) AS avg_vibration,
    MAX(vibration) AS max_vibration,
    AVG(spindle_speed) AS avg_spindle_speed,
    AVG(tool_wear) AS avg_tool_wear,
    COUNT(*) AS sample_count
FROM machine_telemetry
GROUP BY bucket, machine_id;

-- Refresh policy (refresh every 1 minute for last 10 minutes of data)
SELECT add_continuous_aggregate_policy('machine_telemetry_5m',
    start_offset => INTERVAL '10 minutes',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE);

-- Hourly aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS machine_telemetry_1h
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    machine_id,
    AVG(temperature) AS avg_temperature,
    MAX(temperature) AS max_temperature,
    MIN(temperature) AS min_temperature,
    AVG(vibration) AS avg_vibration,
    MAX(vibration) AS max_vibration,
    AVG(spindle_speed) AS avg_spindle_speed,
    AVG(tool_wear) AS avg_tool_wear,
    AVG(power_consumption) AS avg_power_consumption,
    SUM(cycle_count) AS total_cycles
FROM machine_telemetry
GROUP BY bucket, machine_id;

-- Refresh policy
SELECT add_continuous_aggregate_policy('machine_telemetry_1h',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

-- Data retention policy (keep raw data for 90 days)
SELECT add_retention_policy('machine_telemetry', INTERVAL '90 days', if_not_exists => TRUE);
SELECT add_retention_policy('alerts', INTERVAL '365 days', if_not_exists => TRUE);
SELECT add_retention_policy('predictions', INTERVAL '180 days', if_not_exists => TRUE);

-- Insert sample data for testing
INSERT INTO machine_telemetry (time, machine_id, temperature, vibration, spindle_speed, tool_wear, status)
VALUES
    (NOW() - INTERVAL '1 hour', 'OMAYA-001', 62.5, 1.2, 10000, 45.0, 'operational'),
    (NOW() - INTERVAL '30 minutes', 'OMAYA-001', 65.3, 1.5, 10200, 46.0, 'operational'),
    (NOW(), 'OMAYA-001', 68.1, 1.8, 10500, 47.0, 'operational'),
    (NOW() - INTERVAL '1 hour', 'OMAYA-002', 58.2, 0.9, 9800, 32.0, 'operational'),
    (NOW() - INTERVAL '30 minutes', 'OMAYA-002', 59.5, 1.0, 9900, 33.0, 'operational'),
    (NOW(), 'OMAYA-002', 75.8, 2.5, 11000, 85.0, 'warning');

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO omaya_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO omaya_user;

-- Users table for authentication and RBAC
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    roles JSONB DEFAULT '["operator"]',
    is_disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Insert default users (password: password123)
-- Hash generated via passlib bcrypt
INSERT INTO users (username, email, hashed_password, roles)
VALUES
    ('admin', 'admin@omaya-monitoring.com', '$2b$12$6kI.cW2J9.0W6ySj7m6u5.N5H2l0E5y9gZ7kG3y8G1W6z5O4G3y8G', '["admin"]'),
    ('supervisor', 'supervisor@omaya-monitoring.com', '$2b$12$6kI.cW2J9.0W6ySj7m6u5.N5H2l0E5y9gZ7kG3y8G1W6z5O4G3y8G', '["supervisor"]'),
    ('operator', 'operator@omaya-monitoring.com', '$2b$12$6kI.cW2J9.0W6ySj7m6u5.N5H2l0E5y9gZ7kG3y8G1W6z5O4G3y8G', '["operator"]')
ON CONFLICT (username) DO NOTHING;

COMMENT ON TABLE machines IS 'Metadata and status for OMAYA machines';
COMMENT ON TABLE machine_telemetry IS 'Time-series telemetry data from OMAYA machines';
COMMENT ON TABLE alerts IS 'Machine alerts and notifications';
COMMENT ON TABLE predictions IS 'AI-generated failure predictions and RUL estimates';
COMMENT ON TABLE maintenance_records IS 'Historical maintenance records';
COMMENT ON TABLE users IS 'User accounts and roles for OMAYA platform';
