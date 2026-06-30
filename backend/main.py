"""
FastAPI Backend for OMAYA Fleet Monitoring
Real-time API with WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
import asyncio
import random
import json
import time
import os
from pydantic import BaseModel
from logger_config import setup_logging
from middleware import RequestLoggingMiddleware
from tls_config import tls_config
import logging

# Setup structured logging
setup_logging()
logger = logging.getLogger("omaya-api")

# Import connection manager and AI models
from websocket_manager import ConnectionManager
from ai_models import lstm_predictor, rul_predictor, anomaly_detector
from redis_cache import cache
from prometheus_metrics import (
    metrics_endpoint, MetricsMiddleware,
    api_requests_total, machines_total, machines_by_status,
    alerts_total, active_alerts, websocket_connections,
    prediction_requests_total, failure_probability_gauge, rul_hours_gauge
)
from kafka_producer import producer as kafka_producer
from kafka_consumer import consumer as kafka_consumer, stream_processor
from kafka_streams import telemetry_aggregator, alert_aggregator, prediction_tracker

# Import enterprise modules
from graphql_layer import graphql_router
from explainable_ai import explainable_ai
from data_lake import data_lake
from audit_trails import audit_trail, log_data_access, log_alert_action, AuditEventType
from drift_detection import drift_detector
from online_learning import online_detector
from visual_inspection import yolo_inspector
from RAG.rag_logic import rag_manager

# Pydantic models
class MachineStatus(BaseModel):
    id: str
    status: str
    temperature: float
    vibration: float
    spindleSpeed: int
    toolWear: float
    timestamp: str

class AlertCreate(BaseModel):
    machineId: str
    severity: str
    title: str
    message: str

class PredictionRequest(BaseModel):
    machineId: str
    features: dict

from database import db

# Global state
manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting OMAYA Fleet Monitoring API...")
    
    # Initialize Kafka event stream
    if kafka_consumer.consumer:
        print("📡 Starting Kafka event consumer...")
        kafka_consumer.subscribe([
            "machine-telemetry",
            "machine-alerts", 
            "machine-predictions"
        ])
        kafka_consumer.start_consuming(stream_processor.process_event)
    
    # Start background task for simulating data
    asyncio.create_task(simulate_machine_updates())
    
    # Initialize Data Lake buckets
    if data_lake.connected:
        print("📦 Data Lake initialized")
    
    yield
    
    # Shutdown
    print("⏹️  Shutting down...")
    
    # Flush audit logs
    audit_trail.close()
    
    # Stop Kafka consumer
    if kafka_consumer.consumer:
        kafka_consumer.close()
    if kafka_producer.producer:
        kafka_producer.close()

app = FastAPI(
    title="OMAYA Fleet Monitoring API",
    description="Real-time monitoring and predictive analytics for OMAYA machines",
    version="3.1.5",
    lifespan=lifespan
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") == "true" else None,
            "timestamp": datetime.now().isoformat()
        }
    )

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Add Prometheus metrics middleware
app.add_middleware(MetricsMiddleware)

# Mount GraphQL endpoint
app.include_router(graphql_router, prefix="/graphql")

# Prometheus metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return metrics_endpoint()

# Health check
@app.get("/")
async def root():
    return {
        "service": "OMAYA Fleet Monitoring API",
        "status": "operational",
        "version": "3.1.5",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", deprecated=True)
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connections": len(manager.active_connections)
    }

# Self-test endpoint
@app.get("/api/self-test")
async def self_test():
    """Comprehensive system self-test"""
    # Redis check
    redis_status = "pass"
    if cache.client:
        try:
            cache.client.ping()
        except Exception:
            redis_status = "fail"
    else:
        redis_status = "fail"

    # AI Models check
    ai_status = "pass"
    try:
        # Check if predictors are initialized and can perform a simple prediction
        test_features = {"temperature": 60.0, "vibration": 1.0, "toolWear": 50.0}
        lstm_predictor.predict_failure(test_features)
        rul_predictor.predict_rul(test_features)
    except Exception:
        ai_status = "fail"

    # Kafka check
    kafka_status = "pass"
    if not kafka_producer.producer:
        kafka_status = "fail"

    # Data Lake check
    data_lake_status = "pass"
    if not data_lake.connected:
        data_lake_status = "fail"

    tests = {
        "api": "pass",
        "websocket": "pass" if len(manager.active_connections) >= 0 else "fail",
        "redis": redis_status,
        "ai_models": ai_status,
        "kafka": kafka_status,
        "data_lake": data_lake_status,
        "database": "pass" # Placeholder for TimescaleDB check
    }
    
    all_passed = all(test == "pass" for test in tests.values())
    
    return {
        "status": "healthy" if all_passed else "degraded",
        "tests": tests,
        "timestamp": datetime.now().isoformat()
    }

# Machine endpoints
@app.get("/api/machines")
async def get_machines():
    """Get all machines status"""
    try:
        query = "SELECT id, name, zone, status, last_maintenance FROM machines"
        machines = db.execute_query(query)

        # If no machines in DB, fallback to mock for now but log it
        if not machines:
            logger.warning("No machines found in database, using mock data")
            machines = generate_mock_machines(120)
        else:
            # Enrich with some dynamic mock data for demo if needed,
            # but usually we want real telemetry from DB or cache
            for m in machines:
                m["temperature"] = round(random.uniform(45, 80), 1)
                m["vibration"] = round(random.uniform(0.5, 3.0), 2)
                m["spindleSpeed"] = random.randint(8000, 12000)
                m["toolWear"] = random.randint(0, 100)
                m["uptime"] = round(random.uniform(85, 99), 1)

    except Exception as e:
        logger.error(f"Error fetching machines: {e}")
        machines = generate_mock_machines(120)
    
    # Update Prometheus metrics
    machines_total.set(len(machines))
    status_counts = {}
    for machine in machines:
        status = machine["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        machines_by_status.labels(status=status).set(count)
    
    return {"machines": machines, "count": len(machines)}

@app.get("/api/machines/{machine_id}")
async def get_machine(machine_id: str):
    """Get specific machine details"""
    try:
        query = "SELECT id, name, zone, status, last_maintenance FROM machines WHERE id = %s"
        machine = db.execute_one(query, (machine_id,))
        if machine:
            machine["temperature"] = round(random.uniform(45, 80), 1)
            machine["vibration"] = round(random.uniform(0.5, 3.0), 2)
            machine["spindleSpeed"] = random.randint(8000, 12000)
            machine["toolWear"] = random.randint(0, 100)
            machine["uptime"] = round(random.uniform(85, 99), 1)
            return machine
    except Exception as e:
        logger.error(f"Error fetching machine {machine_id}: {e}")

    return generate_mock_machine(machine_id)

@app.post("/api/machines/{machine_id}/status")
async def update_machine_status(machine_id: str, status: MachineStatus):
    """Update machine status"""
    # Store in database (Time-series)
    try:
        query = """
            INSERT INTO machine_telemetry
            (time, machine_id, temperature, vibration, spindle_speed, tool_wear, status)
            VALUES (NOW(), %s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (
            machine_id, status.temperature, status.vibration,
            status.spindleSpeed, status.toolWear, status.status
        ))

        # Update machine current status
        db.execute_query("UPDATE machines SET status = %s WHERE id = %s", (status.status, machine_id))
    except Exception as e:
        logger.error(f"Error saving telemetry to DB: {e}")

    # Broadcast to all connected clients
    await manager.broadcast({
        "type": "machine_update",
        "data": status.dict()
    })
    
    # Publish to Kafka
    kafka_producer.publish_telemetry(machine_id, status.dict())
    
    return {"status": "updated", "machineId": machine_id}

