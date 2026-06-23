#!/bin/bash

# OMAYA Fleet Monitoring - Startup Script
# Validates configuration and starts all services

set -e

echo "🔍 Validating configuration..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your configuration"
fi

# Source environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required variables
REQUIRED_VARS=("REDIS_HOST" "REDIS_PORT" "API_PORT")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required variable $var is not set in .env"
        exit 1
    fi
done

echo "✅ Configuration validated"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    exit 1
fi

echo "🐳 Starting Docker containers..."

# Build and start services
docker-compose up -d --build

echo "⏳ Waiting for services to be ready..."

# Wait for Redis
echo "Checking Redis..."
timeout 30 bash -c 'until docker exec omaya-redis redis-cli ping 2>&1 | grep -q PONG; do sleep 1; done' || {
    echo "❌ Redis failed to start"
    exit 1
}
echo "✅ Redis is ready"

# Wait for TimescaleDB
echo "Checking TimescaleDB..."
timeout 60 bash -c 'until docker exec omaya-timescaledb pg_isready -U omaya_user 2>&1 | grep -q "accepting connections"; do sleep 2; done' || {
    echo "❌ TimescaleDB failed to start"
    exit 1
}
echo "✅ TimescaleDB is ready"

# Wait for Kafka
echo "Checking Kafka..."
timeout 90 bash -c 'until docker exec omaya-kafka kafka-topics --bootstrap-server localhost:9092 --list 2>&1 | grep -q "^"; do sleep 2; done' || {
    echo "❌ Kafka failed to start"
    exit 1
}
echo "✅ Kafka is ready"

# Initialize Kafka topics
echo "Initializing Kafka topics..."
docker exec omaya-api python kafka_init.py
echo "✅ Kafka topics created"

# Wait for API
echo "Checking API..."
timeout 60 bash -c 'until curl -s http://localhost:8000/health > /dev/null; do sleep 2; done' || {
    echo "❌ API failed to start"
    exit 1
}
echo "✅ API is ready"

# Run self-test
echo "🧪 Running system self-test..."
SELF_TEST=$(curl -s http://localhost:8000/api/self-test)
echo "$SELF_TEST" | jq .

if echo "$SELF_TEST" | jq -e '.status == "healthy"' > /dev/null; then
    echo "✅ Self-test passed"
else
    echo "⚠️  Self-test returned warnings"
fi

echo ""
echo "🎉 OMAYA Fleet Monitoring is ready!"
echo ""
echo "📊 Services:"
echo "  - API:          http://localhost:8000"
echo "  - API Docs:     http://localhost:8000/docs"
echo "  - Prometheus:   http://localhost:9090"
echo "  - Grafana:      http://localhost:3001 (admin/admin)"
echo "  - Alertmanager: http://localhost:9093"
echo "  - Kafka:        localhost:9092"
echo ""
echo "📝 Logs: docker-compose logs -f"
echo "🛑 Stop:  docker-compose down"
echo ""
