# Deployment Guide

## Table of Contents

- [Overview](#overview)
- [Deployment Options](#deployment-options)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Multi-Region Deployment](#multi-region-deployment)
- [Production Configuration](#production-configuration)
- [Scaling Strategies](#scaling-strategies)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Security Hardening](#security-hardening)
- [Performance Tuning](#performance-tuning)

---

## Overview

This guide covers deployment strategies for the OMAYA Platform in production environments. It includes instructions for Docker Compose, Kubernetes, and multi-region deployments.

### Deployment Considerations

- **High Availability**: Multiple instances with load balancing
- **Scalability**: Horizontal and vertical scaling options
- **Security**: TLS encryption, authentication, network isolation
- **Monitoring**: Comprehensive logging and metrics collection
- **Backup**: Automated backup and disaster recovery
- **Performance**: Optimized resource allocation and caching

---

## Deployment Options

### Option 1: Docker Compose (Small to Medium Deployments)

**Best for**: 1-100 machines, single region, moderate traffic

**Pros**:
- Simple setup and management
- Lower infrastructure overhead
- Easy to maintain
- Cost-effective for smaller deployments

**Cons**:
- Limited scalability
- Single point of failure
- Manual scaling required
- Limited multi-region support

### Option 2: Kubernetes (Large Deployments)

**Best for**: 100+ machines, multiple regions, high traffic

**Pros**:
- Automatic scaling
- Self-healing capabilities
- Multi-region support
- Advanced load balancing
- Rolling updates

**Cons**:
- Higher complexity
- Requires Kubernetes expertise
- Higher infrastructure costs
- Steeper learning curve

### Option 3: Multi-Region (Enterprise Deployments)

**Best for**: Global operations, disaster recovery, low latency

**Pros**:
- Geographic redundancy
- Disaster recovery
- Low latency for users
- Compliance with data residency

**Cons**:
- Highest complexity
- Significant infrastructure costs
- Data synchronization challenges
- Requires DevOps expertise

---

## Docker Compose Deployment

### Production Docker Compose

#### Prerequisites

- Docker 20.x or higher
- Docker Compose 2.x or higher
- 8+ CPU cores
- 16+ GB RAM
- 100+ GB SSD storage

#### Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Frontend (React + Nginx)
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: omaya-frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      api:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - omaya-network
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl
    environment:
      - NGINX_SSL_ENABLED=true
      - NGINX_SSL_CERT=/etc/nginx/ssl/cert.pem
      - NGINX_SSL_KEY=/etc/nginx/ssl/key.pem

  # FastAPI Backend (Multiple instances)
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: omaya-api
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - TIMESCALE_HOST=timescaledb
      - TIMESCALE_PORT=5432
      - TIMESCALE_USER=${TIMESCALE_USER}
      - TIMESCALE_PASSWORD=${TIMESCALE_PASSWORD}
      - TIMESCALE_DB=${TIMESCALE_DB}
      - ENABLE_METRICS=true
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      redis:
        condition: service_healthy
      timescaledb:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - omaya-network
    volumes:
      - ./backend/models:/app/models
      - ./backend/logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  # Redis Cache with persistence
  redis:
    image: redis:7-alpine
    container_name: omaya-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - omaya-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  # TimescaleDB with backup
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: omaya-timescaledb
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=${TIMESCALE_USER}
      - POSTGRES_PASSWORD=${TIMESCALE_PASSWORD}
      - POSTGRES_DB=${TIMESCALE_DB}
    volumes:
      - timescale-data:/var/lib/postgresql/data
      - ./backups/postgresql:/backups
    restart: unless-stopped
    networks:
      - omaya-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${TIMESCALE_USER} -d ${TIMESCALE_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G

  # Kafka with replication
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: omaya-kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_RETENTION_BYTES: 1073741824
      KAFKA_NUM_PARTITIONS: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
    restart: unless-stopped
    networks:
      - omaya-network
    volumes:
      - kafka-data:/var/lib/kafka/data
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  # Zookeeper
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: omaya-zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_SYNC_LIMIT: 2
      ZOOKEEPER_INIT_LIMIT: 5
    restart: unless-stopped
    networks:
      - omaya-network
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  # Prometheus with persistent storage
  prometheus:
    image: prom/prometheus:latest
    container_name: omaya-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./backend/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./backend/monitoring/alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    restart: unless-stopped
    networks:
      - omaya-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  # Grafana with persistent storage
  grafana:
    image: grafana/grafana:latest
    container_name: omaya-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_INSTALL_PLUGINS=
      - GF_SERVER_ROOT_URL=https://grafana.omaya.com
    volumes:
      - grafana-data:/var/lib/grafana
      - ./backend/monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./backups/grafana:/backups/grafana
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - omaya-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

networks:
  omaya-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  redis-data:
  timescale-data:
  kafka-data:
  zookeeper-data:
  prometheus-data:
  grafana-data:
```

#### Environment Variables

Create `.env.production`:

```env
# Database
TIMESCALE_USER=omaya_prod_user
TIMESCALE_PASSWORD=strong_secure_password_here
TIMESCALE_DB=omaya_production

# Redis
REDIS_PASSWORD=strong_redis_password_here

# Security
JWT_SECRET=very_long_secure_random_secret_key_here

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=strong_grafana_password_here
```

#### Deployment Commands

```bash
# Build and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=4

# Check status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes 1.25+ cluster
- kubectl configured
- Helm 3.x installed
- 16+ CPU cores across cluster
- 32+ GB RAM across cluster
- Persistent storage provisioner

### Helm Chart Structure

```
backend/kubernetes/helm/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   └── networkpolicy.yaml
└── charts/
```

### Helm Chart Installation

#### Add Helm Repository

```bash
helm repo add omaya https://charts.omaya-platform.com
helm repo update
```

#### Install Chart

```bash
# Install with default values
helm install omaya ./backend/kubernetes/helm

# Install with production values
helm install omaya ./backend/kubernetes/helm -f ./backend/kubernetes/helm/values-prod.yaml

# Install with custom values
helm install omaya ./backend/kubernetes/helm --set image.tag=2.4.2 --set replicaCount=3
```

#### Production Values (values-prod.yaml)

```yaml
# Global settings
global:
  imagePullSecrets:
    - name: regcred
  environment: production

# Frontend configuration
frontend:
  image:
    repository: omaya-platform/frontend
    tag: "2.4.2"
    pullPolicy: Always
  
  replicaCount: 3
  
  resources:
    limits:
      cpu: "1"
      memory: "512Mi"
    requests:
      cpu: "500m"
      memory: "256Mi"
  
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  
  ingress:
    enabled: true
    className: "nginx"
    annotations:
      cert-manager.io/cluster-issuer: "letsencrypt-prod"
      nginx.ingress.kubernetes.io/ssl-redirect: "true"
    hosts:
      - host: omaya-platform.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: omaya-platform-tls
        hosts:
          - omaya-platform.com

# Backend API configuration
api:
  image:
    repository: omaya-platform/backend
    tag: "2.4.2"
    pullPolicy: Always
  
  replicaCount: 4
  
  resources:
    limits:
      cpu: "2"
      memory: "4Gi"
    requests:
      cpu: "1"
      memory: "2Gi"
  
  autoscaling:
    enabled: true
    minReplicas: 4
    maxReplicas: 20
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  
  service:
    type: ClusterIP
    port: 8000
  
  env:
    - name: REDIS_HOST
      value: "omaya-redis"
    - name: TIMESCALE_HOST
      value: "omaya-timescaledb"
    - name: KAFKA_BOOTSTRAP_SERVERS
      value: "omaya-kafka:9092"
  
  secrets:
    enabled: true
    secretName: omaya-api-secrets

# Redis configuration
redis:
  enabled: true
  image:
    repository: redis
    tag: "7-alpine"
  
  resources:
    limits:
      cpu: "1"
      memory: "2Gi"
    requests:
      cpu: "500m"
      memory: "1Gi"
  
  persistence:
    enabled: true
    size: 10Gi
    storageClass: "fast-ssd"

# TimescaleDB configuration
timescaledb:
  enabled: true
  image:
    repository: timescale/timescaledb
    tag: "latest-pg15"
  
  resources:
    limits:
      cpu: "4"
      memory: "8Gi"
    requests:
      cpu: "2"
      memory: "4Gi"
  
  persistence:
    enabled: true
    size: 100Gi
    storageClass: "fast-ssd"
  
  backup:
    enabled: true
    schedule: "0 2 * * *"
    retention: 30

# Kafka configuration
kafka:
  enabled: true
  replicaCount: 3
  
  resources:
    limits:
      cpu: "2"
      memory: "4Gi"
    requests:
      cpu: "1"
      memory: "2Gi"
  
  persistence:
    enabled: true
    size: 50Gi
    storageClass: "fast-ssd"

# Monitoring configuration
prometheus:
  enabled: true
  resources:
    limits:
      cpu: "2"
      memory: "4Gi"
    requests:
      cpu: "1"
      memory: "2Gi"
  
  persistence:
    enabled: true
    size: 50Gi
    storageClass: "fast-ssd"

grafana:
  enabled: true
  resources:
    limits:
      cpu: "1"
      memory: "2Gi"
    requests:
      cpu: "500m"
      memory: "1Gi"
  
  persistence:
    enabled: true
    size: 10Gi
    storageClass: "fast-ssd"
  
  ingress:
    enabled: true
    annotations:
      cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

### Kubernetes Deployment Commands

```bash
# Create namespace
kubectl create namespace omaya-production

# Create secrets
kubectl create secret generic omaya-api-secrets \
  --from-literal=jwt-secret=your-secret \
  --from-literal=timescale-password=your-password \
  -n omaya-production

# Create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=registry.omaya-platform.com \
  --docker-username=your-username \
  --docker-password=your-password \
  -n omaya-production

# Install Helm chart
helm install omaya ./backend/kubernetes/helm \
  -f ./backend/kubernetes/helm/values-prod.yaml \
  -n omaya-production

# Check deployment status
kubectl get pods -n omaya-production
kubectl get services -n omaya-production
kubectl get ingress -n omaya-production

# Scale deployment
kubectl scale deployment omaya-api --replicas=10 -n omaya-production

# Check HPA status
kubectl get hpa -n omaya-production
```

---

## Multi-Region Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Region Deployment                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Primary Region (eu-west-1)                               │
│  ├── 4 API instances                                        │
│  ├── 2 Redis instances (master/slave)                       │
│  ├── TimescaleDB (primary)                                   │
│  ├── Kafka (3 brokers)                                      │
│  └── Monitoring stack                                       │
│                                                             │
│  Secondary Regions (us-east-1, ap-northeast-1, us-west-2) │
│  ├── 2 API instances each                                    │
│  ├── 1 Redis instance each                                  │
│  ├── TimescaleDB (read replicas)                            │
│  ├── Kafka (2 brokers each)                                 │
│  └── Monitoring stack                                       │
│                                                             │
│  Global Services                                            │
│  ├── CDN (CloudFlare)                                      │
│  ├── Global Load Balancer                                   │
│  ├── DNS (Route53)                                          │
│  └── Centralized Monitoring                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Configuration

#### Primary Region (eu-west-1)

```yaml
# values-primary.yaml
global:
  region: eu-west-1
  environment: production
  isPrimary: true

api:
  replicaCount: 4
  
  service:
    type: LoadBalancer
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"

timescaledb:
  replication:
    enabled: true
    mode: primary
  readReplicas:
    enabled: true
    regions:
      - us-east-1
      - ap-northeast-1
      - us-west-2
```

#### Secondary Regions

```yaml
# values-secondary.yaml
global:
  region: us-east-1
  environment: production
  isPrimary: false

api:
  replicaCount: 2
  
  service:
    type: LoadBalancer
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"

timescaledb:
  replication:
    enabled: true
    mode: replica
  primaryHost: omaya-timescaledb.eu-west-1.omaya.internal
```

### Deployment Commands

```bash
# Deploy to primary region
kubectl config use-context eu-west-1
helm install omaya-primary ./backend/kubernetes/helm \
  -f ./backend/kubernetes/helm/values-primary.yaml \
  -n omaya-production

# Deploy to secondary regions
kubectl config use-context us-east-1
helm install omaya-secondary-us ./backend/kubernetes/helm \
  -f ./backend/kubernetes/helm/values-secondary.yaml \
  -n omaya-production

kubectl config use-context ap-northeast-1
helm install omaya-secondary-asia ./backend/kubernetes/helm \
  -f ./backend/kubernetes/helm/values-secondary.yaml \
  -n omaya-production

kubectl config use-context us-west-2
helm install omaya-secondary-west ./backend/kubernetes/helm \
  -f ./backend/kubernetes/helm/values-secondary.yaml \
  -n omaya-production
```

### Data Synchronization

#### TimescaleDB Replication

```sql
-- Configure streaming replication
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_replication_slots = 10;

-- Create publication
CREATE PUBLICATION omaya_pub FOR ALL TABLES;
```

#### Kafka Cross-Region Replication

```yaml
# MirrorMaker configuration
clusters:
  - name: primary
    bootstrap.servers: "omaya-kafka.eu-west-1:9092"
  
  - name: secondary
    bootstrap.servers: "omaya-kafka.us-east-1:9092"

topics:
  - name: telemetry
    replication_factor: 2
    include: "telemetry.*"
```

---

## Production Configuration

### SSL/TLS Configuration

#### Generate SSL Certificates

```bash
# Generate private key
openssl genrsa -out omaya.key 2048

# Generate CSR
openssl req -new -key omaya.key -out omaya.csr

# Generate self-signed certificate (for testing)
openssl x509 -req -days 365 -in omaya.csr -signkey omaya.key -out omaya.crt

# Or use Let's Encrypt for production
certbot certonly --standalone -d omaya-platform.com
```

#### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name omaya-platform.com;

    ssl_certificate /etc/nginx/ssl/omaya.crt;
    ssl_certificate_key /etc/nginx/ssl/omaya.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Other SSL configurations...
}
```

### Database Configuration

#### TimescaleDB Tuning

```sql
-- Memory configuration
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET work_mem = '256MB';

-- WAL configuration
ALTER SYSTEM SET wal_buffers = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET max_wal_size = '4GB';

-- Query optimization
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Apply changes
SELECT pg_reload_conf();
```

#### Connection Pooling

```python
# Backend connection pool configuration
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 40,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'echo': False
}
```

### Redis Configuration

```conf
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```

---

## Scaling Strategies

### Horizontal Pod Autoscaler (HPA)

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
  minReplicas: 4
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max
```

### Database Scaling

#### Read Replicas

```yaml
timescaledb:
  readReplicas:
    enabled: true
    count: 3
    resources:
      limits:
        cpu: "2"
        memory: "4Gi"
```

#### Connection Pooling

```python
# Increase pool size for high traffic
DATABASE_CONFIG = {
    'pool_size': 50,
    'max_overflow': 100
}
```

### Kafka Scaling

#### Increase Partitions

```bash
# Increase topic partitions
kafka-topics.sh --alter --bootstrap-server localhost:9092 \
  --topic telemetry --partitions 12
```

#### Add Brokers

```yaml
kafka:
  replicaCount: 5
```

---

## Monitoring & Logging

### Centralized Logging

#### ELK Stack Integration

```yaml
# Filebeat configuration
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
  - add_kubernetes_metadata

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

#### Log Aggregation

```python
# Structured logging
import structlog

logger = structlog.get_logger()
logger.info("api_request", 
            method="GET", 
            endpoint="/api/machines", 
            status_code=200,
            duration_ms=45)
```

### Monitoring Stack

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'omaya-api'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: omaya-api
```

#### Grafana Dashboards

Import pre-built dashboards:
- Fleet Overview Dashboard
- API Performance Dashboard
- Database Performance Dashboard
- System Resources Dashboard

---

## Backup & Recovery

### Database Backup

#### Automated Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec omaya-timescaledb pg_dump -U omaya_user omaya_monitoring > $BACKUP_DIR/backup_$DATE.sql
```

#### Restore Procedure

```bash
# Restore from backup
docker exec -i omaya-timescaledb psql -U omaya_user omaya_monitoring < backup_20240619_100000.sql
```

### Disaster Recovery

#### Recovery Time Objective (RTO): 4 hours
#### Recovery Point Objective (RPO): 1 hour

#### Recovery Steps

1. Assess damage and scope
2. Restore from latest backup
3. Verify data integrity
4. Restart services
5. Validate functionality
6. Monitor for issues

---

## Security Hardening

### Network Security

#### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: omaya-network-policy
spec:
  podSelector:
    matchLabels:
      app: omaya-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: omaya-frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: omaya-redis
    ports:
    - protocol: TCP
      port: 6379
```

### Application Security

#### Security Headers

```python
# Add security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

#### Rate Limiting

```python
# Configure rate limits
RATE_LIMITS = {
    "default": {"requests": 1000, "window": 60},
    "api/machines": {"requests": 100, "window": 60},
    "api/predict": {"requests": 50, "window": 60}
}
```

---

## Performance Tuning

### Backend Optimization

#### Caching Strategy

```python
# Redis caching configuration
CACHE_CONFIG = {
    'default_timeout': 300,
    'key_prefix': 'omaya',
    'max_entries': 10000
}

# Cache frequently accessed data
@cache(ttl=60)
def get_machine_list():
    return fetch_machines_from_db()
```

#### Database Query Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_machines_zone ON machines(zone);
CREATE INDEX idx_telemetry_machine_timestamp ON telemetry(machine_id, timestamp DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity, created_at DESC);
```

### Frontend Optimization

#### Code Splitting

```typescript
// Lazy load components
const PredictiveMaintenancePanel = lazy(() => 
  import('./components/dashboard/PredictiveMaintenancePanel')
);
```

#### Image Optimization

```typescript
// Use next/image for optimized images
import Image from 'next/image';

<Image 
  src="/logo.png" 
  alt="OMAYA Logo" 
  width={200} 
  height={50}
  loading="lazy"
/>
```

---

## Support

For additional help:
- Documentation: [https://docs.omaya-platform.com](https://docs.omaya-platform.com)
- Issues: [https://github.com/Def-Coms/OMAYA-industrial/issues](https://github.com/Def-Coms/OMAYA-industrial/issues)
- Email: deployment-support@omaya-platform.com

---

**Version**: 2.4.2
**Last Updated**: March 2025
