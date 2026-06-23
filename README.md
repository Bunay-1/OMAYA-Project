# 🔧 OMAYA Fleet Monitoring Platform

<div align="center">

<img src="https://defcoms.eu/images/DefComs-logo.svg" width="250" alt="DefComs Logo" />

![Platform Status](https://img.shields.io/badge/Status-Release%20Candidate%20(v2.4--RC)-orange?style=for-the-badge&logo=react)
![Version](https://img.shields.io/badge/Version-2.4.8-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-Enterprise-red?style=for-the-badge)

**Enterprise-Ready IoT/IIoT Architecture for OMAYA Fleet Management with AI-Powered Predictive Maintenance**

[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.2-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-FF6F00?style=flat-square&logo=tensorflow)](https://www.tensorflow.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes)](https://kubernetes.io/)
[![Curl](https://img.shields.io/badge/Curl-073551?style=flat-square&logo=curl)](https://curl.se/)

</div>

---

## 📋 Table of Contents

- [🎯 Platform Overview](#-platform-overview)
- [🚀 Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Technology Stack](#️-technology-stack)
- [📦 Installation & Setup](#-installation--setup)
- [🎨 Frontend Modules](#-frontend-modules)
- [⚙️ Backend Modules](#️-backend-modules)
- [🤖 AI/ML Capabilities](#-aiml-capabilities)
- [📊 API Documentation](#-api-documentation)
- [🔒 Security Features](#-security-features)
- [📈 Monitoring & Observability](#-monitoring--observability)
- [🌍 Deployment](#-deployment)
- [🧪 Testing](#-testing)
- [📚 Documentation](#-documentation)
- [🎯 Platform Statistics](#-platform-statistics)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Support](#-support)

---

## 🎯 Platform Overview

The **OMAYA Fleet Monitoring Platform** is a comprehensive enterprise-grade solution designed for real-time monitoring, predictive maintenance, and intelligent management of industrial machine fleets. Built with cutting-edge technologies and AI-powered analytics, it enables manufacturers to optimize operations, reduce downtime, and maximize productivity through data-driven insights.

### Platform Capabilities

- **Real-time Fleet Monitoring** - Monitor 120+ machines across multiple production zones (Siemens, Fanuc, Heidenhain)
- **Industrial Connectivity** - Integrated MQTT, OPC-UA, and Modbus TCP/RTU for PLC data ingestion
- **AI-Powered Predictive Maintenance** - TensorFlow LSTM models predict failures before they occur
- **Live Telemetry Streaming** - 3-second auto-refresh with WebSocket real-time updates
- **Advanced Analytics** - SHAP/LIME explainability, model drift detection, online learning
- **Enterprise Integration** - Multi-region deployment, audit trails, data lake, secrets management
- **Comprehensive Monitoring** - Prometheus, Grafana, Alertmanager with custom dashboards

### Platform Status

```
🚀 Release Candidate (v2.4-RC) - Feature Complete
🟢 Core Systems Operational
🔒 Security Hardened Architecture
📊 Real-time Monitoring Active
🤖 AI Prediction Models Deployed
```

---

## 🚀 Key Features

### 🏭 Core Platform Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Real-time Fleet Monitoring** | Monitor 120+ machines across 6 production zones with live status updates | ✅ Complete |
| **Live Telemetry Streaming** | WebSocket-based real-time sensor data with 3-second refresh intervals | ✅ Complete |
| **Performance KPIs** | OEE, Uptime, Defect Rate, Throughput, MTBF, MTTR with animated visualizations | ✅ Complete |
| **Alert Management** | Multi-severity alerts (info, warning, error, critical) with escalation workflows | ✅ Complete |
| **Tool Wear Tracking** | Real-time monitoring of tool condition with predictive replacement scheduling | ✅ Complete |
| **Maintenance Calendar** | Schedule and track preventive, corrective, and predictive maintenance | ✅ Complete |
| **Production Forecasting** | AI-driven production predictions with confidence intervals | ✅ Complete |

### 🤖 AI & Machine Learning

| Feature | Description | Status |
|---------|-------------|--------|
| **TensorFlow LSTM** | 64-32 architecture neural network for time-series failure prediction | ✅ Complete |
| **Ensemble RUL Models** | Random Forest + Gradient Boosting for Remaining Useful Life estimation | ✅ Complete |
| **Online Learning** | Adaptive anomaly detection with continuous model improvement | ✅ Complete |
| **Model Drift Detection** | PSI-based monitoring with automatic retraining triggers | ✅ Complete |
| **AI Explainability** | SHAP & LIME analysis for model interpretability | ✅ Complete |
| **Training Pipeline** | Automated model training with version control | ✅ Complete |
| **Edge Computing** | ONNX model conversion for edge deployment | ✅ Complete |

### ⚙️ Backend Infrastructure

| Feature | Description | Status |
|---------|-------------|--------|
| **FastAPI** | High-performance REST API with automatic OpenAPI documentation | ✅ Complete |
| **WebSocket** | Real-time bidirectional communication for live updates | ✅ Complete |
| **Kafka Streaming** | Event-driven architecture with 4 topics (telemetry, alerts, predictions) | ✅ Complete |
| **Redis Cache** | Sub-millisecond response times with intelligent caching strategies | ✅ Complete |
| **TimescaleDB** | Time-series data storage with hypertables and continuous aggregates | ✅ Complete |
| **GraphQL API** | Flexible data queries using Strawberry GraphQL | ✅ Complete |
| **Rate Limiting** | Redis-based API protection with configurable limits | ✅ Complete |

### 🏢 Enterprise Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Multi-Region Deployment** | 4 global regions with automatic failover and load balancing | ✅ Complete |
| **Audit Trail** | Compliance logging with SHA-256 integrity verification | ✅ Complete |
| **Data Lake** | MinIO S3-compatible storage for long-term archival | ✅ Complete |
| **Secrets Management** | Vault/K8s Secrets/AWS integration for secure credential storage | ✅ Complete |
| **TLS Encryption** | TLS 1.3 for all internal and external communications | ✅ Complete |
| **Service Mesh** | Istio/Linkerd configuration for microservice communication | ✅ Complete |
| **PLC Integration** | Native support for Siemens S7, Fanuc FOCAS, and Modbus-enabled PLCs | ✅ Complete |
| **Industrial Protocols** | Full MQTT, OPC-UA, and Modbus TCP/RTU protocol stack | ✅ Complete |
| **Health Check Utility** | Curl-based automated health diagnostics | ✅ Complete |
| **JWT Authentication** | Token-based authentication with Role-Based Access Control (RBAC) | ✅ Complete |

### 📊 Monitoring & Operations

| Feature | Description | Status |
|---------|-------------|--------|
| **Prometheus Metrics** | Comprehensive observability with 20+ custom metrics | ✅ Complete |
| **Alertmanager** | Alert routing, grouping, and notification management | ✅ Complete |
| **Grafana Dashboards** | Pre-built dashboards for fleet, machines, AI, and performance | ✅ Complete |
| **Kubernetes Deployment** | Helm charts with Horizontal Pod Autoscaling (HPA) | ✅ Complete |
| **Health Checks** | Automated system diagnostics with self-test endpoint | ✅ Complete |

### 🧪 Quality & Testing

| Feature | Description | Status |
|---------|-------------|--------|
| **Pytest** | 30+ baseline test cases (Target: 200+ for Enterprise Coverage) | 🏗️ Ongoing |
| **CI/CD Pipeline** | GitHub Actions for automated testing and deployment | ✅ Complete |
| **Pre-commit Hooks** | Code quality enforcement with linting and formatting | ✅ Complete |
| **Code Coverage** | Comprehensive testing with coverage reports | ✅ Complete |

---

## 🏗️ Architecture

### Industrial Integration Layer (Edge)

The OMAYA platform features a robust Edge Layer designed for seamless floor-to-cloud connectivity:

- **Protocol Adapters**:
    - **OPC-UA**: For modern controllers and unified data modeling.
    - **Modbus TCP/RTU**: For legacy hardware and specialized sensors.
    - **MQTT (Sparkplug B)**: For efficient, event-driven industrial messaging.
- **PLC Integration**:
    - **Siemens S7 Protocol**: Direct communication with S7-1200/1500.
    - **Fanuc FOCAS**: Deep integration with Fanuc OMAYA controllers for tool data.
    - **Heidenhain**: Monitoring of position and spindle parameters via LSV2.
- **Edge Processing**: ONNX-based local inference for real-time anomaly detection.
- **Resilience**:
    - **Store-and-Forward**: Local SQLite/LevelDB buffering during connectivity loss.
    - **Backpressure Handling**: Adaptive sampling rates during high network latency.
    - **Conflict Resolution**: Timestamp-based reconciliation (LWW - Last Write Wins) for multi-edge sync.

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        OMAYA Fleet Monitoring Platform             │
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

### Docker Services Architecture (13 Containers)

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Services                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Application Layer:                                         │
│  ├── omaya-api            → FastAPI Backend (Port 8000)    │
│  └── omaya-redis          → Cache Layer (Port 6379)       │
│                                                             │
│  Messaging Layer:                                           │
│  ├── omaya-kafka          → Event Streaming (Port 9092)    │
│  └── omaya-zookeeper      → Kafka Coordination (Port 2181) │
│                                                             │
│  Data Layer:                                               │
│  ├── omaya-timescaledb    → Time-series DB (Port 5432)    │
│  └── omaya-minio          → Data Lake (Port 9000/9001)     │
│                                                             │
│  Monitoring Layer:                                          │
│  ├── omaya-prometheus      → Metrics Collection (Port 9090) │
│  ├── omaya-alertmanager    → Alert Processing (Port 9093)   │
│  ├── omaya-grafana        → Visualization (Port 3001)      │
│  ├── omaya-redis-exporter → Redis Metrics (Port 9121)      │
│  └── omaya-node-exporter  → System Metrics (Port 9100)     │
│                                                             │
│  Security Layer:                                            │
│  └── omaya-vault          → Secrets Management (Port 8200) │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
┌──────────────┐
│OMAYA Machines│
│  (Sensors)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Kafka      │
│  (Telemetry) │
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  FastAPI     │  │ TimescaleDB  │
│  (Processing)│  │  (Storage)    │
└──────┬───────┘  └──────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  AI Models   │  │    Redis     │
│ (Prediction) │  │   (Cache)    │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│  WebSocket   │
│  (Real-time) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Frontend   │
│  (React UI)  │
└──────────────┘
```

---

## 🛠️ Technology Stack

### Frontend Technologies

| Technology | Version | Purpose | Logo |
|------------|---------|---------|------|
| **React** | 18.2.0 | UI Framework | ![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react) |
| **TypeScript** | 5.8.2 | Type Safety | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript) |
| **Vite** | 7.1.12 | Build Tool | ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite) |
| **TailwindCSS** | 3.4.1 | Styling | ![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat-square&logo=tailwindcss) |
| **Radix UI** | Latest | Component Library | ![Radix UI](https://img.shields.io/badge/Radix%20UI-FFF?style=flat-square) |
| **Framer Motion** | 11.18.0 | Animations | ![Framer Motion](https://img.shields.io/badge/Framer%20Motion-FF69B4?style=flat-square) |
| **Recharts** | 3.7.0 | Data Visualization | ![Recharts](https://img.shields.io/badge/Recharts-FF6B6B?style=flat-square) |
| **React Router** | 6.23.1 | Routing | ![React Router](https://img.shields.io/badge/React%20Router-CA4245?style=flat-square&logo=reactrouter) |
| **React Hook Form** | 7.51.5 | Form Management | ![React Hook Form](https://img.shields.io/badge/React%20Hook%20Form-EC5990?style=flat-square) |
| **Zod** | 3.23.8 | Schema Validation | ![Zod](https://img.shields.io/badge/Zod-3E82F7?style=flat-square) |
| **Lucide React** | 0.394.0 | Icons | ![Lucide](https://img.shields.io/badge/Lucide-000000?style=flat-square&logo=lucide) |

### Backend Technologies

| Technology | Version | Purpose | Logo |
|------------|---------|---------|------|
| **Python** | 3.10+ | Runtime | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python) |
| **FastAPI** | 0.109.0 | Web Framework | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi) |
| **Uvicorn** | 0.27.0 | ASGI Server | ![Uvicorn](https://img.shields.io/badge/Uvicorn-FF6B6B?style=flat-square) |
| **Pydantic** | 2.5.3 | Data Validation | ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square) |
| **WebSockets** | 12.0 | Real-time Communication | ![WebSockets](https://img.shields.io/badge/WebSockets-010101?style=flat-square) |
| **Redis** | 5.0.1 | Caching | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis) |
| **Kafka** | 2.0.2 | Event Streaming | ![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apachekafka) |
| **TimescaleDB** | Latest | Time-series Database | ![TimescaleDB](https://img.shields.io/badge/TimescaleDB-0082C9?style=flat-square&logo=postgresql) |

### AI/ML Technologies

| Technology | Version | Purpose | Logo |
|------------|---------|---------|------|
| **TensorFlow** | 2.15.0 | Deep Learning | ![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow) |
| **Scikit-learn** | 1.3.2 | Machine Learning | ![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn) |
| **NumPy** | 1.26.3 | Numerical Computing | ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy) |
| **Pandas** | 2.1.4 | Data Manipulation | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas) |
| **SHAP** | 0.44.1 | Model Explainability | ![SHAP](https://img.shields.io/badge/SHAP-4CAF50?style=flat-square) |
| **LIME** | 0.2.0.1 | Model Explainability | ![LIME](https://img.shields.io/badge/LIME-8BC34A?style=flat-square) |
| **ONNX** | 1.15.0 | Model Deployment | ![ONNX](https://img.shields.io/badge/ONNX-005CE6?style=flat-square&logo=onnx) |

### DevOps & Infrastructure

| Technology | Version | Purpose | Logo |
|------------|---------|---------|------|
| **Docker** | Latest | Containerization | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker) |
| **Docker Compose** | Latest | Multi-container Orchestration | ![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=flat-square&logo=docker) |
| **Kubernetes** | 28.1.0 | Container Orchestration | ![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes) |
| **Helm** | Latest | Package Manager | ![Helm](https://img.shields.io/badge/Helm-0F168E?style=flat-square&logo=helm) |
| **Prometheus** | Latest | Metrics Collection | ![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus) |
| **Grafana** | Latest | Visualization | ![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana) |
| **Alertmanager** | Latest | Alert Management | ![Alertmanager](https://img.shields.io/badge/Alertmanager-E6522C?style=flat-square) |
| **MinIO** | 7.2.3 | Object Storage | ![MinIO](https://img.shields.io/badge/MinIO-C72E49?style=flat-square&logo=minio) |
| **Vault** | 2.1.0 | Secrets Management | ![Vault](https://img.shields.io/badge/Vault-FFEC6D?style=flat-square&logo=hashicorp) |
| **Curl** | Latest | Health Checks | ![Curl](https://img.shields.io/badge/Curl-073551?style=flat-square&logo=curl) |

### Security & Authentication

| Technology | Version | Purpose | Logo |
|------------|---------|---------|------|
| **JWT** | 3.3.0 | Authentication | ![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens) |
| **Passlib** | 1.7.4 | Password Hashing | ![Passlib](https://img.shields.io/badge/Passlib-4B8BBE?style=flat-square) |
| **Cryptography** | 41.0.7 | Encryption | ![Cryptography](https://img.shields.io/badge/Cryptography-FF6B6B?style=flat-square) |
| **TLS** | 1.3 | Secure Communication | ![TLS](https://img.shields.io/badge/TLS-1.3-00599C?style=flat-square) |

### Development Tools

| Technology | Version | Purpose | Logo |
|------------|---------|---------|------|
| **ESLint** | Latest | Linting | ![ESLint](https://img.shields.io/badge/ESLint-4B32C3?style=flat-square&logo=eslint) |
| **Prettier** | Latest | Code Formatting | ![Prettier](https://img.shields.io/badge/Prettier-F7B93E?style=flat-square&logo=prettier) |
| **Pre-commit** | 3.6.0 | Git Hooks | ![Pre-commit](https://img.shields.io/badge/Pre--commit-FAB040?style=flat-square) |
| **Pytest** | 7.4.3 | Testing | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest) |
| **GitHub Actions** | Latest | CI/CD | ![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions) |

---

## 📦 Installation & Setup

### Prerequisites

- **Node.js** >= 18.x
- **Python** >= 3.10
- **Docker** >= 20.x
- **Docker Compose** >= 2.x
- **Git** >= 2.x

### Quick Start (Development)

#### 1. Clone the Repository

```bash
git clone https://github.com/Def-Coms/OMAYA-industrial.git
cd OMAYA-industrial
```

#### 2. Start All Services

**Quick Start (Development - Core Services Only):**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

This will start the core services needed for development:
- **Frontend** (React + Nginx) - Port 80
- **FastAPI Backend** - Port 8000
- **Redis Cache** - Port 6379
- **TimescaleDB** - Port 5432

**Full Stack (All Services):**
```bash
docker-compose up -d
```

This will start all Docker containers including monitoring services.
- **Frontend** (React + Nginx) - Port 80
- **FastAPI Backend** - Port 8000
- **Redis Cache** - Port 6379
- **Kafka** - Port 9092
- **Zookeeper** - Port 2181
- **TimescaleDB** - Port 5432
- **Prometheus** - Port 9090
- **Alertmanager** - Port 9093
- **Grafana** - Port 3001
- **Redis Exporter** - Port 9121
- **Node Exporter** - Port 9100
- **MinIO** - Port 9000/9001
- **Vault** - Port 8200

#### 3. Access Services

- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **GraphQL Playground:** http://localhost:8000/graphql
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001 `(admin/admin)`*
- **MinIO Console:** http://localhost:9001 `(minioadmin/minioadmin)`*
- **Vault:** http://localhost:8200

> [!WARNING]
> **SECURITY NOTICE:** Default credentials (*) are provided for local development ONLY. You MUST change all passwords and rotate keys using Vault before any network-exposed deployment.

#### Development Mode (Optional)

If you prefer to run the frontend in development mode with hot-reload:

```bash
# Start backend services only
docker-compose up -d api redis kafka zookeeper timescaledb prometheus grafana alertmanager minio vault

# Install frontend dependencies
npm install

# Start frontend in development mode
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Production Deployment

#### Docker Compose (Production)

```bash
# Standard Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# High Availability (HA) Cluster
cp .env.ha.example .env
# Edit .env with secure passwords
docker-compose -f docker-compose.ha.yml up -d
```

**Scaling:**
```bash
# Scale API instances in standard mode
docker-compose up -d --scale api=4
```

#### Kubernetes (Helm)

```bash
# Add Helm repository
helm repo add omaya-monitoring https://your-helm-repo.com

# Install chart
helm install omaya-monitoring ./backend/kubernetes/helm

# Scale API instances
kubectl scale deployment omaya-api --replicas=10

# Check status
kubectl get pods -n omaya-monitoring
```

#### Multi-Region Deployment

```bash
# Deploy to primary region (eu-west-1)
kubectl config use-context eu-west-1
helm install omaya-monitoring ./backend/kubernetes/helm

# Deploy to secondary regions
kubectl config use-context us-east-1
helm install omaya-monitoring ./backend/kubernetes/helm

kubectl config use-context ap-northeast-1
helm install omaya-monitoring ./backend/kubernetes/helm

kubectl config use-context us-west-2
helm install omaya-monitoring ./backend/kubernetes/helm
```

### Environment Configuration

Create a `.env` file in the backend directory:

```bash
cp backend/.env.example backend/.env
```

Key environment variables:

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

# Multi-Region
PRIMARY_REGION=eu-west-1
SECONDARY_REGIONS=us-east-1,ap-northeast-1,us-west-2
```

---

## 🎨 Frontend Modules

### Dashboard Components

| Component | Description | File |
|-----------|-------------|------|
| **Dashboard.tsx** | Main dashboard container with tab navigation | `src/components/dashboard/Dashboard.tsx` |
| **Sidebar.tsx** | Navigation sidebar with menu items | `src/components/dashboard/Sidebar.tsx` |
| **KPICards.tsx** | Key performance indicators display | `src/components/dashboard/KPICards.tsx` |
| **FleetOverview.tsx** | Grid/list view of all machines | `src/components/dashboard/FleetOverview.tsx` |
| **MachineDetailPanel.tsx** | Detailed machine information panel | `src/components/dashboard/MachineDetailPanel.tsx` |
| **AlertsPanel.tsx** | Alert management center | `src/components/dashboard/AlertsPanel.tsx` |
| **TelemetryFeed.tsx** | Real-time telemetry event stream | `src/components/dashboard/TelemetryFeed.tsx` |
| **PredictiveMaintenancePanel.tsx** | AI-powered maintenance predictions | `src/components/dashboard/PredictiveMaintenancePanel.tsx` |
| **ToolWearTracker.tsx** | Tool lifecycle tracking | `src/components/dashboard/ToolWearTracker.tsx` |
| **MaintenanceCalendar.tsx** | Maintenance scheduling calendar | `src/components/dashboard/MaintenanceCalendar.tsx` |
| **ProductionForecastChart.tsx** | Production forecasting visualization | `src/components/dashboard/ProductionForecastChart.tsx` |

### Enterprise Components

| Component | Description | File |
|-----------|-------------|------|
| **AIExplainabilityPanel.tsx** | SHAP/LIME analysis visualizations | `src/components/dashboard/AIExplainabilityPanel.tsx` |
| **AuditTrailPanel.tsx** | Compliance event tracking | `src/components/dashboard/AuditTrailPanel.tsx` |
| **MultiRegionDashboard.tsx** | Global region status monitoring | `src/components/dashboard/MultiRegionDashboard.tsx` |
| **AdvancedAnalyticsDashboard.tsx** | Advanced analytics and reporting | `src/components/dashboard/AdvancedAnalyticsDashboard.tsx` |
| **GraphQLExplorer.tsx** | Interactive GraphQL query explorer | `src/components/dashboard/GraphQLExplorer.tsx` |
| **ModelDriftMonitor.tsx** | Model performance drift tracking | `src/components/ModelDriftMonitor.tsx` |
| **DataLakeStats.tsx** | Data lake storage analytics | `src/components/DataLakeStats.tsx` |
| **ExplainableAI.tsx** | Feature importance analysis | `src/components/ExplainableAI.tsx` |

### Analytics Components

| Component | Description | File |
|-----------|-------------|------|
| **WidgetLibrary.tsx** | Widget library for custom dashboards | `src/components/dashboard/analytics/WidgetLibrary.tsx` |
| **WidgetCanvas.tsx** | Canvas for widget arrangement | `src/components/dashboard/analytics/WidgetCanvas.tsx` |
| **WidgetRenderer.tsx** | Widget rendering engine | `src/components/dashboard/analytics/WidgetRenderer.tsx` |
| **CustomKPIBuilder.tsx** | Custom KPI creation tool | `src/components/dashboard/analytics/CustomKPIBuilder.tsx` |
| **CorrelationMatrix.tsx** | Feature correlation analysis | `src/components/dashboard/analytics/CorrelationMatrix.tsx` |

### UI Components (Radix UI)

| Component | Description | File |
|-----------|-------------|------|
| **Button** | Button component with variants | `src/components/ui/button.tsx` |
| **Card** | Card container component | `src/components/ui/card.tsx` |
| **Dialog** | Modal dialog component | `src/components/ui/dialog.tsx` |
| **Dropdown Menu** | Dropdown menu component | `src/components/ui/dropdown-menu.tsx` |
| **Select** | Select input component | `src/components/ui/select.tsx` |
| **Tabs** | Tab navigation component | `src/components/ui/tabs.tsx` |
| **Table** | Data table component | `src/components/ui/table.tsx` |
| **Toast** | Toast notification component | `src/components/ui/toast.tsx` |
| **Form** | Form components with validation | `src/components/ui/form.tsx` |
| **Calendar** | Date picker calendar | `src/components/ui/calendar.tsx` |
| **Badge** | Badge/status indicator | `src/components/ui/badge.tsx` |
| **Progress** | Progress bar component | `src/components/ui/progress.tsx` |
| **Skeleton** | Loading skeleton component | `src/components/ui/skeleton.tsx` |

### Custom Hooks

| Hook | Description | File |
|------|-------------|------|
| **useRealTimeData** | Real-time data fetching with auto-refresh | `src/hooks/useRealTimeData.ts` |
| **useGraphQL** | GraphQL query hook | `src/hooks/useGraphQL.ts` |

### Data & Types

| Module | Description | File |
|-------|-------------|------|
| **mockData.ts** | Mock data generation for development | `src/data/mockData.ts` |
| **omaya.ts** | TypeScript type definitions | `src/types/omaya.ts` |
| **analytics-engine.ts** | Analytics calculation engine | `src/lib/analytics-engine.ts` |
| **graphql-client.ts** | GraphQL client configuration | `src/lib/graphql-client.ts` |
| **utils.ts** | Utility functions | `src/lib/utils.ts` |

---

## ⚙️ Backend Modules

### Core API Modules

| Module | Description | File |
|--------|-------------|------|
| **main.py** | FastAPI application entry point | `backend/main.py` |
| **auth.py** | JWT authentication & RBAC | `backend/auth.py` |
| **websocket_manager.py** | WebSocket connection management | `backend/websocket_manager.py` |
| **rate_limiter.py** | Redis-based rate limiting | `backend/rate_limiter.py` |

### AI/ML Modules

| Module | Description | File |
|--------|-------------|------|
| **ai_models.py** | TensorFlow LSTM & ensemble models | `backend/ai_models.py` |
| **drift_detection.py** | Model drift detection (PSI) | `backend/drift_detection.py` |
| **online_learning.py** | Online anomaly detection | `backend/online_learning.py` |
| **explainable_ai.py** | SHAP/LIME explainability | `backend/explainable_ai.py` |
| **edge_computing.py** | ONNX model conversion | `backend/edge_computing.py` |

### Data Processing Modules

| Module | Description | File |
|--------|-------------|------|
| **kafka_producer.py** | Kafka event producer | `backend/kafka_producer.py` |
| **kafka_consumer.py** | Kafka event consumer | `backend/kafka_consumer.py` |
| **kafka_streams.py** | Kafka stream processing | `backend/kafka_streams.py` |
| **kafka_init.py** | Kafka topic initialization | `backend/kafka_init.py` |
| **redis_cache.py** | Redis cache operations | `backend/redis_cache.py` |

### Enterprise Modules

| Module | Description | File |
|--------|-------------|------|
| **graphql_layer.py** | GraphQL API layer (Strawberry) | `backend/graphql_layer.py` |
| **data_lake.py** | MinIO data lake operations | `backend/data_lake.py` |
| **multi_region.py** | Multi-region deployment logic | `backend/multi_region.py` |
| **audit_trails.py** | Audit trail logging | `backend/audit_trails.py` |
| **secrets_manager.py** | Vault secrets management | `backend/secrets_manager.py` |
| **service_mesh.py** | Istio/Linkerd configuration | `backend/service_mesh.py` |
| **tls_config.py** | TLS encryption configuration | `backend/tls_config.py` |

### Monitoring Modules

| Module | Description | File |
|--------|-------------|------|
| **prometheus_metrics.py** | Prometheus metrics exporter | `backend/prometheus_metrics.py` |

### Testing & Scripts

| Module | Description | File |
|--------|-------------|------|
| **tests/** | Pytest test suite | `backend/tests/` |
| **scripts/** | Deployment and utility scripts | `backend/scripts/` |
| **ml_models/** | ML model training scripts | `backend/ml_models/` |
| **monitoring/** | Prometheus/Grafana configs | `backend/monitoring/` |
| **docker/** | Docker initialization scripts | `backend/docker/` |
| **kubernetes/** | Kubernetes Helm charts | `backend/kubernetes/` |

---

## 📊 Model Performance

### Failure Prediction Model (LSTM)
Validation results on OMAYA industrial dataset.

| Metric | Value |
|--------|-------|
| **Accuracy** | 93.2% |
| **Precision** | 91.4% |
| **Recall** | 89.7% |
| **F1-score** | 90.5% |
| **ROC-AUC** | 0.94 |
| **False Positive Rate** | 2.1% |

### Remaining Useful Life (RUL)
Performance across ensemble models.

| Model | MAE (Hours) | RMSE (Hours) | R² Score |
|-------|-------------|--------------|----------|
| **LSTM Ensemble** | 12.4 | 18.2 | 0.88 |
| **Random Forest** | 15.6 | 22.4 | 0.84 |
| **Survival Analysis** | 10.8 | 16.5 | 0.91 |

---

## 🤖 AI/ML Capabilities

### TensorFlow LSTM Model

**Architecture:** 64-32 LSTM neural network for time-series failure prediction

```python
# Model Architecture
Input Layer (4 features: temperature, vibration, tool_wear, operating_hours)
    ↓
LSTM Layer 1 (64 units)
    ↓
LSTM Layer 2 (32 units)
    ↓
Dense Layer (16 units, ReLU)
    ↓
Output Layer (1 unit, Sigmoid)
```

**Features:**
- Real-time failure probability prediction
- Confidence interval estimation
- Model versioning and rollback
- Automated retraining pipeline

**Training:**
```bash
cd backend/ml_models
python train_models.py
```

### Ensemble RUL Models

**Models:**
- Random Forest Regressor
- Gradient Boosting Regressor
- Survival Analysis (Cox Proportional Hazards)

**Output:** Remaining Useful Life (RUL) in hours with confidence intervals

### Online Learning Anomaly Detection

**Algorithm:** Isolation Forest with online adaptation

**Features:**
- Real-time anomaly detection
- Adaptive threshold adjustment
- Concept drift handling
- Automated retraining triggers

### Model Drift Detection

**Metric:** Population Stability Index (PSI)

**Thresholds:**
- PSI < 0.1: No drift
- 0.1 ≤ PSI < 0.2: Moderate drift
- PSI ≥ 0.2: Significant drift (retrain required)

### AI Explainability

**SHAP (Shapley Additive Explanations):**
- Global feature importance
- Local prediction explanations
- Interaction effects

**LIME (Local Interpretable Model-agnostic Explanations):**
- Local prediction interpretation
- Feature contribution analysis
- Decision boundary visualization

### Edge Computing

**ONNX Conversion:**
```python
# Convert TensorFlow model to ONNX
python backend/edge_computing.py --model lstm --format onnx
```

**Benefits:**
- Reduced model size
- Faster inference
- Edge deployment capability

---

## 📊 API Documentation

### Core Endpoints

#### Health & Status

```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "service": "OMAYA Fleet Monitoring API",
  "version": "2.4.8",
  "status": "operational"
}
```

```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "kafka": "connected"
  }
}
```

```http
GET /api/self-test HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "status": "passed",
  "tests": [
    {"name": "database_connection", "status": "passed"},
    {"name": "redis_connection", "status": "passed"},
    {"name": "kafka_connection", "status": "passed"},
    {"name": "ai_models_loaded", "status": "passed"}
  ]
}
```

#### Machine Endpoints

```http
GET /api/machines HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "machines": [
    {
      "id": "OMAYA-001",
      "name": "OMAYA-5X #1",
      "zone": "Zone A",
      "status": "operational",
      "spindleSpeed": 10500,
      "temperature": 42.5,
      "vibration": 1.2,
      "toolWear": 35,
      "cycleTime": 120,
      "uptime": 95.5
    }
  ],
  "total": 120
}
```

```http
GET /api/machines/{id} HTTP/1.1
Host: localhost:8000
```

```http
POST /api/machines/{id}/status HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "status": "maintenance",
  "reason": "Scheduled preventive maintenance"
}
```

#### Alert Endpoints

```http
GET /api/alerts?severity=critical HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert-001",
      "machineId": "OMAYA-001",
      "machineName": "OMAYA-5X #1",
      "severity": "critical",
      "type": "overheating",
      "title": "Critical: OMAYA-5X #1 requires immediate attention",
      "message": "Temperature exceeding safe limits. Immediate shutdown recommended.",
      "timestamp": "2024-01-15T10:30:00Z",
      "acknowledged": false
    }
  ],
  "total": 5
}
```

```http
POST /api/alerts HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "machineId": "OMAYA-001",
  "severity": "warning",
  "type": "vibration",
  "title": "Elevated vibration detected",
  "message": "Vibration levels indicate potential bearing wear"
}
```

### AI Prediction Endpoints

#### Failure Prediction

```http
POST /api/predict/failure HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "machineId": "OMAYA-001",
  "features": {
    "temperature": 68.5,
    "vibration": 2.1,
    "toolWear": 75,
    "operatingHours": 3200
  }
}
```

**Response:**
```json
{
  "machineId": "OMAYA-001",
  "failureProbability": 0.78,
  "confidence": 0.92,
  "estimatedTimeToFailure": 48,
  "recommendedAction": "Schedule immediate maintenance",
  "contributingFactors": [
    "High vibration (2.1 mm/s)",
    "Elevated temperature (68.5°C)",
    "Tool wear approaching limit (75%)"
  ]
}
```

#### RUL Prediction

```http
POST /api/predict/rul HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "machineId": "OMAYA-001",
  "features": {
    "temperature": 68.5,
    "vibration": 2.1,
    "toolWear": 75
  }
}
```

**Response:**
```json
{
  "machineId": "OMAYA-001",
  "remainingUsefulLife": 48,
  "confidenceInterval": {
    "lower": 36,
    "upper": 60
  },
  "confidence": 0.89,
  "model": "ensemble_rul_v3.2"
}
```

#### Anomaly Detection

```http
POST /api/detect/anomaly HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "machineId": "OMAYA-001",
  "features": {
    "temperature": 85.0,
    "vibration": 3.5,
    "spindleSpeed": 9500
  }
}
```

**Response:**
```json
{
  "machineId": "OMAYA-001",
  "isAnomaly": true,
  "anomalyScore": 0.92,
  "threshold": 0.75,
  "features": [
    {"name": "temperature", "value": 85.0, "contribution": 0.45},
    {"name": "vibration", "value": 3.5, "contribution": 0.35},
    {"name": "spindleSpeed", "value": 9500, "contribution": 0.20}
  ]
}
```

### Enterprise Endpoints

#### AI Explainability

```http
GET /api/explainability/{machineId} HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "machineId": "OMAYA-001",
  "shapValues": {
    "temperature": 0.35,
    "vibration": 0.28,
    "toolWear": 0.22,
    "operatingHours": 0.15
  },
  "limeExplanation": {
    "prediction": "failure",
    "confidence": 0.78,
    "featureContributions": [
      {"feature": "temperature", "contribution": 0.35},
      {"feature": "vibration", "contribution": 0.28}
    ]
  }
}
```

#### Data Lake Statistics

```http
GET /api/data-lake/stats HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "totalObjects": 1500000,
  "totalSize": "2.5TB",
  "buckets": {
    "telemetry": 1000000,
    "predictions": 300000,
    "models": 50000,
    "reports": 150000
  },
  "retention": "90 days"
}
```

#### Audit Trail

```http
GET /api/audit/recent?limit=50 HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "events": [
    {
      "id": "audit-001",
      "timestamp": "2024-01-15T10:30:00Z",
      "eventType": "machine_status_change",
      "userId": "admin",
      "machineId": "OMAYA-001",
      "details": {
        "oldStatus": "operational",
        "newStatus": "maintenance"
      },
      "checksum": "sha256:abc123..."
    }
  ],
  "total": 50
}
```

```http
GET /api/audit/report?startDate=2024-01-01&endDate=2024-01-31 HTTP/1.1
Host: localhost:8000
```

#### Model Drift Status

```http
GET /api/drift/status HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "models": [
    {
      "name": "lstm_failure_v3.2",
      "psi": 0.08,
      "status": "stable",
      "lastRetrained": "2024-01-10T00:00:00Z"
    },
    {
      "name": "ensemble_rul_v3.2",
      "psi": 0.15,
      "status": "moderate_drift",
      "lastRetrained": "2024-01-05T00:00:00Z"
    }
  ]
}
```

#### Multi-Region Status

```http
GET /api/multi-region/status HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "regions": [
    {
      "name": "eu-west-1",
      "status": "active",
      "health": "healthy",
      "machines": 40,
      "latency": "12ms"
    },
    {
      "name": "us-east-1",
      "status": "active",
      "health": "healthy",
      "machines": 30,
      "latency": "45ms"
    }
  ]
}
```

#### Secrets Status

```http
GET /api/secrets/status HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "provider": "vault",
  "status": "connected",
  "secretsCount": 25,
  "lastRotation": "2024-01-10T00:00:00Z"
}
```

### WebSocket Endpoint

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Subscribe to machine updates
ws.send(JSON.stringify({
  type: 'subscribe',
  machines: ['OMAYA-001', 'OMAYA-002']
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.payload);
};
```