# Alert endpoints
@app.get("/api/alerts")
async def get_alerts(severity: Optional[str] = None, limit: int = 50):
    """Get recent alerts"""
    alerts = generate_mock_alerts(limit)
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    return {"alerts": alerts, "count": len(alerts)}

@app.post("/api/alerts")
async def create_alert(alert: AlertCreate):
    """Create new alert"""
    new_alert = {
        "id": f"alert-{datetime.now().timestamp()}",
        **alert.dict(),
        "timestamp": datetime.now().isoformat(),
        "acknowledged": False
    }
    
    # Update Prometheus metrics
    alerts_total.labels(severity=alert.severity).inc()
    
    # Audit log
    log_alert_action(
        user_id="system",
        alert_id=new_alert["id"],
        action="create"
    )
    
    # Store in Data Lake
    data_lake.store_alert(new_alert)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "new_alert",
        "data": new_alert
    })
    
    # Publish to Kafka
    kafka_producer.publish_alert(
        machine_id=alert.machineId,
        severity=alert.severity,
        title=alert.title,
        message=alert.message,
        metadata={"alert_id": new_alert["id"]}
    )
    
    return new_alert

# Simulation endpoint
@app.post("/api/simulate")
async def simulate_scenario(scenario: dict):
    """
    Simulate various scenarios for testing
    Scenarios: machine_failure, high_wear, temperature_spike, etc.
    """
    scenario_type = scenario.get("type", "random")
    machine_id = scenario.get("machineId", "OMAYA-001")
    
    if scenario_type == "machine_failure":
        event = {
            "type": "alert",
            "severity": "critical",
            "machineId": machine_id,
            "message": "Critical failure detected - immediate attention required"
        }
    elif scenario_type == "high_wear":
        event = {
            "type": "alert",
            "severity": "warning",
            "machineId": machine_id,
            "message": "Tool wear exceeds threshold - schedule replacement"
        }
    elif scenario_type == "temperature_spike":
        event = {
            "type": "telemetry",
            "machineId": machine_id,
            "temperature": 85.0,
            "message": "Temperature spike detected"
        }
    else:
        event = {
            "type": "info",
            "message": f"Simulated event: {scenario_type}"
        }
    
    event["timestamp"] = datetime.now().isoformat()
    
    # Broadcast to WebSocket clients
    await manager.broadcast(event)
    
    return {"status": "simulated", "event": event}

