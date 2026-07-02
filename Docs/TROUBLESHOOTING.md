# Troubleshooting Guide

## Table of Contents

- [Overview](#overview)
- [Common Issues](#common-issues)
- [Installation Issues](#installation-issues)
- [Docker Issues](#docker-issues)
- [Database Issues](#database-issues)
- [API Issues](#api-issues)
- [Frontend Issues](#frontend-issues)
- [Sensor Issues](#sensor-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)
- [Monitoring Issues](#monitoring-issues)
- [Debugging Tools](#debugging-tools)
- [Getting Help](#getting-help)

---

## Overview

This guide provides solutions to common issues encountered when deploying and operating the OMAYA Platform. It covers installation, runtime, and performance troubleshooting.

### Troubleshooting Approach

1. **Identify the Problem**: Clearly define what's not working
2. **Gather Information**: Collect logs, metrics, and error messages
3. **Isolate the Issue**: Determine which component is affected
4. **Apply Solution**: Follow the appropriate troubleshooting steps
5. **Verify Fix**: Confirm the issue is resolved
6. **Document**: Record the solution for future reference

---

## Common Issues

### Platform Not Starting

**Symptoms**:
- Services fail to start
- Containers exit immediately
- Connection refused errors

**Possible Causes**:
- Port conflicts
- Resource limitations
- Configuration errors
- Missing dependencies

**Solutions**:

1. **Check Port Availability**:
```bash
# Check what's using the ports
sudo lsof -i :80
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :6379
```

2. **Check Docker Resources**:
```bash
# Check Docker system resources
docker system df

# Check container resource usage
docker stats
```

3. **Review Logs**:
```bash
# Check container logs
docker-compose logs api
docker-compose logs frontend
docker-compose logs timescaledb
```

4. **Verify Configuration**:
```bash
# Check environment variables
docker-compose config

# Validate docker-compose.yml
docker-compose config --resolve-image-digests
```

### High CPU/Memory Usage

**Symptoms**:
- System becomes unresponsive
- Containers are killed by OOM killer
- Slow response times

**Possible Causes**:
- Insufficient resources
- Memory leaks
- Inefficient queries
- Too many concurrent connections

**Solutions**:

1. **Monitor Resource Usage**:
```bash
# Check resource usage
docker stats --no-stream

# Check system resources
htop
top
```

2. **Optimize Database Queries**:
```sql
-- Check slow queries
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Create missing indexes
CREATE INDEX idx_telemetry_machine_timestamp ON telemetry(machine_id, timestamp DESC);
```

3. **Adjust Resource Limits**:
```yaml
# In docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

4. **Enable Connection Pooling**:
```python
# Backend configuration
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 40,
    'pool_timeout': 30
}
```

### Data Not Updating

**Symptoms**:
- Dashboard shows stale data
- Real-time updates not working
- WebSocket connection issues

**Possible Causes**:
- WebSocket connection failure
- Kafka not processing messages
- Database write issues
- Cache not invalidating

**Solutions**:

1. **Check WebSocket Connection**:
```bash
# Test WebSocket connection
wscat -c ws://localhost:8000/ws

# Check WebSocket logs
docker-compose logs api | grep websocket
```

2. **Verify Kafka Status**:
```bash
# Check Kafka topics
docker-compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

# Check consumer lag
docker-compose exec kafka kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group omaya-processor
```

3. **Clear Cache**:
```bash
# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Or clear specific keys
docker-compose exec redis redis-cli KEYS "omaya:*" | xargs redis-cli DEL
```

4. **Check Database Writes**:
```sql
-- Check recent inserts
SELECT COUNT(*) FROM telemetry WHERE timestamp > NOW() - INTERVAL '5 minutes';

-- Check for locks
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

---

## Installation Issues

### Docker Installation Fails

**Symptoms**:
- Docker won't install
- Docker daemon won't start
- Permission errors

**Solutions**:

1. **Install Docker Correctly**:
```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

2. **Start Docker Daemon**:
```bash
# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

3. **Fix Permission Issues**:
```bash
# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Or add user to docker group (recommended)
sudo usermod -aG docker $USER
```

### Dependencies Installation Fails

**Symptoms**:
- npm install fails
- pip install fails
- Build errors

**Solutions**:

1. **Clear npm Cache**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

2. **Use Python Virtual Environment**:
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Install System Dependencies**:
```bash
# Install build dependencies
sudo apt-get install build-essential python3-dev

# Install specific dependencies
sudo apt-get install libpq-dev python3-psycopg2
```

---

## Docker Issues

### Container Won't Start

**Symptoms**:
- Container exits immediately
- Container stuck in restarting state
- Container won't start

**Solutions**:

1. **Check Container Logs**:
```bash
# View container logs
docker logs omaya-api

# View last 100 lines
docker logs --tail 100 omaya-api

# Follow logs in real-time
docker logs -f omaya-api
```

2. **Inspect Container**:
```bash
# Inspect container details
docker inspect omaya-api

# Check container state
docker ps -a
```

3. **Rebuild Container**:
```bash
# Rebuild without cache
docker-compose build --no-cache api

# Restart container
docker-compose up -d api
```

4. **Check Health Status**:
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' omaya-api

# Check health logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' omaya-api
```

### Docker Network Issues

**Symptoms**:
- Containers can't communicate
- DNS resolution fails
- Network connectivity issues

**Solutions**:

1. **Check Network Configuration**:
```bash
# List networks
docker network ls

# Inspect network
docker network inspect omaya-network

# Check container network
docker inspect omaya-api | grep Network
```

2. **Recreate Network**:
```bash
# Stop all containers
docker-compose down

# Remove network
docker network rm omaya-network

# Recreate network
docker-compose up -d
```

3. **Test Connectivity**:
```bash
# Test from one container to another
docker-compose exec api ping redis

# Test DNS resolution
docker-compose exec api nslookup redis
```

### Docker Volume Issues

**Symptoms**:
- Data persistence issues
- Volume mount errors
- Permission denied on volumes

**Solutions**:

1. **Check Volume Status**:
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect omaya_redis-data

# Check volume usage
docker system df -v
```

2. **Fix Volume Permissions**:
```bash
# Change volume ownership
sudo chown -R $USER:$USER /var/lib/docker/volumes

# Or use named volumes with proper permissions
```

3. **Backup and Restore Volume**:
```bash
# Backup volume
docker run --rm -v omaya_redis-data:/data -v $(pwd):/backup ubuntu tar czf /backup/redis-backup.tar.gz /data

# Restore volume
docker run --rm -v omaya_redis-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/redis-backup.tar.gz -C /
```

---

## Database Issues

### Database Connection Failed

**Symptoms**:
- Can't connect to database
- Connection timeout errors
- Authentication failures

**Solutions**:

1. **Check Database Status**:
```bash
# Check if database is running
docker-compose ps timescaledb

# Check database logs
docker-compose logs timescaledb

# Test connection
docker-compose exec timescaledb pg_isready -U omaya_user
```

2. **Verify Credentials**:
```bash
# Check environment variables
docker-compose exec api env | grep TIMESCALE

# Test connection manually
docker-compose exec timescaledb psql -U omaya_user -d omaya_monitoring
```

3. **Check Network Connectivity**:
```bash
# Test from API container
docker-compose exec api ping timescaledb

# Check port accessibility
docker-compose exec api nc -zv timescaledb 5432
```

4. **Reset Database Password**:
```bash
# Access database
docker-compose exec timescaledb psql -U postgres

# Reset password
ALTER USER omaya_user WITH PASSWORD 'new_password';
```

### Slow Database Performance

**Symptoms**:
- Queries taking too long
- High CPU usage
- Connection pool exhaustion

**Solutions**:

1. **Analyze Slow Queries**:
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

2. **Create Missing Indexes**:
```sql
-- Analyze query patterns
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Create appropriate indexes
CREATE INDEX CONCURRENTLY idx_telemetry_machine_timestamp 
ON telemetry(machine_id, timestamp DESC);
```

3. **Optimize Configuration**:
```sql
-- Increase shared buffers
ALTER SYSTEM SET shared_buffers = '4GB';

-- Increase work memory
ALTER SYSTEM SET work_mem = '256MB';

-- Increase maintenance work memory
ALTER SYSTEM SET maintenance_work_mem = '1GB';

-- Apply changes
SELECT pg_reload_conf();
```

4. **Vacuum and Analyze**:
```sql
-- Vacuum and analyze tables
VACUUM ANALYZE telemetry;
VACUUM ANALYZE machines;
VACUUM ANALYZE alerts;
```

### Database Lock Issues

**Symptoms**:
- Queries hanging
- Lock wait timeouts
- Deadlock errors

**Solutions**:

1. **Check for Locks**:
```sql
-- Check current locks
SELECT 
    pid,
    usename,
    pg_blocking_pids(pid) AS blocked_by,
    query,
    state
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```

2. **Kill Blocking Processes**:
```sql
-- Terminate blocking process
SELECT pg_terminate_backend(pid);
```

3. **Set Lock Timeout**:
```sql
-- Set lock timeout to prevent long waits
SET lock_timeout = '30s';
```

---

## API Issues

### API Returns 500 Errors

**Symptoms**:
- Internal server errors
- Unhandled exceptions
- Service crashes

**Solutions**:

1. **Check API Logs**:
```bash
# View API logs
docker-compose logs api

# Filter for errors
docker-compose logs api | grep ERROR
```

2. **Enable Debug Mode**:
```python
# In backend/.env
DEBUG=true
LOG_LEVEL=DEBUG
```

3. **Check Python Errors**:
```bash
# Access API container
docker-compose exec api python

# Test imports
import sys
try:
    from backend.main import app
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
```

4. **Verify Dependencies**:
```bash
# Check installed packages
docker-compose exec api pip list

# Reinstall dependencies
docker-compose exec api pip install -r requirements.txt --force-reinstall
```

### API Authentication Fails

**Symptoms**:
- 401 Unauthorized errors
- Token validation failures
- Permission denied

**Solutions**:

1. **Verify JWT Secret**:
```bash
# Check JWT secret in environment
docker-compose exec api env | grep JWT_SECRET

# Ensure it matches between services
```

2. **Test Token Generation**:
```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

3. **Check Token Expiration**:
```python
# Verify token expiration
import jwt
token = "your-token-here"
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded.get('exp'))
```

4. **Reset Admin Password**:
```python
# In backend container
from backend.auth import get_password_hash
from backend.database import SessionLocal, User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()
user.password_hash = get_password_hash("new_password")
db.commit()
```

### API Rate Limiting

**Symptoms**:
- 429 Too Many Requests errors
- Requests being blocked
- Rate limit exceeded

**Solutions**:

1. **Check Rate Limit Status**:
```bash
# Check rate limit headers
curl -I http://localhost:8000/api/machines

# Look for X-RateLimit-* headers
```

2. **Adjust Rate Limits**:
```python
# In backend/rate_limiter.py
RATE_LIMITS = {
    "public": {"requests": 2000, "window": 60},  # Increased
    "authenticated": {"requests": 5000, "window": 60}
}
```

3. **Clear Rate Limit Cache**:
```bash
# Clear Redis rate limit keys
docker-compose exec redis redis-cli KEYS "ratelimit:*" | xargs redis-cli DEL
```

---

## Frontend Issues

### Frontend Won't Build

**Symptoms**:
- Build errors
- TypeScript errors
- Dependency conflicts

**Solutions**:

1. **Clear Build Cache**:
```bash
# Clear npm cache
npm cache clean --force

# Remove build artifacts
rm -rf dist node_modules .vite

# Reinstall and build
npm install
npm run build
```

2. **Fix TypeScript Errors**:
```bash
# Check TypeScript errors
npm run build

# Fix specific errors
# Edit tsconfig.json if needed
```

3. **Update Dependencies**:
```bash
# Check for outdated packages
npm outdated

# Update specific package
npm update package-name

# Update all packages
npm update
```

### Frontend Runtime Errors

**Symptoms**:
- White screen
- Console errors
- Component crashes

**Solutions**:

1. **Check Browser Console**:
```javascript
// Open browser DevTools (F12)
// Check Console tab for errors
// Check Network tab for failed requests
```

2. **Check API Connectivity**:
```bash
# Test API from browser
curl http://localhost:8000/health

# Check CORS configuration
```

3. **Verify Environment Variables**:
```bash
# Check .env file
cat .env

# Ensure variables are set correctly
```

4. **Enable Debug Mode**:
```typescript
// In vite.config.ts
export default defineConfig({
  server: {
    hmr: true,
    strictPort: true
  }
})
```

---

## Sensor Issues

### Sensor Not Detected

**Symptoms**:
- Sensor not showing in system
- No data from sensor
- Connection timeout

**Solutions**:

1. **Check Sensor Power**:
```bash
# Verify sensor is powered
# Check power supply voltage
# Check power cables
```

2. **Test Network Connectivity**:
```bash
# Ping sensor IP
ping 192.168.1.100

# Check port accessibility
nc -zv 192.168.1.100 502  # For Modbus
```

3. **Verify Protocol Configuration**:
```python
# Check sensor configuration
# Ensure protocol matches sensor capabilities
# Verify connection parameters
```

4. **Test with Manufacturer Tools**:
```bash
# Use manufacturer's diagnostic software
# Verify sensor is working independently
```

### Sensor Data Inaccurate

**Symptoms**:
- Readings don't match expected values
- Drift over time
- Inconsistent data

**Solutions**:

1. **Calibrate Sensor**:
```python
# Run calibration procedure
from backend.sensor_calibration import calibrate_sensor
calibrate_sensor(sensor_id, reference_points)
```

2. **Check Scaling Factors**:
```python
# Verify scaling configuration
# Adjust scale factor if needed
```

3. **Check Environmental Factors**:
```bash
# Ensure sensor is in proper environment
# Check for interference
# Verify mounting position
```

4. **Compare with Reference Sensor**:
```bash
# Use known-good sensor for comparison
# Identify systematic errors
```

---

## Performance Issues

### Slow Response Times

**Symptoms**:
- API requests taking too long
- Dashboard loading slowly
- High latency

**Solutions**:

1. **Enable Caching**:
```python
# Enable Redis caching
from backend.redis_cache import RedisCache

cache = RedisCache()
cache.set('key', data, ttl=3600)
```

2. **Optimize Database Queries**:
```sql
-- Add appropriate indexes
-- Use query optimization
-- Limit result sets
```

3. **Implement Pagination**:
```python
# Use pagination for large datasets
def get_machines(page=1, limit=20):
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()
```

4. **Use CDN for Static Assets**:
```nginx
# Configure CDN for static files
location /static/ {
    proxy_pass https://cdn.omaya-platform.com/static/;
}
```

### High Memory Usage

**Symptoms**:
- Out of memory errors
- Containers being killed
- System swapping

**Solutions**:

1. **Monitor Memory Usage**:
```bash
# Check memory usage
docker stats --no-stream

# Check process memory
docker-compose exec api ps aux
```

2. **Optimize Memory Usage**:
```python
# Use generators instead of lists
def process_large_dataset():
    for item in large_dataset:
        yield process(item)

# Clear cache periodically
cache.invalidate_pattern('temp:*')
```

3. **Adjust Memory Limits**:
```yaml
# In docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 8G
```

4. **Enable Memory Profiling**:
```python
# Use memory profiler
import memory_profiler

@memory_profiler.profile
def memory_intensive_function():
    # Your code here
    pass
```

---

## Security Issues

### SSL/TLS Certificate Issues

**Symptoms**:
- Certificate errors
- HTTPS not working
- Mixed content warnings

**Solutions**:

1. **Check Certificate Validity**:
```bash
# Check certificate expiration
openssl x509 -in /path/to/cert.pem -noout -dates

# Check certificate chain
openssl s_client -connect omaya-platform.com:443 -showcerts
```

2. **Renew Certificate**:
```bash
# Using Let's Encrypt
certbot renew

# Or generate new self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

3. **Fix Certificate Chain**:
```nginx
# Ensure full certificate chain is included
ssl_certificate /etc/nginx/ssl/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/privkey.pem;
```

### Authentication Issues

**Symptoms**:
- Can't log in
- Session expired
- Permission denied

**Solutions**:

1. **Check User Database**:
```sql
-- Check if user exists
SELECT * FROM users WHERE username = 'admin';

-- Check user status
SELECT * FROM users WHERE is_active = true;
```

2. **Reset User Password**:
```python
from backend.auth import get_password_hash
from backend.database import SessionLocal, User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()
user.password_hash = get_password_hash("new_password")
db.commit()
```

3. **Check Session Configuration**:
```python
# Verify session settings
SESSION_CONFIG = {
    'expire_after': 3600,  # 1 hour
    'cookie_secure': True,
    'cookie_httponly': True
}
```

---

## Monitoring Issues

### Prometheus Not Scraping Metrics

**Symptoms**:
- No metrics in Prometheus
- Targets down
- Scraping errors

**Solutions**:

1. **Check Prometheus Configuration**:
```bash
# Check prometheus.yml
cat backend/monitoring/prometheus.yml

# Validate configuration
docker-compose exec prometheus promtool check config /etc/prometheus/prometheus.yml
```

2. **Check Target Status**:
```bash
# Access Prometheus UI
# http://localhost:9090/targets

# Check if targets are up
```

3. **Verify Metrics Endpoint**:
```bash
# Test metrics endpoint
curl http://localhost:8000/metrics

# Check if metrics are being exposed
```

4. **Restart Prometheus**:
```bash
# Restart Prometheus
docker-compose restart prometheus

# Check logs
docker-compose logs prometheus
```

### Grafana Dashboard Not Loading

**Symptoms**:
- Dashboards not showing data
- Data source connection errors
- Panel errors

**Solutions**:

1. **Check Data Source Configuration**:
```bash
# Access Grafana UI
# http://localhost:3001

# Check data sources in Configuration > Data Sources
# Test connection
```

2. **Verify Prometheus Connection**:
```bash
# Test from Grafana container
docker-compose exec grafana wget -O- http://prometheus:9090/api/v1/query?query=up
```

3. **Import Dashboards**:
```bash
# Import dashboards from JSON files
# Use Grafana UI: Create > Import
# Upload dashboard JSON
```

---

## Debugging Tools

### Docker Debugging

```bash
# Enter container shell
docker-compose exec api bash

# View container processes
docker-compose exec api ps aux

# Check container resources
docker-compose exec api top

# Network debugging
docker-compose exec api netstat -tulpn
```

### Database Debugging

```sql
-- Check query performance
EXPLAIN ANALYZE SELECT * FROM machines;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### API Debugging

```bash
# Test API endpoints
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/api/machines
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Test with verbose output
curl -v http://localhost:8000/health

# Test WebSocket
wscat -c ws://localhost:8000/ws
```

### Log Analysis

```bash
# Search for errors
docker-compose logs api | grep ERROR

# Search for specific patterns
docker-compose logs api | grep "connection"

# Count error occurrences
docker-compose logs api | grep ERROR | wc -l

# Export logs
docker-compose logs api > api-logs.txt
```

---

## Getting Help

### Collect Diagnostic Information

```bash
# Create diagnostic script
#!/bin/bash
echo "=== Docker Status ==="
docker-compose ps
echo ""
echo "=== Docker Logs (Last 100 lines) ==="
docker-compose logs --tail=100
echo ""
echo "=== System Resources ==="
docker stats --no-stream
echo ""
echo "=== Network Configuration ==="
docker network inspect omaya-network
echo ""
echo "=== Volume Status ==="
docker volume ls
```

### Contact Support

When contacting support, provide:

1. **System Information**:
   - Platform version
   - Operating system
   - Docker version
   - Resource specifications

2. **Error Messages**:
   - Exact error messages
   - Timestamps
   - Affected components

3. **Logs**:
   - Relevant log files
   - Diagnostic output
   - Configuration files

4. **Steps Taken**:
   - What you've tried
   - Results of troubleshooting steps
   - Current system state

### Support Channels

- **Documentation**: [https://docs.omaya-platform.com](https://docs.omaya-platform.com)
- **Issues**: [https://github.com/Bunay-1/OMAYA-Project/issues](https://github.com/Bunay-1/OMAYA-Project/issues)
- **Email**: support@omaya-platform.com
- **Slack**: #omaya-support (for enterprise customers)

---

## Prevention

### Regular Maintenance

1. **Daily**:
   - Check system health dashboard
   - Review critical alerts
   - Monitor disk space usage

2. **Weekly**:
   - Review performance metrics
   - Check AI model drift
   - Backup configuration files

3. **Monthly**:
   - Update AI models if needed
   - Review and optimize database
   - Security updates and patches

### Monitoring Setup

1. **Set Up Alerts**:
   - Configure critical alerts
   - Set up notification channels
   - Define escalation procedures

2. **Performance Baseline**:
   - Establish baseline metrics
   - Set performance thresholds
   - Monitor for deviations

3. **Capacity Planning**:
   - Monitor resource trends
   - Plan for growth
   - Scale proactively

---

**Version**: 3.1.0
**Last Updated**: June 2026