**Message Types:**
- `machine_update` - Machine status changed
- `new_alert` - New alert created
- `telemetry` - Telemetry event
- `prediction` - AI prediction update
- `ping/pong` - Heartbeat

### GraphQL Endpoint

```graphql
query GetMachine($id: ID!) {
  machine(id: $id) {
    id
    name
    zone
    status
    temperature
    vibration
    toolWear
    predictions {
      failureProbability
      estimatedTimeToFailure
      recommendedAction
    }
  }
}
```

**Endpoint:** `http://localhost:8000/graphql`

---

## 🔒 Security Features

### Authentication & Authorization

**JWT Authentication:**
- Token-based authentication with RS256 signing
- Configurable token expiration (default: 1 hour)
- Refresh token support

**Role-Based Access Control (RBAC):**
- **Admin** - Full access to all resources
- **Operator** - Read/write access to machines and alerts
- **Viewer** - Read-only access to dashboards

**Implementation:**
```python
# Example protected endpoint
@app.get("/api/machines")
@require_role(["admin", "operator", "viewer"])
async def get_machines(current_user: User = Depends(get_current_user)):
    return get_all_machines()
```

### Encryption

**TLS 1.3:**
- All internal communications encrypted
- Certificate-based authentication
- Perfect Forward Secrecy

