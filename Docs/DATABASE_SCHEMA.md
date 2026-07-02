# Database Schema Documentation

## Table of Contents

- [Overview](#overview)
- [Database Technology](#database-technology)
- [Schema Design](#schema-design)
- [Tables](#tables)
- [Hypertables](#hypertables)
- [Indexes](#indexes)
- [Retention Policies](#retention-policies)
- [Data Model](#data-model)
- [Relationships](#relationships)
- [Performance Optimization](#performance-optimization)

---

## Overview

The OMAYA Platform uses TimescaleDB (PostgreSQL extension) for time-series data storage. This document describes the complete database schema, including tables, hypertables, indexes, and retention policies.

## Database Technology

### TimescaleDB

TimescaleDB is chosen for its:
- **Time-series optimization**: Efficient storage and querying of time-series data
- **SQL compatibility**: Full PostgreSQL compatibility with time-series extensions
- **Automatic partitioning**: Hypertables for automatic data partitioning
- **Retention policies**: Automated data lifecycle management
- **Continuous aggregates**: Pre-computed aggregations for faster queries

### Version

- **PostgreSQL**: 15.x
- **TimescaleDB**: Latest (compatible with PostgreSQL 15)

---

## Schema Design

### Database: omaya_monitoring

The main database contains all platform data, organized into:
- **Core tables**: Machines, sensors, users, alerts
- **Time-series hypertables**: Telemetry data, metrics
- **Audit tables**: Audit trails, logs
- **Configuration tables**: Settings, preferences

---

## Tables

### Core Tables

#### machines

Stores machine fleet information.

**Status Update Mechanism**:
The `status` field is **NOT updated from the telemetry pipeline** to avoid frequent writes to the main table. Instead:

1. **Status is computed from telemetry**: Machine status is calculated on-demand from the latest telemetry records
2. **Status is updated manually**: Operators can manually set status (offline, maintenance) via the API
3. **Status is updated by events**: Status changes based on maintenance events, alerts, or manual interventions

**Why this approach**:
- With 120 machines and 3-second updates, automatic status updates would cause 28,800 writes per day to the main table
- Computing status from telemetry is more efficient and provides real-time accuracy
- Manual status updates allow operators to override computed status when needed
- Separation of concerns: telemetry data (facts) vs. machine status (state)

**Status Computation Logic**:
```sql
-- Computed status from latest telemetry
WITH latest_telemetry AS (
  SELECT DISTINCT ON (machine_id) machine_id, sensor_type, value, timestamp
  FROM telemetry
  WHERE timestamp > NOW() - INTERVAL '5 minutes'
  ORDER BY machine_id, timestamp DESC
)
SELECT
  m.id,
  m.name,
  CASE
    WHEN m.status IN ('maintenance', 'offline') THEN m.status  -- Manual override
    WHEN EXISTS (
      SELECT 1 FROM latest_telemetry lt
      WHERE lt.machine_id = m.id
      AND lt.sensor_type = 'temperature'
      AND lt.value > 80
    ) THEN 'error'
    WHEN EXISTS (
      SELECT 1 FROM latest_telemetry lt
      WHERE lt.machine_id = m.id
      AND lt.sensor_type = 'temperature'
      AND lt.value > 60
    ) THEN 'warning'
    WHEN EXISTS (
      SELECT 1 FROM latest_telemetry lt
      WHERE lt.machine_id = m.id
      AND lt.sensor_type = 'vibration'
      AND lt.value > 2.0
    ) THEN 'error'
    ELSE 'operational'
  END AS computed_status
FROM machines m;
```

**Status Values**:
- `operational`: Machine is running normally
- `warning`: Machine has warning conditions (elevated temperature, vibration)
- `error`: Machine has error conditions (critical temperature, vibration)
- `maintenance`: Machine is under maintenance (manual override)
- `offline`: Machine is offline (manual override)

```sql
CREATE TABLE machines (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    zone VARCHAR(100),
    status VARCHAR(50) DEFAULT 'offline',
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    year INTEGER,
    specifications JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_machines_zone ON machines(zone);
CREATE INDEX idx_machines_status ON machines(status);
CREATE INDEX idx_machines_manufacturer ON machines(manufacturer);
```

**Columns**:
- `id`: Unique machine identifier (e.g., M001)
- `name`: Human-readable machine name
- `zone`: Production zone location
- `status`: Current status (offline, operational, maintenance, error)
- `manufacturer`: Equipment manufacturer
- `model`: Machine model
- `year`: Manufacturing year
- `specifications`: JSONB with detailed specifications
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

**Specifications JSONB Structure**:
```json
{
  "spindle_max_rpm": 12000,
  "axis_count": 5,
  "power_rating": "15kW",
  "work_area": {
    "x": 500,
    "y": 400,
    "z": 300
  },
  "tool_capacity": 24
}
```

#### sensors

Stores sensor information and configuration.

```sql
CREATE TABLE sensors (
    id VARCHAR(20) PRIMARY KEY,
    machine_id VARCHAR(20) NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) NOT NULL,
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    serial_number VARCHAR(255),
    protocol VARCHAR(50) NOT NULL,
    location VARCHAR(255),
    connection_params JSONB,
    calibration_params JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sensors_machine_id ON sensors(machine_id);
CREATE INDEX idx_sensors_type ON sensors(sensor_type);
CREATE INDEX idx_sensors_protocol ON sensors(protocol);
```

**Columns**:
- `id`: Unique sensor identifier (e.g., S001)
- `machine_id`: Associated machine ID
- `sensor_type`: Sensor type (temperature, vibration, pressure, etc.)
- `model`: Sensor model
- `manufacturer`: Sensor manufacturer
- `serial_number`: Serial number
- `protocol`: Communication protocol (modbus_tcp, opc_ua, mqtt, http)
- `location`: Physical location on machine
- `connection_params`: JSONB with connection parameters
- `calibration_params`: JSONB with calibration data
- `status`: Sensor status (active, warning, error, offline)

**Connection Params JSONB Structure**:
```json
{
  "host": "192.168.1.100",
  "port": 502,
  "unit_id": 1,
  "register_address": 40001,
  "register_count": 2,
  "scale_factor": 0.1
}
```

**Calibration Params JSONB Structure**:
```json
{
  "offset": 0.0,
  "gain": 1.0,
  "calibration_date": "2024-01-15",
  "reference_points": [
    {"reference": 0.0, "sensor": 0.0},
    {"reference": 100.0, "sensor": 100.0}
  ]
}
```

#### users

Stores user accounts and authentication.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**Columns**:
- `id`: Unique user ID
- `username`: Username
- `email`: Email address
- `password_hash`: Bcrypt password hash
- `role`: User role (admin, operator, viewer, analyst)
- `is_active`: Account status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp

#### alerts

Stores alert information and status.

```sql
CREATE TABLE alerts (
    id VARCHAR(20) PRIMARY KEY,
    machine_id VARCHAR(20) NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_machine_id ON alerts(machine_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(acknowledged, resolved);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
```

**Columns**:
- `id`: Unique alert identifier
- `machine_id`: Associated machine ID
- `severity`: Alert severity (info, warning, error, critical)
- `type`: Alert type (temperature, vibration, pressure, etc.)
- `title`: Alert title
- `message`: Detailed alert message
- `acknowledged`: Alert acknowledgment status
- `acknowledged_by`: User who acknowledged
- `acknowledged_at`: Acknowledgment timestamp
- `resolved`: Resolution status
- `resolved_at`: Resolution timestamp
- `notes`: Additional notes
- `created_at`: Alert creation timestamp
- `updated_at`: Last update timestamp

#### maintenance_events

Stores maintenance scheduling and history.

```sql
CREATE TABLE maintenance_events (
    id VARCHAR(20) PRIMARY KEY,
    machine_id VARCHAR(20) NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    scheduled_date TIMESTAMPTZ NOT NULL,
    estimated_duration INTEGER,
    actual_duration INTEGER,
    status VARCHAR(50) DEFAULT 'scheduled',
    assigned_to VARCHAR(255),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_maintenance_machine_id ON maintenance_events(machine_id);
CREATE INDEX idx_maintenance_scheduled_date ON maintenance_events(scheduled_date);
CREATE INDEX idx_maintenance_status ON maintenance_events(status);
CREATE INDEX idx_maintenance_type ON maintenance_events(type);
```

**Columns**:
- `id`: Unique maintenance event identifier
- `machine_id`: Associated machine ID
- `type`: Maintenance type (preventive, corrective, predictive)
- `scheduled_date`: Scheduled date/time
- `estimated_duration`: Estimated duration in hours
- `actual_duration`: Actual duration in hours
- `status`: Status (scheduled, in_progress, completed, cancelled)
- `assigned_to`: Assigned team/person
- `description`: Maintenance description
- `notes`: Additional notes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `completed_at`: Completion timestamp

---

## Hypertables

### telemetry

Stores time-series sensor data (main hypertable).

```sql
CREATE TABLE telemetry (
    id BIGSERIAL PRIMARY KEY,
    machine_id VARCHAR(20) NOT NULL,
    sensor_id VARCHAR(20) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    quality VARCHAR(20) DEFAULT 'good',
    metadata JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('telemetry', 'timestamp', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Create indexes
CREATE INDEX idx_telemetry_machine_id ON telemetry(machine_id);
CREATE INDEX idx_telemetry_sensor_id ON telemetry(sensor_id);
CREATE INDEX idx_telemetry_sensor_type ON telemetry(sensor_type);
CREATE INDEX idx_telemetry_timestamp ON telemetry(timestamp DESC);
CREATE INDEX idx_telemetry_machine_timestamp ON telemetry(machine_id, timestamp DESC);

-- Create composite index for common queries
CREATE INDEX idx_telemetry_machine_sensor_timestamp ON telemetry(machine_id, sensor_id, timestamp DESC);
```

**Columns**:
- `id`: Unique record ID
- `machine_id`: Associated machine ID
- `sensor_id`: Associated sensor ID
- `sensor_type`: Sensor type
- `value`: Sensor reading value
- `unit`: Measurement unit (°C, mm/s, bar, etc.)
- `quality`: Data quality (good, uncertain, bad)
- `metadata`: JSONB with additional metadata
- `timestamp`: Measurement timestamp

**Metadata JSONB Structure**:
```json
{
  "raw_value": 425,
  "calibrated": true,
  "source": "modbus_tcp",
  "batch_id": "batch_001"
}
```

**Hypertable Configuration**:
- **Time column**: timestamp
- **Chunk interval**: 1 day
- **Compression**: Enabled for data older than 7 days
- **Retention**: 90 days by default

### predictions

Stores AI prediction results.

```sql
CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,
    machine_id VARCHAR(20) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    probability DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    estimated_time_to_failure INTEGER,
    risk_level VARCHAR(20),
    recommended_action TEXT,
    model_version VARCHAR(50),
    features JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('predictions', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Create indexes
CREATE INDEX idx_predictions_machine_id ON predictions(machine_id);
CREATE INDEX idx_predictions_type ON predictions(prediction_type);
CREATE INDEX idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX idx_predictions_risk_level ON predictions(risk_level);
```

**Columns**:
- `id`: Unique prediction ID
- `machine_id`: Associated machine ID
- `prediction_type`: Type of prediction (failure, rul, anomaly)
- `probability`: Predicted probability (0-1)
- `confidence`: Model confidence (0-1)
- `estimated_time_to_failure`: Estimated time to failure in hours
- `risk_level`: Risk level (low, medium, high)
- `recommended_action`: Recommended action
- `model_version`: Model version used
- `features`: JSONB with input features
- `timestamp`: Prediction timestamp

**Features JSONB Structure**:
```json
{
  "temperature": 68.5,
  "vibration": 2.1,
  "tool_wear": 75,
  "operating_hours": 3200,
  "cycle_count": 15000
}
```

### kpis

Stores calculated KPI metrics.

```sql
CREATE TABLE kpis (
    id BIGSERIAL PRIMARY KEY,
    machine_id VARCHAR(20),
    zone VARCHAR(100),
    metric_name VARCHAR(50) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('kpis', 'timestamp',
    chunk_time_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Create indexes
CREATE INDEX idx_kpis_machine_id ON kpis(machine_id);
CREATE INDEX idx_kpis_zone ON kpis(zone);
CREATE INDEX idx_kpis_metric_name ON kpis(metric_name);
CREATE INDEX idx_kpis_timestamp ON kpis(timestamp DESC);
```

**Columns**:
- `id`: Unique KPI ID
- `machine_id`: Machine ID (null for fleet-wide KPIs)
- `zone`: Zone (null for fleet-wide KPIs)
- `metric_name`: Metric name (oee, uptime, defect_rate, etc.)
- `metric_value`: Metric value
- `timestamp`: Calculation timestamp

---

## Indexes

### Performance-Critical Indexes

```sql
-- Telemetry queries (most common)
CREATE INDEX idx_telemetry_machine_timestamp ON telemetry(machine_id, timestamp DESC);
CREATE INDEX idx_telemetry_sensor_timestamp ON telemetry(sensor_id, timestamp DESC);

-- Alert queries
CREATE INDEX idx_alerts_active ON alerts(acknowledged, resolved) WHERE acknowledged = FALSE OR resolved = FALSE;

-- Prediction queries
CREATE INDEX idx_predictions_recent ON predictions(machine_id, timestamp DESC) WHERE timestamp > NOW() - INTERVAL '7 days';

-- KPI queries
CREATE INDEX idx_kpis_recent ON kpis(metric_name, timestamp DESC) WHERE timestamp > NOW() - INTERVAL '30 days';
```

---

## Retention Policies

### Telemetry Data Retention

```sql
-- Drop data older than 90 days
SELECT add_retention_policy('telemetry', 
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- Compress data older than 7 days
SELECT add_compression_policy('telemetry',
    INTERVAL '7 days',
    if_not_exists => TRUE
);
```

### Predictions Retention

```sql
-- Drop predictions older than 180 days
SELECT add_retention_policy('predictions',
    INTERVAL '180 days',
    if_not_exists => TRUE
);
```

### KPIs Retention

```sql
-- Drop KPIs older than 365 days
SELECT add_retention_policy('kpis',
    INTERVAL '365 days',
    if_not_exists => TRUE
);
```

### Audit Logs Retention

```sql
-- Keep audit logs for 7 years (compliance)
SELECT add_retention_policy('audit_logs',
    INTERVAL '7 years',
    if_not_exists => TRUE
);
```

---

## Data Model

### Entity Relationship Diagram

```
┌─────────────┐
│   users     │
└──────┬──────┘
       │
       │ (alerts acknowledged_by)
       │
┌──────▼──────┐         ┌──────────────┐
│   alerts    │◄────────│   machines   │
└─────────────┘         └──────┬───────┘
                               │
                               │ (1:N)
                               │
                    ┌──────────▼──────────┐
                    │      sensors       │
                    └──────────┬──────────┘
                               │
                               │ (1:N)
                               │
                    ┌──────────▼──────────┐
                    │     telemetry       │
                    │   (hypertable)      │
                    └─────────────────────┘

┌──────────────┐         ┌──────────────┐
│ maintenance  │◄────────│   machines   │
│   _events    │         └──────────────┘
└──────────────┘

┌──────────────┐         ┌──────────────┐
│  predictions │◄────────│   machines   │
│ (hypertable) │         └──────────────┘
└──────────────┘

┌──────────────┐
│     kpis     │
│ (hypertable) │
└──────────────┘
```

---

## Relationships

### Primary Relationships

- **machines → sensors**: One-to-many (each machine has multiple sensors)
- **machines → alerts**: One-to-many (each machine can have multiple alerts)
- **machines → maintenance_events**: One-to-many (each machine has maintenance events)
- **machines → predictions**: One-to-many (each machine has predictions)
- **sensors → telemetry**: One-to-many (each sensor produces telemetry data)
- **users → alerts**: One-to-many (users acknowledge alerts)

### Cascade Rules

- **ON DELETE CASCADE**: When a machine is deleted, all related sensors, alerts, maintenance events, and predictions are deleted
- **ON UPDATE CASCADE**: When a machine ID is updated, all related records are updated

---

## Performance Optimization

### Continuous Aggregates

```sql
-- Hourly aggregates for telemetry
CREATE MATERIALIZED VIEW telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    machine_id,
    sensor_id,
    sensor_type,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value
FROM telemetry
GROUP BY bucket, machine_id, sensor_id, sensor_type;

-- Daily aggregates for telemetry
CREATE MATERIALIZED VIEW telemetry_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', timestamp) AS bucket,
    machine_id,
    sensor_id,
    sensor_type,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value
FROM telemetry
GROUP BY bucket, machine_id, sensor_id, sensor_type;

-- Refresh policies
SELECT add_continuous_aggregate_policy('telemetry_hourly',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

SELECT add_continuous_aggregate_policy('telemetry_daily',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day'
);
```

### Query Optimization Tips

1. **Use time ranges**: Always include time range in queries
   ```sql
   SELECT * FROM telemetry
   WHERE machine_id = 'M001'
   AND timestamp > NOW() - INTERVAL '1 hour';
   ```

2. **Use continuous aggregates**: For aggregated data, use materialized views
   ```sql
   SELECT * FROM telemetry_hourly
   WHERE bucket > NOW() - INTERVAL '24 hours';
   ```

3. **Limit result sets**: Use LIMIT for large result sets
   ```sql
   SELECT * FROM telemetry
   WHERE machine_id = 'M001'
   ORDER BY timestamp DESC
   LIMIT 1000;
   ```

4. **Use appropriate indexes**: Ensure indexes exist for query patterns
   ```sql
   -- Check index usage
   EXPLAIN ANALYZE SELECT * FROM telemetry WHERE machine_id = 'M001';
   ```

---

## Backup Strategy

### Backup Commands

```bash
# Full backup
pg_dump -U omaya_user -d omaya_monitoring -F c -f backup_$(date +%Y%m%d).dump

# Schema-only backup
pg_dump -U omaya_user -d omaya_monitoring -s -f schema_backup.sql

# Data-only backup
pg_dump -U omaya_user -d omaya_monitorup -a -f data_backup.sql
```

### Restore Commands

```bash
# Restore from backup
pg_restore -U omaya_user -d omaya_monitoring -F c backup_20240619.dump
```

---

## Migration Scripts

### Initial Schema Setup

```sql
-- Run this script to create the initial schema
-- This should be executed after database creation

-- Create tables
CREATE TABLE machines (...);
CREATE TABLE sensors (...);
CREATE TABLE users (...);
CREATE TABLE alerts (...);
CREATE TABLE maintenance_events (...);

-- Create hypertables
CREATE TABLE telemetry (...);
SELECT create_hypertable('telemetry', 'timestamp');

CREATE TABLE predictions (...);
SELECT create_hypertable('predictions', 'timestamp');

CREATE TABLE kpis (...);
SELECT create_hypertable('kpis', 'timestamp');

-- Create indexes
CREATE INDEX idx_machines_zone ON machines(zone);
-- ... (other indexes)

-- Set up retention policies
SELECT add_retention_policy('telemetry', INTERVAL '90 days');
SELECT add_retention_policy('predictions', INTERVAL '180 days');
SELECT add_retention_policy('kpis', INTERVAL '365 days');

-- Set up compression policies
SELECT add_compression_policy('telemetry', INTERVAL '7 days');

-- Create continuous aggregates
CREATE MATERIALIZED VIEW telemetry_hourly WITH (timescaledb.continuous) AS ...;
```

---

## Support

For additional help:
- Documentation: [https://docs.omaya-platform.com](https://docs.omaya-platform.com)
- Issues: [https://github.com/Bunay-1/OMAYA-Project/issues](https://github.com/Bunay-1/OMAYA-Project/issues)
- Email: db-support@omaya-platform.com

---

**Version**: 3.1.0
**Last Updated**: June 2026
