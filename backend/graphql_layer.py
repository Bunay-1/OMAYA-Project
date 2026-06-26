"""
GraphQL API Layer
Flexible data queries with Strawberry GraphQL
"""
import os
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Types
@strawberry.type
class MachineType:
    id: str
    name: str
    status: str
    zone: str
    temperature: float
    vibration: float
    spindle_speed: float
    tool_wear: float
    operating_hours: float
    last_updated: str

@strawberry.type
class AlertType:
    id: str
    machine_id: str
    severity: str
    title: str
    message: str
    timestamp: str
    acknowledged: bool

@strawberry.type
class PredictionType:
    machine_id: str
    failure_probability: float
    rul_hours: float
    rul_days: float
    confidence: float
    model_version: str
    factors: List[str]

@strawberry.type
class TelemetryType:
    machine_id: str
    temperature: float
    vibration: float
    spindle_speed: float
    timestamp: str

@strawberry.type
class MaintenanceType:
    id: str
    machine_id: str
    scheduled_date: str
    maintenance_type: str
    priority: str
    estimated_duration: float
    status: str

@strawberry.type
class KPIType:
    oee: float
    uptime: float
    defect_rate: float
    machines_running: int
    machines_idle: int
    machines_error: int

@strawberry.type
class DriftStatusType:
    has_drift: bool
    accuracy_drift: bool
    feature_drift: bool
    current_accuracy: float
    recommendation: str

# Input Types
@strawberry.input
class MachineFilterInput:
    status: Optional[str] = None
    zone: Optional[str] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None

@strawberry.input
class AlertFilterInput:
    severity: Optional[str] = None
    machine_id: Optional[str] = None
    acknowledged: Optional[bool] = None

@strawberry.input
class PredictionInput:
    machine_id: str
    temperature: float
    vibration: float
    spindle_speed: float
    tool_wear: float
    operating_hours: float

# Mock data generators
def generate_mock_machines(filter_input: Optional[MachineFilterInput] = None) -> List[MachineType]:
    """Generate mock machine data"""
    import random
    
    statuses = ["running", "idle", "warning", "error", "maintenance"]
    zones = ["Zone A", "Zone B", "Zone C", "Zone D"]
    
    machines = []
    for i in range(120):
        status = random.choice(statuses)
        
        if filter_input:
            if filter_input.status and status != filter_input.status:
                continue
            if filter_input.zone and zones[i % len(zones)] != filter_input.zone:
                continue
        
        temp = 50 + random.random() * 30
        if filter_input:
            if filter_input.min_temperature and temp < filter_input.min_temperature:
                continue
            if filter_input.max_temperature and temp > filter_input.max_temperature:
                continue
        
        machines.append(MachineType(
            id=f"OMAYA-{i+1:03d}",
            name=f"OMAYA Machine {i+1}",
            status=status,
            zone=zones[i % len(zones)],
            temperature=round(temp, 1),
            vibration=round(1.0 + random.random() * 2, 2),
            spindle_speed=round(8000 + random.random() * 4000, 0),
            tool_wear=round(random.random() * 100, 1),
            operating_hours=round(random.random() * 5000, 1),
            last_updated=datetime.now().isoformat()
        ))
    
    return machines

def generate_mock_alerts(filter_input: Optional[AlertFilterInput] = None) -> List[AlertType]:
    """Generate mock alert data"""
    import random
    
    severities = ["critical", "error", "warning", "info"]
    titles = ["High Temperature", "Vibration Anomaly", "Tool Wear Alert", "Maintenance Due"]
    
    alerts = []
    for i in range(50):
        severity = random.choice(severities)
        machine_id = f"OMAYA-{random.randint(1, 120):03d}"
        acknowledged = random.random() > 0.7
        
        if filter_input:
            if filter_input.severity and severity != filter_input.severity:
                continue
            if filter_input.machine_id and machine_id != filter_input.machine_id:
                continue
            if filter_input.acknowledged is not None and acknowledged != filter_input.acknowledged:
                continue
        
        alerts.append(AlertType(
            id=f"ALERT-{i+1:05d}",
            machine_id=machine_id,
            severity=severity,
            title=random.choice(titles),
            message=f"Alert generated for machine {machine_id}",
            timestamp=datetime.now().isoformat(),
            acknowledged=acknowledged
        ))
    
    return alerts

