# OMAYA Platform - Technical Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Model Performance](#model-performance)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Sensor Integration](#sensor-integration)
- [API Reference](#api-reference)
- [Module Documentation](#module-documentation)
- [Deployment](#deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Overview

The OMAYA Platform is an enterprise-grade IoT/IIoT solution for real-time monitoring, predictive maintenance, and intelligent management of industrial machine fleets. It provides AI-powered analytics, real-time telemetry streaming, and comprehensive monitoring capabilities.

### Key Features

- **Real-time Fleet Monitoring**: Monitor 120+ machines across multiple production zones
- **AI-Powered Predictive Maintenance**: TensorFlow LSTM models predict failures before they occur
- **Live Telemetry Streaming**: WebSocket-based real-time sensor data with 3-second refresh intervals
- **Advanced Analytics**: SHAP/LIME explainability, model drift detection, online learning
- **Enterprise Integration**: Multi-region deployment, audit trails, data lake, secrets management
- **Comprehensive Monitoring**: Prometheus, Grafana, Alertmanager with custom dashboards
- **Industrial Connectivity**: MQTT, OPC-UA, Modbus, Siemens S7, Fanuc FOCAS, Heidenhain LSV2

### Technology Stack

- **Frontend**: React 18.2.0, TypeScript 5.8.2, Vite 7.1.12, TailwindCSS 3.4.1
- **Backend**: Python 3.11, FastAPI 0.109.0, Uvicorn 0.27.0
- **Database**: TimescaleDB (PostgreSQL with time-series extension)
- **Cache**: Redis 7-alpine
- **Messaging**: Apache Kafka 7.5.0
- **Monitoring**: Prometheus, Grafana, Alertmanager
- **AI/ML**: TensorFlow 2.15.0, Scikit-learn 1.3.2
- **Utilities**: curl 8.5.0 (Docker Health Checks)

---

## Model Performance

### Failure Prediction (LSTM)
| Metric | Value |
|--------|-------|
| Accuracy | 93.2% |
| Precision | 91.4% |
| Recall | 89.7% |
| F1-score | 90.5% |

### Remaining Useful Life (RUL)
| Model | MAE (Hours) |
|-------|-------------|
| Ensemble | 12.4 |

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        OMAYA Platform                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Frontend   │    │   Backend    │    │   Database   │      │
│  │              │    │              │    │              │      │
│  │  React + TS  │◄──►│   FastAPI    │◄──►│  TimescaleDB │      │
│  │  Vite + Tail │    │   Python     │    │  PostgreSQL  │      │
│  │  Radix UI    │    │   WebSocket  │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │              │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Browser    │    │    Redis     │    │    Kafka     │      │
│  │              │    │   Cache      │    │  Streaming   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                             │                   │
│                                             ▼                   │
│                                    ┌──────────────┐             │
│                                    │   MinIO      │             │
│                                    │  Data Lake   │             │
│                                    └──────────────┘             │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                    Monitoring & Security Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Prometheus│  │ Grafana  │  │  Vault   │  │  Alert   │       │
│  │ Metrics  │  │Dashboards│  │ Secrets  │  │ Manager  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Sensors** → **Kafka** (Telemetry data)
2. **Kafka** → **FastAPI** (Processing)
3. **FastAPI** → **TimescaleDB** (Storage)
4. **FastAPI** → **AI Models** (Prediction)
5. **AI Models** → **Redis** (Cache results)
6. **FastAPI** → **WebSocket** (Real-time updates)
7. **WebSocket** → **Frontend** (Display)

---

## Quick Start

### Prerequisites

- Docker 20.x or higher
- Docker Compose 2.x or higher
- Node.js 18.x or higher (for development)
- Python 3.11 or higher (for development)

### Quick Start (Development)

```bash
# Clone the repository
git clone https://github.com/Def-Coms/OMAYA-industrial.git
cd OMAYA-industrial

# Start core services
docker-compose -f docker-compose.dev.yml up -d

# Access the platform
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Full Stack Start

```bash
# Start all services including monitoring
docker-compose up -d

# Access monitoring services
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
# MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
# Vault: http://localhost:8200
```

---

## Installation

For detailed installation instructions, see [Installation Guide](./guides/INSTALLATION.md).

### System Requirements

- **Minimum**: 4 CPU cores, 8GB RAM, 50GB storage
- **Recommended**: 8 CPU cores, 16GB RAM, 100GB storage
- **Production**: 16+ CPU cores, 32GB+ RAM, 500GB+ SSD storage

### Supported Platforms

- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- Windows 10/11 with WSL2
- macOS 11+ with Docker Desktop

---

## Configuration

For detailed configuration options, see [Configuration Guide](./guides/CONFIGURATION.md).

### Environment Variables

Key environment variables for the backend:

```env
# Database
TIMESCALE_HOST=timescaledb
TIMESCALE_PORT=5432
TIMESCALE_USER=omaya_user
TIMESCALE_PASSWORD=omaya_password
TIMESCALE_DB=omaya_monitoring

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Vault
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=dev-token

# Security
JWT_SECRET=your-secret-key
TLS_CERT_PATH=/path/to/cert.pem
TLS_KEY_PATH=/path/to/key.pem
```

---

## Sensor Integration

For detailed sensor integration instructions, see [Sensor Integration Guide](./guides/SENSOR_INTEGRATION.md).

### Supported Sensor Types

- **Temperature Sensors**: PT100, PT1000, Thermocouples
- **Vibration Sensors**: Accelerometers, Velocity sensors
- **Pressure Sensors**: Industrial pressure transducers
- **Flow Sensors**: Flow meters, flow sensors
- **Position Sensors**: Encoders, linear scales
- **Current/Voltage Sensors**: Power monitoring sensors

### Sensor Communication Protocols

- **Modbus TCP/IP**: Industrial standard protocol
- **OPC UA**: Modern industrial communication
- **MQTT**: Lightweight messaging protocol
- **HTTP/REST**: Web-based sensor APIs
- **Serial/RS485**: Legacy sensor communication

---

## API Reference

For complete API documentation, see [API Documentation](./api/API_REFERENCE.md).

### Core Endpoints

#### Health & Status
- `GET /` - Service information
- `GET /health` - Health check
- `GET /api/self-test` - System self-test

#### Machine Management
- `GET /api/machines` - List all machines
- `GET /api/machines/{id}` - Get machine details
- `POST /api/machines/{id}/status` - Update machine status

#### Alerts
- `GET /api/alerts` - List alerts
- `POST /api/alerts` - Create alert
- `PUT /api/alerts/{id}` - Update alert

#### AI Predictions
- `POST /api/predict/failure` - Predict machine failure
- `GET /api/predict/rul/{id}` - Get remaining useful life

---

## Module Documentation

Detailed documentation for each module:

- [Frontend Modules](./modules/FRONTEND.md)
- [Backend Modules](./modules/BACKEND.md)
- [AI/ML Models](./modules/AI_MODELS.md)
- [Monitoring Modules](./modules/MONITORING.md)
- [Security Modules](./modules/SECURITY.md)

---

## Deployment

For deployment instructions, see [Deployment Guide](./guides/DEPLOYMENT.md).

### Deployment Options

1. **Docker Compose** - Simple containerized deployment
2. **Kubernetes** - Scalable orchestration deployment
3. **Multi-Region** - Global distributed deployment

### Production Checklist

- [ ] Configure TLS/SSL certificates
- [ ] Set up secure authentication
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts
- [ ] Configure log aggregation
- [ ] Test disaster recovery
- [ ] Performance tuning
- [ ] Security audit

---

## Monitoring & Maintenance

### System Monitoring

The platform includes comprehensive monitoring:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notification
- **Custom Metrics**: 20+ platform-specific metrics

### Maintenance Tasks

#### Daily
- Check system health dashboard
- Review critical alerts
- Monitor disk space usage

#### Weekly
- Review performance metrics
- Check AI model drift
- Backup configuration files

#### Monthly
- Update AI models if needed
- Review and optimize database
- Security updates and patches

---

## Troubleshooting

For common issues and solutions, see [Troubleshooting Guide](./guides/TROUBLESHOOTING.md).

### Common Issues

#### Services Not Starting
- Check Docker logs: `docker-compose logs`
- Verify port availability
- Check resource allocation

#### Database Connection Issues
- Verify TimescaleDB is running
- Check connection credentials
- Test network connectivity

#### High Memory Usage
- Review Redis cache configuration
- Check Kafka message backlog
- Optimize database queries

---

## Support

For additional support:
- Documentation: [https://docs.omaya-platform.com](https://docs.omaya-platform.com)
- Issues: [https://github.com/Def-Coms/OMAYA-industrial/issues](https://github.com/Def-Coms/OMAYA-industrial/issues)
- Email: support@omaya-platform.com

---

## License

Enterprise License - See LICENSE file for details.

---

**Version**: 3.1.0
**Last Updated**: June 2026