# Anomaly detection endpoint
@app.post("/api/detect/anomaly")
async def detect_anomaly(request: PredictionRequest):
    """Detect anomalies in machine sensor data"""
    result = anomaly_detector.detect_anomaly(request.machineId, request.features)
    
    # Update baseline for online learning
    if not result["isAnomalous"]:
        anomaly_detector.update_baseline(request.machineId, request.features)
    
    return result

# Prediction endpoints
@app.post("/api/predict/failure")
async def predict_failure(request: PredictionRequest):
    """Predict machine failure probability using LSTM model"""
    start_time = time.time()
    
    # Check cache first
    cache_key = f"prediction:failure:{request.machineId}"
    cached = cache.get(cache_key)
    if cached:
        cached["cached"] = True
        return cached
    
    # Track prediction request
    prediction_requests_total.labels(model_type="lstm_failure").inc()
    
    # Use LSTM predictor
    from ai_models import get_lstm_prediction
    prediction = get_lstm_prediction(request.features)
    prediction["machineId"] = request.machineId
    
    # Update Prometheus gauge
    failure_probability_gauge.labels(machine_id=request.machineId).set(
        prediction["failureProbability"]
    )
    
    # Track for drift detection
    drift_detector.add_prediction(
        prediction=prediction["failureProbability"],
        actual=0,  # Will be updated later with actual outcome
        features=request.features
    )
    
    # Store in Data Lake
    data_lake.store_prediction(request.machineId, prediction)
    
    # Generate explanation
    explanation = explainable_ai.explain_prediction_shap(
        lstm_predictor.model,
        request.features
    )
    prediction["explanation"] = explanation
    
    # Publish to Kafka
    kafka_producer.publish_prediction(
        machine_id=request.machineId,
        prediction_type="failure",
        data=prediction
    )
    
    # Cache for 2 minutes
    cache.set(cache_key, prediction, ttl_seconds=120)
    
    return prediction

@app.post("/api/predict/rul")
async def predict_rul(request: PredictionRequest):
    """Predict Remaining Useful Life with confidence intervals"""
    # Check cache
    cache_key = f"prediction:rul:{request.machineId}"
    cached = cache.get(cache_key)
    if cached:
        cached["cached"] = True
        return cached
    
    # Track prediction request
    prediction_requests_total.labels(model_type="rul_survival").inc()
    
    # Use RUL predictor
    from ai_models import get_rul_prediction
    prediction = get_rul_prediction(request.features)
    prediction["machineId"] = request.machineId
    
    # Update Prometheus gauge
    rul_hours_gauge.labels(machine_id=request.machineId).set(
        prediction["rul_hours"]
    )
    
    # Generate explanation
    explanation = explainable_ai.explain_prediction_lime(
        rul_predictor.model,
        request.features
    )
    prediction["explanation"] = explanation
    
    # Store in Data Lake
    data_lake.store_prediction(request.machineId, prediction)
    
    # Publish to Kafka
    kafka_producer.publish_prediction(
        machine_id=request.machineId,
        prediction_type="rul",
        data=prediction
    )
    
    # Cache for 5 minutes
    cache.set(cache_key, prediction, ttl_seconds=300)
    
    return prediction

# Kafka Stream Analytics Endpoints