# Queries
@strawberry.type
class Query:
    @strawberry.field
    def machines(self, filter: Optional[MachineFilterInput] = None, 
                 limit: int = 100, offset: int = 0) -> List[MachineType]:
        """Get all machines with optional filtering"""
        all_machines = generate_mock_machines(filter)
        return all_machines[offset:offset + limit]
    
    @strawberry.field
    def machine(self, id: str) -> Optional[MachineType]:
        """Get single machine by ID"""
        machines = generate_mock_machines()
        for m in machines:
            if m.id == id:
                return m
        return None
    
    @strawberry.field
    def alerts(self, filter: Optional[AlertFilterInput] = None,
               limit: int = 50, offset: int = 0) -> List[AlertType]:
        """Get alerts with optional filtering"""
        all_alerts = generate_mock_alerts(filter)
        return all_alerts[offset:offset + limit]
    
    @strawberry.field
    def alert(self, id: str) -> Optional[AlertType]:
        """Get single alert by ID"""
        alerts = generate_mock_alerts()
        for a in alerts:
            if a.id == id:
                return a
        return None
    
    @strawberry.field
    def prediction(self, machine_id: str) -> PredictionType:
        """Get AI prediction for a machine"""
        import random
        
        failure_prob = random.random() * 0.5
        rul_hours = 100 + random.random() * 900
        
        return PredictionType(
            machine_id=machine_id,
            failure_probability=round(failure_prob, 3),
            rul_hours=round(rul_hours, 1),
            rul_days=round(rul_hours / 24, 1),
            confidence=round(0.7 + random.random() * 0.25, 3),
            model_version="LSTM-TF-v1.0",
            factors=["Temperature", "Vibration", "Tool Wear"]
        )
    
    @strawberry.field
    def kpis(self) -> KPIType:
        """Get current KPIs"""
        import random
        return KPIType(
            oee=round(85 + random.random() * 10, 1),
            uptime=round(90 + random.random() * 8, 1),
            defect_rate=round(0.5 + random.random() * 2, 2),
            machines_running=random.randint(80, 100),
            machines_idle=random.randint(10, 25),
            machines_error=random.randint(2, 8)
        )
    
    @strawberry.field
    def drift_status(self) -> DriftStatusType:
        """Get model drift status"""
        return DriftStatusType(
            has_drift=False,
            accuracy_drift=False,
            feature_drift=False,
            current_accuracy=0.92,
            recommendation="No drift detected. Model performing normally."
        )

# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def acknowledge_alert(self, alert_id: str) -> AlertType:
        """Acknowledge an alert"""
        return AlertType(
            id=alert_id,
            machine_id="OMAYA-001",
            severity="warning",
            title="Acknowledged Alert",
            message="Alert has been acknowledged",
            timestamp=datetime.now().isoformat(),
            acknowledged=True
        )
    
    @strawberry.mutation
    def schedule_maintenance(self, machine_id: str, 
                            scheduled_date: str,
                            maintenance_type: str) -> MaintenanceType:
        """Schedule maintenance for a machine"""
        import random
        return MaintenanceType(
            id=f"MAINT-{random.randint(10000, 99999)}",
            machine_id=machine_id,
            scheduled_date=scheduled_date,
            maintenance_type=maintenance_type,
            priority="normal",
            estimated_duration=4.0,
            status="scheduled"
        )
    
    @strawberry.mutation
    def request_prediction(self, input: PredictionInput) -> PredictionType:
        """Request new AI prediction"""
        import random
        
        # Calculate risk based on inputs
        risk = 0.0
        risk += min((input.temperature - 40) / 40, 1.0) * 0.3
        risk += min(input.vibration / 3.0, 1.0) * 0.25
        risk += min(input.tool_wear / 100, 1.0) * 0.35
        risk += min(input.operating_hours / 5000, 1.0) * 0.1
        risk = max(0, min(1, risk + random.uniform(-0.05, 0.05)))
        
        rul_hours = 1000 * (1 - risk)
        
        return PredictionType(
            machine_id=input.machine_id,
            failure_probability=round(risk, 3),
            rul_hours=round(rul_hours, 1),
            rul_days=round(rul_hours / 24, 1),
            confidence=round(0.85 + random.random() * 0.1, 3),
            model_version="LSTM-TF-v1.0",
            factors=["Temperature", "Vibration", "Tool Wear", "Operating Hours"]
        )

# Subscriptions (for real-time updates)
@strawberry.type
class Subscription:
    @strawberry.subscription
    async def telemetry_stream(self, machine_id: str) -> TelemetryType:
        """Stream real-time telemetry data"""
        import asyncio
        import random
        
        while True:
            yield TelemetryType(
                machine_id=machine_id,
                temperature=round(55 + random.random() * 20, 1),
                vibration=round(1.0 + random.random() * 2, 2),
                spindle_speed=round(9000 + random.random() * 2000, 0),
                timestamp=datetime.now().isoformat()
            )
            await asyncio.sleep(3)

# Create schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

# Create GraphQL router
# Disable introspection and tool in production
IS_PROD = os.getenv("ENV") == "production"

graphql_router = GraphQLRouter(
    schema,
    graphql_ide="graphiql" if not IS_PROD else None,
    allow_queries_via_get=not IS_PROD
)