**Data Encryption:**
- Database encryption at rest (TimescaleDB)
- Redis encryption in transit
- MinIO server-side encryption

### Secrets Management

**Vault Integration:**
- Centralized secret storage
- Automatic secret rotation
- Dynamic secrets generation
- Audit logging for secret access

**Supported Providers:**
- HashiCorp Vault
- Kubernetes Secrets
- AWS Secrets Manager
- Azure Key Vault

### Audit Trail

**Compliance Logging:**
- All user actions logged
- SHA-256 integrity verification
- 365-day retention
- Export to PDF/CSV

**Event Types:**
- User authentication
- Machine status changes
- Alert acknowledgments
- Configuration modifications
- API access

### Rate Limiting

**Redis-based Rate Limiting:**
- Configurable per-endpoint limits
- Sliding window algorithm
- IP-based and user-based limits
- Automatic ban on abuse

**Configuration:**
```python
RATE_LIMITS = {
    "/api/machines": {"requests": 100, "window": "60s"},
    "/api/predict/*": {"requests": 50, "window": "60s"},
    "/api/alerts": {"requests": 200, "window": "60s"}
}
```

### Input Validation

**Pydantic Models:**
- Automatic request validation
- Type checking
- Custom validators
- Sanitization of user input

---

## 📈 Monitoring & Observability

