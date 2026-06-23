# Installation Guide

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Docker Installation](#docker-installation)
- [Manual Installation](#manual-installation)
- [Post-Installation Configuration](#post-installation-configuration)
- [Verification](#verification)
- [Uninstallation](#uninstallation)

---

## System Requirements

### Minimum Requirements

- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **Network**: 1 Gbps
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+), Windows 10/11 with WSL2, macOS 11+

### Recommended Requirements

- **CPU**: 8 cores
- **RAM**: 16 GB
- **Storage**: 100 GB SSD
- **Network**: 1 Gbps
- **OS**: Linux (Ubuntu 22.04 LTS recommended)

### Production Requirements

- **CPU**: 16+ cores
- **RAM**: 32+ GB
- **Storage**: 500+ GB SSD
- **Network**: 10 Gbps
- **OS**: Linux (Ubuntu 22.04 LTS or RHEL 9)

---

## Prerequisites

### Required Software

#### Docker
```bash
# Install Docker on Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
```

#### Docker Compose
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Node.js (for development)
```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Python (for development)
```bash
# Install Python 3.11
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip
```

#### Curl
```bash
# Required for Docker health checks
sudo apt-get update
sudo apt-get install -y curl
```

### Optional Software

- **Git**: For version control
- **VS Code**: Recommended IDE
- **Postman**: For API testing
- **DBeaver**: For database management

---

## Installation Methods

### Method 1: Docker Compose (Recommended)

This is the simplest and recommended method for most users.

#### Quick Start (Core Services)

```bash
# Clone repository
git clone https://github.com/Def-Coms/OMAYA-industrial.git
cd OMAYA-industrial

# Start core services
docker-compose -f docker-compose.dev.yml up -d

# Check status
docker-compose -f docker-compose.dev.yml ps
```

#### Full Stack Installation

```bash
# Start all services including monitoring
docker-compose up -d

# Check status
docker-compose ps
```

### Method 2: Manual Installation

For advanced users who need more control over the installation.

#### Backend Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python -c "from backend.main import Base, engine; Base.metadata.create_all(bind=engine)"

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend Installation

```bash
# Navigate to root directory
cd OMAYA-industrial

# Install dependencies
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

---

## Docker Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/Def-Coms/OMAYA-industrial.git
cd OMAYA-industrial
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit configuration
nano backend/.env
```

Required environment variables:

```env
# Database Configuration
TIMESCALE_HOST=timescaledb
TIMESCALE_PORT=5432
TIMESCALE_USER=omaya_user
TIMESCALE_PASSWORD=omaya_password
TIMESCALE_DB=omaya_monitoring

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Security
# Generate a secure JWT secret using: openssl rand -base64 32
# Or retrieve from Vault: vault kv get omaya/jwt
JWT_SECRET=
```

### Step 3: Start Services

#### Development Mode (Core Services)

```bash
docker-compose -f docker-compose.dev.yml up -d
```

This starts:
- Frontend (React + Nginx)
- Backend (FastAPI)
- Redis Cache
- TimescaleDB

#### Production Mode (All Services)

```bash
docker-compose up -d
```

This starts all services including:
- Kafka & Zookeeper
- Prometheus & Grafana
- Alertmanager
- MinIO
- Vault
- Redis Exporter
- Node Exporter

### Step 4: Verify Installation

```bash
# Check all containers are running
docker-compose ps

# Check logs
docker-compose logs -f

# Test frontend
curl http://localhost

# Test backend
curl http://localhost:8000/health
```

---

## Manual Installation

### Database Setup (TimescaleDB)

#### Install TimescaleDB

```bash
# Add TimescaleDB repository
echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
wget -qO - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt-get update

# Install TimescaleDB
sudo apt-get install timescaledb-2-postgresql-15

# Start TimescaleDB
sudo service timescaledb start

# Create database and user
sudo -u postgres psql
```

```sql
CREATE USER omaya_user WITH PASSWORD 'omaya_password';
CREATE DATABASE omaya_monitoring OWNER omaya_user;
\c omaya_monitoring
CREATE EXTENSION IF NOT EXISTS timescaledb;
GRANT ALL PRIVILEGES ON DATABASE omaya_monitoring TO omaya_user;
\q
```

### Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Start Redis
sudo service redis-server start
```

### Kafka Setup

```bash
# Install Java (required for Kafka)
sudo apt-get install openjdk-11-jdk

# Download Kafka
wget https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz
tar -xzf kafka_2.13-2.8.0.tgz
cd kafka_2.13-2.8.0

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka
bin/kafka-server-start.sh config/server.properties
```

---

## Post-Installation Configuration

### Database Initialization

```bash
# Run initialization script
docker-compose exec timescaledb psql -U omaya_user -d omaya_monitoring -f /docker-entrypoint-initdb.d/init.sql
```

### Create Admin User

```bash
# Access backend container
docker-compose exec api python

# In Python shell
from backend.auth import create_admin_user
create_admin_user("admin@omaya.com", "secure_password")
```

### Configure Monitoring

```bash
# Access Grafana
# URL: http://localhost:3001
# Default credentials: admin/admin (CHANGE IMMEDIATELY)

# Add Prometheus data source
# URL: http://prometheus:9090

# Import dashboards from ./backend/monitoring/grafana/dashboards/
```

> [!CAUTION]
> Never use default credentials in production environments. Change all passwords during the first login.

### Configure Alerts

```bash
# Edit alert rules
nano backend/monitoring/alert_rules.yml

# Restart Prometheus
docker-compose restart prometheus
```

---

## Verification

### Health Checks

```bash
# Check all services
docker-compose ps

# Check service health
curl http://localhost:8000/health

# Check database connection
docker-compose exec timescaledb pg_isready -U omaya_user

# Check Redis
docker-compose exec redis redis-cli ping
```

### Functionality Tests

```bash
# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/machines
curl http://localhost:8000/docs

# Test frontend
# Open browser to http://localhost

# Test WebSocket connection
# Use browser console or WebSocket client
ws://localhost:8000/ws
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API performance
ab -n 1000 -c 10 http://localhost:8000/api/machines

# Test frontend performance
ab -n 1000 -c 10 http://localhost/
```

---

## Uninstallation

### Docker Compose Removal

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Remove everything
docker-compose down -v --rmi all --remove-orphans
```

### Manual Removal

```bash
# Stop services
sudo service timescaledb stop
sudo service redis-server stop

# Remove packages
sudo apt-get remove timescaledb-2-postgresql-15 redis-server

# Remove data directories
sudo rm -rf /var/lib/postgresql
sudo rm -rf /var/lib/redis

# Remove application files
rm -rf /path/to/OMAYA-industrial
```

---

## Troubleshooting

### Port Conflicts

If ports are already in use:

```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :8000

# Change ports in docker-compose.yml
# Edit port mappings:
ports:
  - "8080:80"  # Change from 80:80
```

### Permission Issues

```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER /path/to/OMAYA-industrial
```

### Memory Issues

```bash
# Check Docker memory allocation
docker system df

# Clean up unused resources
docker system prune -a

# Increase Docker memory limit
# In Docker Desktop: Settings > Resources > Memory
```

### Network Issues

```bash
# Check Docker network
docker network ls
docker network inspect omaya-network

# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

---

## Support

For additional help:
- Documentation: [https://docs.omaya-platform.com](https://docs.omaya-platform.com)
- Issues: [https://github.com/Def-Coms/OMAYA-industrial/issues](https://github.com/Def-Coms/OMAYA-industrial/issues)
- Email: support@omaya-platform.com

---

**Version**: 2.4.2
**Last Updated**: March 2025
