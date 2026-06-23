"""
Prometheus Metrics Instrumentation
Exposes metrics for monitoring API and system health
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)

# Machine Metrics
machines_total = Gauge(
    'machines_total',
    'Total number of monitored machines'
)

machines_by_status = Gauge(
    'machines_by_status',
    'Number of machines by status',
    ['status']
)

# Alert Metrics
alerts_total = Counter(
    'alerts_total',
    'Total number of alerts generated',
    ['severity']
)

active_alerts = Gauge(
    'active_alerts',
    'Number of currently active alerts',
    ['severity']
)

# AI Prediction Metrics
prediction_requests_total = Counter(
    'prediction_requests_total',
    'Total number of AI prediction requests',
    ['model_type']
)

prediction_duration_seconds = Histogram(
    'prediction_duration_seconds',
    'AI prediction duration in seconds',
    ['model_type']
)

failure_probability_gauge = Gauge(
    'machine_failure_probability',
    'Current failure probability for machines',
    ['machine_id']
)

rul_hours_gauge = Gauge(
    'machine_rul_hours',
    'Remaining useful life in hours',
    ['machine_id']
)

# WebSocket Metrics
websocket_connections = Gauge(
    'websocket_connections',
    'Number of active WebSocket connections'
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'Total number of WebSocket messages',
    ['direction']  # sent or received
)

# Redis Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total number of cache hits'
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total number of cache misses'
)

# System Health Metrics
system_health = Gauge(
    'system_health_status',
    'Overall system health status (1=healthy, 0=unhealthy)'
)


class MetricsMiddleware:
    """Middleware to track API metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Track metrics
                duration = time.time() - start_time
                method = scope["method"]
                path = scope["path"]
                status = message["status"]
                
                api_requests_total.labels(
                    method=method,
                    endpoint=path,
                    status=status
                ).inc()
                
                api_request_duration_seconds.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def metrics_endpoint():
    """Generate Prometheus metrics"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