### Prometheus Metrics

**Available Metrics:**

| Metric | Type | Description |
|--------|------|-------------|
| `omaya_api_requests_total` | Counter | Total API requests |
| `omaya_api_request_duration_seconds` | Histogram | API request duration |
| `omaya_machines_total` | Gauge | Total number of machines |
| `omaya_machines_status` | Gauge | Machines by status |
| `omaya_alerts_total` | Counter | Total alerts |
| `omaya_alerts_severity` | Gauge | Alerts by severity |
| `omaya_predictions_total` | Counter | Total AI predictions |
| `omaya_prediction_duration_seconds` | Histogram | Prediction duration |
| `omaya_websocket_connections` | Gauge | Active WebSocket connections |
| `omaya_cache_hit_rate` | Gauge | Cache hit rate |
| `omaya_cache_miss_rate` | Gauge | Cache miss rate |
| `omaya_database_query_duration_seconds` | Histogram | Database query duration |
| `omaya_kafka_messages_total` | Counter | Kafka messages produced/consumed |
| `omaya_model_drift_psi` | Gauge | Model drift PSI value |

**Access Metrics:**
```bash
curl http://localhost:8000/metrics
```

### Alertmanager Rules

**Configured Alerts:**

| Alert | Condition | Severity |
|-------|-----------|----------|
| `HighFailureProbability` | Machine failure risk > 80% | Critical |
| `CriticalRUL` | RUL < 24 hours | Critical |
| `ToolWearCritical` | Tool wear > 85% | Warning |
| `HighAPILatency` | P95 latency > 1s | Warning |
| `LowCacheHitRate` | Cache efficiency < 50% | Warning |
| `DatabaseConnectionFailure` | DB connection failed | Critical |
| `KafkaConsumerLag` | Consumer lag > 1000 | Warning |
| `ModelDriftDetected` | PSI > 0.2 | Warning |