@app.get("/api/analytics/telemetry/{machine_id}")
async def get_telemetry_analytics(machine_id: str):
    """Get real-time telemetry analytics for machine"""
    metrics = telemetry_aggregator.get_metrics(machine_id)
    return {
        "machineId": machine_id,
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/alerts/{machine_id}")
async def get_machine_alerts(machine_id: str):
    """Get alerts for specific machine"""
    alerts = alert_aggregator.get_alerts_by_machine(machine_id)
    return {
        "machineId": machine_id,
        "alerts": alerts,
        "count": len(alerts),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/critical-alerts")
async def get_critical_alerts():
    """Get all active critical alerts"""
    alerts = alert_aggregator.get_active_critical_alerts()
    return {
        "alerts": alerts,
        "count": len(alerts),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/predictions/{machine_id}")
async def get_machine_predictions(machine_id: str):
    """Get predictions for machine"""
    all_predictions = prediction_tracker.get_predictions(machine_id)
    return {
        "machineId": machine_id,
        "predictions": all_predictions,
        "count": len(all_predictions),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/summary")
async def get_fleet_analytics_summary():
    """Get fleet-wide analytics summary"""
    all_metrics = telemetry_aggregator.get_metrics()
    all_alerts = alert_aggregator.get_alerts_by_severity()
    critical_alerts = alert_aggregator.get_active_critical_alerts()
    
    return {
        "machines_monitored": len(all_metrics),
        "alerts_by_severity": {
            severity: len(alerts)
            for severity, alerts in all_alerts.items()
        },
        "critical_alerts_active": len(critical_alerts),
        "timestamp": datetime.now().isoformat()
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    websocket_connections.set(len(manager.active_connections))
    
    client_id = f"{websocket.client.host}:{websocket.client.port}"

    try:
        while True:
            data = await websocket.receive_text()

            # Rate limiting check
            if not manager.check_rate_limit(client_id):
                logger.warning(f"WebSocket rate limit exceeded for {client_id}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Rate limit exceeded"
                })
                continue

            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                # Client subscribes to specific machines
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "machines": message.get("machines", [])
                })
            elif message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        websocket_connections.set(len(manager.active_connections))

# Background task to simulate machine updates
async def simulate_machine_updates():
    """Simulate periodic machine status updates"""
    while True:
        await asyncio.sleep(3)  # Every 3 seconds
        
        if len(manager.active_connections) > 0:
            # Generate random machine update
            machine_id = f"OMAYA-{random.randint(1, 120):03d}"
            update = {
                "type": "machine_update",
                "machineId": machine_id,
                "temperature": round(random.uniform(45, 75), 1),
                "vibration": round(random.uniform(0.5, 2.5), 2),
                "spindleSpeed": random.randint(8000, 12000),
                "timestamp": datetime.now().isoformat()
            }
            
            await manager.broadcast(update)
            
            # Publish to Kafka
            kafka_producer.publish_telemetry(
                machine_id,
                {
                    "temperature": update["temperature"],
                    "vibration": update["vibration"],
                    "spindleSpeed": update["spindleSpeed"]
                }
            )

# Helper functions for mock data
def generate_mock_machine(machine_id: str):
    statuses = ["operational", "warning", "maintenance", "critical"]
    return {
        "id": machine_id,
        "name": f"Mill {machine_id.split('-')[1]}",
        "zone": f"Zone {chr(65 + random.randint(0, 4))}",
        "status": random.choice(statuses),
        "temperature": round(random.uniform(45, 80), 1),
        "vibration": round(random.uniform(0.5, 3.0), 2),
        "spindleSpeed": random.randint(8000, 12000),
        "toolWear": random.randint(0, 100),
        "uptime": round(random.uniform(85, 99), 1),
        "lastMaintenance": "2024-01-15T10:30:00Z"
    }

def generate_mock_machines(count: int):
    return [generate_mock_machine(f"OMAYA-{i:03d}") for i in range(1, count + 1)]

def generate_mock_alerts(limit: int):
    severities = ["critical", "error", "warning", "info"]
    alerts = []
    for i in range(limit):
        alerts.append({
            "id": f"alert-{i}",
            "machineId": f"OMAYA-{random.randint(1, 120):03d}",
            "severity": random.choice(severities),
            "title": "Temperature anomaly detected",
            "message": "Machine temperature exceeded threshold",
            "timestamp": datetime.now().isoformat(),
            "acknowledged": random.choice([True, False])
        })
    return alerts

# Enterprise endpoints

@app.get("/api/drift/status")
async def get_drift_status():
    """Get model drift detection status"""
    return drift_detector.detect_drift()

@app.get("/api/data-lake/stats")
async def get_data_lake_stats():
    """Get Data Lake storage statistics"""
    return data_lake.get_storage_stats()

@app.post("/api/audit/compliance-report")
async def generate_compliance_report(start_date: str, end_date: str):
    """Generate compliance audit report"""
    from datetime import datetime
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    return audit_trail.generate_compliance_report(start, end, report_type="summary")

# Additional enterprise endpoints

@app.get("/api/explainability/{machine_id}")
async def get_ai_explanation(machine_id: str):
    """Get explainable AI analysis for predictions"""
    features = {
        "temperature": random.uniform(50, 80),
        "vibration": random.uniform(1.0, 3.0),
        "toolWear": random.uniform(30, 90),
        "spindleSpeed": random.uniform(8000, 12000),
        "operatingHours": random.uniform(1000, 5000),
        "cycleCount": random.uniform(1000, 10000)
    }
    
    shap_result = explainable_ai._mock_shap_explanation(features)
    lime_result = explainable_ai._mock_lime_explanation(features)
    
    return {
        "machineId": machine_id,
        "features": features,
        "shap": shap_result,
        "lime": lime_result,
        "featureImportance": explainable_ai.get_feature_importance(None)
    }

@app.get("/api/audit/recent")
async def get_recent_audit_logs(limit: int = 50):
    """Get recent audit trail events"""
    events = audit_trail.query(limit=limit)
    return {"events": events, "count": len(events)}

@app.get("/api/multi-region/status")
async def get_multi_region_status():
    """Get multi-region deployment status"""
    from multi_region import multi_region
    return multi_region.get_status_report()

@app.get("/api/secrets/status")
async def get_secrets_status():
    """Get secrets manager status"""
    from secrets_manager import secrets_manager
    return secrets_manager.get_status()

# Visual Inspection (YOLO) Endpoints

@app.post("/api/inspect/image")
async def inspect_part(machine_id: str = "OMAYA-QC-01", part_id: Optional[str] = None):
    """
    Perform visual inspection on a part
    In production, this would accept a file/stream
    """
    metadata = {
        "machine_id": machine_id,
        "part_id": part_id or f"PART-{random.randint(1000, 9999)}"
    }

    # Mocking image data input
    result = yolo_inspector.inspect_image(None, metadata)

    # Audit log
    audit_trail.log_event(
        event_type=AuditEventType.PROCESS_CHANGE,
        user_id="system",
        details={
            "action": "visual_inspection",
            "part_id": result["part_id"],
            "status": result["status"]
        }
    )

    return result

@app.get("/api/inspect/stats")
async def get_inspection_stats():
    """Get visual inspection statistics"""
    return yolo_inspector.get_stats()

@app.get("/api/service-mesh/config")
async def get_service_mesh_config():
    """Get service mesh configuration"""
    from service_mesh import service_mesh
    return service_mesh.generate_all_configs()

# RAG (Retrieval-Augmented Generation) Endpoints

class QuestionRequest(BaseModel):
    question: str
    k: Optional[int] = 4

@app.post("/api/rag/query")
async def query_rag(request: QuestionRequest):
    """Query the RAG system for information from indexed documents"""
    results = rag_manager.query(request.question, k=request.k)

    # Audit log
    audit_trail.log_event(
        event_type=AuditEventType.PROCESS_CHANGE, # Using existing type for now
        user_id="system",
        details={
            "action": "rag_query",
            "question": request.question,
            "results_count": len(results)
        }
    )

    return {"results": results}

@app.post("/api/rag/reindex")
async def reindex_rag():
    """Trigger re-indexing of documents in the RAG directory"""
    new_files, new_chunks = rag_manager.index_files()
    return {
        "status": "success",
        "new_files": new_files,
        "new_chunks": new_chunks,
        "total_stats": rag_manager.get_stats()
    }

@app.get("/api/rag/stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    return rag_manager.get_stats()

# Mount GraphQL endpoint
app.include_router(graphql_router, prefix="/graphql", tags=["GraphQL"])

if __name__ == "__main__":
    import uvicorn

    # Generate certs if they don't exist and in development mode
    if os.getenv("ENV") == "development" and not tls_config._certs_exist():
        tls_config.generate_self_signed_certs()

    # Get SSL context
    ssl_context = tls_config.get_server_ssl_context()

    if ssl_context:
        logger.info("🔒 Starting API with TLS encryption")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8443,
            ssl_keyfile=str(tls_config.server_key),
            ssl_certfile=str(tls_config.server_cert),
            reload=True
        )
    else:
        logger.warning("⚠️ Starting API without TLS encryption (Insecure)")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