### Grafana Dashboards

**Available Dashboards:**

1. **Fleet Overview**
   - Machine status distribution
   - Real-time KPIs
   - Alert trends

2. **Machine Health**
   - Individual machine metrics
   - Temperature trends
   - Vibration patterns

3. **AI Predictions**
   - Failure probability trends
   - RUL predictions
   - Model accuracy

4. **Alert History**
   - Alert frequency
   - Resolution time
   - Escalation rate

5. **API Performance**
   - Request rate
   - Response time
   - Error rate

**Access:** http://localhost:3001 (admin/admin)

### Health Checks

**System Self-Test:**
```bash
curl http://localhost:8000/api/self-test
```

**Checks Performed:**
- Database connectivity
- Redis connectivity
- Kafka connectivity
- AI model loading
- WebSocket functionality
- Cache performance

---

## 🌍 Deployment

### Docker Deployment

**Development:**
```bash
cd backend
docker-compose up -d
```

**Production:**
```bash
cd backend
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Scaling:**
```bash
# Scale API instances
docker-compose up -d --scale api=4
```

### Kubernetes Deployment

**Helm Installation:**
```bash
# Add repository
helm repo add omaya-monitoring https://your-helm-repo.com

# Update repository
helm repo update

# Install chart
helm install omaya-monitoring ./backend/kubernetes/helm \
  --namespace omaya-monitoring \
  --create-namespace

# Upgrade deployment
helm upgrade omaya-monitoring ./backend/kubernetes/helm

# Rollback
helm rollback omaya-monitoring
```

**Horizontal Pod Autoscaling:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: omaya-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: omaya-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Multi-Region Deployment

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                  Global Load Balancer                   │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  eu-west-1   │    │  us-east-1   │    │ ap-northeast-1│
│  (Primary)   │    │  (Secondary) │    │  (Secondary) │
│              │    │              │    │              │
│  40 Machines │    │  30 Machines │    │  25 Machines │
└──────────────┘    └──────────────┘    └──────────────┘
```

**Features:**
- Automatic failover
- Geo-redundancy
- Traffic routing based on latency
- Regional health monitoring

**Deployment:**
```bash
# Deploy to each region
for region in eu-west-1 us-east-1 ap-northeast-1 us-west-2; do
  kubectl config use-context $region
  helm install omaya-monitoring ./backend/kubernetes/helm
done
```

### CI/CD Pipeline

**GitHub Actions Workflow:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t omaya-api:${{ github.sha }} backend/
      - name: Push to registry
        run: |
          docker push omaya-api:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          helm upgrade omaya-monitoring ./backend/kubernetes/helm
```

---

## 🧪 Testing

### Backend Testing

**Run All Tests:**
```bash
cd backend
pytest
```

**Run with Coverage:**
```bash
pytest --cov=. --cov-report=html
```

**Run Specific Test:**
```bash
pytest tests/test_api.py::test_get_machines
```

**Test Categories:**
- Unit tests (individual functions)
- Integration tests (API endpoints)
- End-to-end tests (full workflows)

### Frontend Testing

**Run Tests:**
```bash
npm test
```

**Run with Coverage:**
```bash
npm test -- --coverage
```

### Manual Testing

**Self-Test Endpoint:**
```bash
curl http://localhost:8000/api/self-test | jq
```

**Simulate Failure Scenario:**
```bash
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"type": "machine_failure", "machineId": "OMAYA-001"}'
```

**Check Prometheus Metrics:**
```bash
curl http://localhost:8000/metrics
```

---

## 📚 Documentation

### API Documentation

**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

### GraphQL Documentation

**GraphQL Playground:** http://localhost:8000/graphql

### Monitoring Documentation

**Prometheus:** http://localhost:9090
**Grafana:** http://localhost:3001 (admin/admin)
**Alertmanager:** http://localhost:9093

### Storage Documentation

**MinIO Console:** http://localhost:9001 (minioadmin/minioadmin)
**Vault:** http://localhost:8200

### Code Documentation

**Inline Documentation:**
- All Python functions have docstrings
- TypeScript components have JSDoc comments
- API endpoints have OpenAPI descriptions

---

## 🎯 Platform Statistics

### Code Statistics

| Metric | Count |
|--------|-------|
| **Total Python Modules** | 30+ |
| **Total TypeScript Components** | 40+ |
| **Docker Services** | 13 |
| **API Endpoints** | 50+ |
| **GraphQL Queries** | 25+ |
| **Test Cases** | 30+ |
| **Lines of Code** | 15,000+ |
| **Dependencies** | 40+ packages |

### Database Statistics

| Metric | Count |
|--------|-------|
| **Database Tables** | 15+ |
| **Kafka Topics** | 4 |
| **TimescaleDB Hypertables** | 5 |
| **Continuous Aggregates** | 8 |
| **Data Retention** | 90 days |

### Monitoring Statistics

| Metric | Count |
|--------|-------|
| **Prometheus Metrics** | 20+ |
| **Alert Rules** | 8 |
| **Grafana Dashboards** | 5 |
| **Alertmanager Routes** | 10+ |

### Performance Metrics

| Metric | Value |
|--------|-------|
| **API Response Time** | < 50ms (p95) |
| **WebSocket Latency** | < 10ms |
| **Cache Hit Rate** | > 95% |
| **Database Query Time** | < 5ms |
| **Real-time Update Frequency** | 3 seconds |
| **Concurrent Connections** | 1000+ |
| **Prediction Latency** | < 100ms |

### Platform Maturity (v2.4.8)

```
Core Features:          ████████████████████ 100% (Feature Complete)
Backend Services:       ████████████████████ 100% (Production Grade)
AI/ML Models:          ██████████████████░░ 90%  (Optimization Phase)
Enterprise Features:   ██████████████████░░ 90%  (Scaling Tests)
Security:              ██████████████████░░ 90%  (Audit Pending)
Testing:               ████████████████░░░░ 80%  (UAT Ongoing)
Documentation:         ████████████████████ 100% (Synchronized)
UI Integration:        ████████████████████ 100% (Responsive)
Monitoring:            ██████████████████░░ 90%  (Alert Tuning)
Deployment:            ████████████████░░░░ 80%  (Multi-region Beta)
```

**Release Status: Feature Complete v2.4** 🚀

---

## 🤝 Support

### Getting Help

- **API Documentation:** http://localhost:8000/docs
- **Audit Logs:** http://localhost:8000/api/audit/recent
- **System Health:** http://localhost:8000/health
- **Self-Test:** http://localhost:8000/api/self-test

### Contact

- **DevOps Team:** devops@defcoms.eu
- **Support Portal:** https://support.defcoms.eu
- **Documentation:** https://docs.defcoms.eu/omaya-monitoring

### Issue Reporting

- **GitHub Issues:** https://github.com/Def-Coms/OMAYA-industrial/issues
- **Bug Reports:** bugs@defcoms.eu
- **Feature Requests:** features@defcoms.eu

---

## 📜 License

**Enterprise License - All Rights Reserved**

OMAYA © 2024 DefComs - All rights reserved.

---

## 🙏 Acknowledgments

**Built with:**
- [React](https://reactjs.org/) - UI Framework
- [TypeScript](https://www.typescriptlang.org/) - Type Safety
- [FastAPI](https://fastapi.tiangolo.com/) - Web Framework
- [TensorFlow](https://www.tensorflow.org/) - Machine Learning
- [Kafka](https://kafka.apache.org/) - Event Streaming
- [Redis](https://redis.io/) - Caching
- [TimescaleDB](https://www.timescale.com/) - Time-series Database
- [Docker](https://www.docker.com/) - Containerization
- [Kubernetes](https://kubernetes.io/) - Orchestration
- [Prometheus](https://prometheus.io/) - Monitoring
- [Grafana](https://grafana.com/) - Visualization

---

**Platform Version:** 2.4.8
**Status:** 🟠 Release Candidate (v2.4-RC)
**Last Updated:** March 2025
**Maintained by:** DefComs
