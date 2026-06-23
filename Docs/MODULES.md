# Module Documentation

## Table of Contents

- [Frontend Modules](#frontend-modules)
- [Backend Modules](#backend-modules)
- [AI/ML Modules](#aiml-modules)
- [Monitoring Modules](#monitoring-modules)
- [Security Modules](#security-modules)

---

## Frontend Modules

### Overview

The frontend is built with React 18.2.0, TypeScript 5.8.2, and Vite 7.1.12. It uses a component-based architecture with Radix UI for UI components and TailwindCSS for styling.

### Core Components

#### Dashboard (`src/components/dashboard/Dashboard.tsx`)

**Purpose**: Main dashboard container with tab navigation and state management.

**Key Features**:
- Tab-based navigation (Overview, Machines, Telemetry, Predictive, Tools, Alerts, Maintenance, Explainability, GraphQL, Analytics, Audit, Multi-Region, Settings)
- Real-time data integration with 3-second refresh
- Machine selection and detail panel management
- Live/pause toggle for real-time updates

**Props**:
```typescript
interface DashboardProps {
  // No props - uses internal state management
}
```

**State Management**:
```typescript
const [activeTab, setActiveTab] = useState('overview');
const [selectedMachine, setSelectedMachine] = useState<OmayaMachine | null>(null);
const [isLoaded, setIsLoaded] = useState(false);
```

**Usage**:
```typescript
import { Dashboard } from './components/dashboard/Dashboard';

function App() {
  return <Dashboard />;
}
```

#### Sidebar (`src/components/dashboard/Sidebar.tsx`)

**Purpose**: Navigation sidebar with menu items and active tab highlighting.

**Key Features**:
- Collapsible sidebar
- Icon-based navigation
- Active tab highlighting
- Badge notifications for alerts

**Props**:
```typescript
interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}
```

**Navigation Items**:
- Overview (Dashboard icon)
- Machines (Server icon)
- Telemetry (Activity icon)
- Predictive (Brain icon)
- Tools (Wrench icon)
- Alerts (Bell icon)
- Maintenance (Calendar icon)
- Explainability (Lightbulb icon)
- GraphQL (Code icon)
- Analytics (BarChart icon)
- Audit (FileText icon)
- Multi-Region (Globe icon)
- Settings (Settings icon)

#### KPICards (`src/components/dashboard/KPICards.tsx`)

**Purpose**: Display Key Performance Indicators with real-time updates and animations.

**Key Features**:
- Animated value transitions
- Color-coded indicators (green/yellow/red)
- Trend indicators (up/down arrows)
- Responsive grid layout

**Props**:
```typescript
interface KPICardsProps {
  data: KPIData;
  isLive: boolean;
}

interface KPIData {
  oee: number;
  uptime: number;
  defect_rate: number;
  throughput: number;
  mtbf: number;
  mttr: number;
}
```

**KPI Metrics**:
- **OEE** (Overall Equipment Effectiveness): 0-100%
- **Uptime**: Percentage of operational time
- **Defect Rate**: Percentage of defective parts
- **Throughput**: Parts per hour
- **MTBF** (Mean Time Between Failures): Hours
- **MTTR** (Mean Time To Repair): Hours

#### FleetOverview (`src/components/dashboard/FleetOverview.tsx`)

**Purpose**: Grid/list view of all machines with status indicators and filtering.

**Key Features**:
- Grid and list view toggle
- Machine status color coding
- Real-time status updates
- Click to select machine
- Filter by zone and status

**Props**:
```typescript
interface FleetOverviewProps {
  machines: OmayaMachine[];
  onMachineSelect: (machine: OmayaMachine) => void;
  selectedMachineId?: string;
  updatedMachineIds: Set<string>;
  isLive: boolean;
  onToggleLive: () => void;
}
```

**Machine Status Colors**:
- Green: Operational
- Yellow: Warning
- Red: Critical/Error
- Gray: Offline/Maintenance

#### MachineDetailPanel (`src/components/dashboard/MachineDetailPanel.tsx`)

**Purpose**: Detailed machine information panel with historical data and trends.

**Key Features**:
- Real-time sensor data display
- Historical trend charts
- Maintenance schedule
- Alert history
- Performance metrics

**Props**:
```typescript
interface MachineDetailPanelProps {
  machine: OmayaMachine;
  onClose: () => void;
}
```

#### AlertsPanel (`src/components/dashboard/AlertsPanel.tsx`)

**Purpose**: Alert management center with filtering and escalation.

**Key Features**:
- Multi-severity filtering
- Alert acknowledgment
- Alert escalation
- Real-time alert updates
- Compact and full view modes

**Props**:
```typescript
interface AlertsPanelProps {
  alerts: Alert[];
  compact?: boolean;
  newAlertIds?: Set<string>;
  onEscalate?: (alert: Alert) => void;
}
```

**Alert Severity Levels**:
- **Info**: Informational messages
- **Warning**: Warning conditions
- **Error**: Error conditions
- **Critical**: Critical conditions requiring immediate attention

#### TelemetryFeed (`src/components/dashboard/TelemetryFeed.tsx`)

**Purpose**: Real-time telemetry event stream with auto-scroll and filtering.

**Key Features**:
- Real-time event streaming
- Auto-scroll to latest
- Filter by machine and sensor type
- Event highlighting
- Export functionality

**Props**:
```typescript
interface TelemetryFeedProps {
  events: TelemetryEvent[];
  maxItems?: number;
  isLive: boolean;
  onToggleLive?: () => void;
}
```

#### PredictiveMaintenancePanel (`src/components/dashboard/PredictiveMaintenancePanel.tsx`)

**Purpose**: AI-powered maintenance predictions with confidence intervals.

**Key Features**:
- Failure probability predictions
- Remaining Useful Life (RUL) estimation
- Confidence intervals
- Risk level indicators
- Recommended actions

**Props**:
```typescript
interface PredictiveMaintenancePanelProps {
  machines: OmayaMachine[];
  onMachineSelect: (machine: OmayaMachine) => void;
}
```

#### ToolWearTracker (`src/components/dashboard/ToolWearTracker.tsx`)

**Purpose**: Tool lifecycle tracking with predictive replacement scheduling.

**Key Features**:
- Tool wear percentage
- Predicted remaining tool life
- Replacement scheduling
- Tool performance history
- Cost tracking

**Props**:
```typescript
interface ToolWearTrackerProps {
  tools: Tool[];
}
```

#### MaintenanceCalendar (`src/components/dashboard/MaintenanceCalendar.tsx`)

**Purpose**: Maintenance scheduling calendar with drag-and-drop.

**Key Features**:
- Monthly/weekly/daily views
- Drag-and-drop scheduling
- Maintenance type color coding
- Resource assignment
- Conflict detection

**Props**:
```typescript
interface MaintenanceCalendarProps {
  events: MaintenanceEvent[];
}
```

### UI Components

#### Button (`src/components/ui/button.tsx`)

**Purpose**: Reusable button component with variants and sizes.

**Variants**: default, destructive, outline, secondary, ghost, link
**Sizes**: default, sm, lg, icon

```typescript
<Button variant="default" size="default">
  Click me
</Button>
```

#### Card (`src/components/ui/card.tsx`)

**Purpose**: Card container component for content grouping.

```typescript
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content</CardContent>
  <CardFooter>Footer</CardFooter>
</Card>
```

#### Dialog (`src/components/ui/dialog.tsx`)

**Purpose**: Modal dialog component for overlays.

```typescript
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    Content
  </DialogContent>
</Dialog>
```

### Custom Hooks

#### useRealTimeData (`src/hooks/useRealTimeData.ts`)

**Purpose**: Hook for real-time data fetching with auto-refresh.

**Parameters**:
```typescript
interface UseRealTimeDataParams {
  refreshInterval?: number; // Default: 3000ms
}
```

**Returns**:
```typescript
interface UseRealTimeDataReturn {
  machines: OmayaMachine[];
  alerts: Alert[];
  kpis: KPIData;
  telemetryEvents: TelemetryEvent[];
  isLive: boolean;
  newAlertIds: Set<string>;
  updatedMachineIds: Set<string>;
  toggleLive: () => void;
}
```

**Usage**:
```typescript
const {
  machines,
  alerts,
  kpis,
  isLive,
  toggleLive
} = useRealTimeData({ refreshInterval: 3000 });
```

#### useGraphQL (`src/hooks/useGraphQL.ts`)

**Purpose**: Hook for GraphQL queries and mutations.

**Parameters**:
```typescript
interface UseGraphQLParams {
  query: string;
  variables?: Record<string, any>;
}
```

**Returns**:
```typescript
interface UseGraphQLReturn {
  data: any;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}
```

---

## Backend Modules

### Overview

The backend is built with Python 3.11, FastAPI 0.109.0, and Uvicorn 0.27.0. It follows a modular architecture with separate modules for different functionalities.

### Core API Modules

#### main.py (`backend/main.py`)

**Purpose**: FastAPI application entry point with route definitions and middleware.

**Key Features**:
- CORS configuration
- JWT authentication middleware
- Rate limiting middleware
- WebSocket endpoint setup
- API route registration
- Prometheus metrics integration

**Configuration**:
```python
app = FastAPI(
    title="OMAYA Fleet Monitoring API",
    version="2.4.2",
    description="Enterprise-grade IoT/IIoT Platform API"
)
```

**Middleware**:
```python
app.add_middleware(CORSMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)
```

#### auth.py (`backend/auth.py`)

**Purpose**: JWT authentication and RBAC (Role-Based Access Control).

**Key Features**:
- JWT token generation and validation
- User authentication
- Role-based permissions
- Password hashing with bcrypt
- Token refresh mechanism

**Functions**:
```python
def create_access_token(data: dict) -> str
def verify_token(token: str) -> dict
def authenticate_user(username: str, password: str) -> User
def get_current_user(token: str) -> User
def check_permission(user: User, permission: str) -> bool
```

**User Roles**:
- **admin**: Full system access
- **operator**: Machine monitoring and control
- **viewer**: Read-only access
- **analyst**: Analytics and reporting access

#### websocket_manager.py (`backend/websocket_manager.py`)

**Purpose**: WebSocket connection management for real-time updates.

**Key Features**:
- Connection pooling
- Topic-based subscriptions
- Broadcast messaging
- Connection health monitoring
- Automatic reconnection

**Methods**:
```python
class WebSocketManager:
    async def connect(websocket: WebSocket, machine_id: str)
    async def disconnect(websocket: WebSocket, machine_id: str)
    async def broadcast(message: dict, topic: str)
    async def send_personal_message(message: dict, websocket: WebSocket)
    async def subscribe(websocket: WebSocket, topic: str)
    async def unsubscribe(websocket: WebSocket, topic: str)
```

#### rate_limiter.py (`backend/rate_limiter.py`)

**Purpose**: Redis-based rate limiting for API protection.

**Key Features**:
- Sliding window rate limiting
- Configurable limits per endpoint
- Redis-backed storage
- Distributed support
- Automatic cleanup

**Configuration**:
```python
RATE_LIMITS = {
    "public": {"requests": 100, "window": 60},
    "authenticated": {"requests": 1000, "window": 60},
    "websocket": {"connections": 10, "window": 60}
}
```

### AI/ML Modules

#### ai_models.py (`backend/ai_models.py`)

**Purpose**: TensorFlow LSTM and ensemble models for failure prediction.

**Key Features**:
- LSTM neural network for time-series prediction
- Ensemble models (Random Forest + Gradient Boosting)
- Model versioning and rollback
- Batch prediction support
- Model performance tracking

**LSTM Architecture**:
```python
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(sequence_length, n_features)),
    LSTM(32),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])
```

**Training**:
```python
def train_lstm_model(X_train, y_train, epochs=100, batch_size=32):
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)
    return model, history
```

**Prediction**:
```python
def predict_failure_probability(model, features):
    probability = model.predict(features)[0][0]
    confidence = calculate_confidence(model, features)
    return probability, confidence
```

#### drift_detection.py (`backend/drift_detection.py`)

**Purpose**: Model drift detection using Population Stability Index (PSI).

**Key Features**:
- PSI calculation for feature distributions
- Automatic drift detection
- Retraining triggers
- Drift reporting
- Historical drift tracking

**PSI Calculation**:
```python
def calculate_psi(expected, actual, buckets=10):
    expected_percents = calculate_percentiles(expected, buckets)
    actual_percents = calculate_percentiles(actual, buckets)
    psi = sum((expected_percents[i] - actual_percents[i]) * 
              np.log(expected_percents[i] / actual_percents[i]) 
              for i in range(buckets))
    return psi
```

**Drift Thresholds**:
- PSI < 0.1: No drift
- 0.1 ≤ PSI < 0.2: Moderate drift
- PSI ≥ 0.2: Significant drift (retrain required)

#### online_learning.py (`backend/online_learning.py`)

**Purpose**: Online anomaly detection with adaptive thresholds.

**Key Features**:
- Isolation Forest for anomaly detection
- Adaptive threshold adjustment
- Concept drift handling
- Real-time scoring
- Model updating

**Implementation**:
```python
from sklearn.ensemble import IsolationForest

class OnlineAnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination)
        self.threshold = None
        
    def fit(self, X):
        self.model.fit(X)
        scores = self.model.score_samples(X)
        self.threshold = np.percentile(scores, 5)
        
    def predict(self, X):
        scores = self.model.score_samples(X)
        anomalies = scores < self.threshold
        return anomalies
```

#### explainable_ai.py (`backend/explainable_ai.py`)

**Purpose**: SHAP and LIME analysis for model interpretability.

**Key Features**:
- SHAP value calculation
- LIME local explanations
- Feature importance ranking
- Visualization support
- Batch explanation generation

**SHAP Analysis**:
```python
import shap

def explain_prediction(model, instance, background_data):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(instance)
    
    explanation = {
        'feature_importance': explainer.feature_importances_,
        'shap_values': shap_values,
        'base_value': explainer.expected_value
    }
    return explanation
```

#### edge_computing.py (`backend/edge_computing.py`)

**Purpose**: ONNX model conversion for edge deployment.

**Key Features**:
- TensorFlow to ONNX conversion
- Model optimization
- Edge deployment packaging
- Model size reduction
- Inference speed improvement

**Conversion**:
```python
import tf2onnx
import onnx

def convert_to_onnx(tf_model, output_path):
    onnx_model, _ = tf2onnx.convert.from_keras(tf_model)
    onnx.save(onnx_model, output_path)
    return output_path
```

### Data Processing Modules

#### kafka_producer.py (`backend/kafka_producer.py`)

**Purpose**: Kafka event producer for telemetry data streaming.

**Key Features**:
- Async message publishing
- Message batching
- Error handling and retries
- Producer pooling
- Message acknowledgment

**Configuration**:
```python
KAFKA_PRODUCER_CONFIG = {
    'bootstrap_servers': 'kafka:9092',
    'acks': 'all',
    'retries': 3,
    'batch_size': 16384,
    'linger_ms': 10,
    'compression_type': 'gzip'
}
```

**Usage**:
```python
producer = KafkaProducer(**KAFKA_PRODUCER_CONFIG)

async def send_telemetry(data):
    await producer.send_and_wait(
        'telemetry',
        key=data['machine_id'].encode(),
        value=json.dumps(data).encode()
    )
```

#### kafka_consumer.py (`backend/kafka_consumer.py`)

**Purpose**: Kafka event consumer for data processing.

**Key Features**:
- Consumer group management
- Offset tracking
- Message deserialization
- Error handling
- Parallel processing

**Configuration**:
```python
KAFKA_CONSUMER_CONFIG = {
    'bootstrap_servers': 'kafka:9092',
    'group_id': 'omaya-processor',
    'auto_offset_reset': 'latest',
    'enable_auto_commit': True
}
```

#### redis_cache.py (`backend/redis_cache.py`)

**Purpose**: Redis cache operations for performance optimization.

**Key Features**:
- Get/Set operations with TTL
- Cache invalidation
- Batch operations
- Pub/Sub support
- Connection pooling

**Operations**:
```python
class RedisCache:
    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        self.client.setex(key, ttl, json.dumps(value))
    
    def delete(self, key: str):
        self.client.delete(key)
    
    def invalidate_pattern(self, pattern: str):
        keys = self.client.keys(pattern)
        if keys:
            self.client.delete(*keys)
```

### Enterprise Modules

#### graphql_layer.py (`backend/graphql_layer.py`)

**Purpose**: GraphQL API layer using Strawberry.

**Key Features**:
- Schema definition
- Query and mutation resolvers
- Type definitions
- Subscriptions support
- DataLoader integration

**Schema Example**:
```python
@strawberry.type
class Machine:
    id: str
    name: str
    zone: str
    status: str

@strawberry.type
class Query:
    @strawberry.field
    def machine(self, id: str) -> Machine:
        return get_machine(id)
    
    @strawberry.field
    def machines(self) -> List[Machine]:
        return get_all_machines()
```

#### data_lake.py (`backend/data_lake.py`)

**Purpose**: MinIO data lake operations for long-term storage.

**Key Features**:
- Object upload/download
- Bucket management
- Lifecycle policies
- Versioning support
- Presigned URLs

**Operations**:
```python
class DataLake:
    def upload_file(self, bucket: str, object_name: str, file_path: str):
        self.client.fput_object(bucket, object_name, file_path)
    
    def download_file(self, bucket: str, object_name: str, file_path: str):
        self.client.fget_object(bucket, object_name, file_path)
    
    def list_objects(self, bucket: str, prefix: str = ''):
        objects = self.client.list_objects(bucket, prefix=prefix)
        return [obj.object_name for obj in objects]
```

#### multi_region.py (`backend/multi_region.py`)

**Purpose**: Multi-region deployment logic and data synchronization.

**Key Features**:
- Region configuration
- Data replication
- Failover management
- Load balancing
- Health monitoring

**Configuration**:
```python
REGIONS = {
    'primary': 'eu-west-1',
    'secondary': ['us-east-1', 'ap-northeast-1', 'us-west-2']
}

REGION_CONFIG = {
    'eu-west-1': {'endpoint': 'api.eu.omaya.com', 'priority': 1},
    'us-east-1': {'endpoint': 'api.us.omaya.com', 'priority': 2},
    'ap-northeast-1': {'endpoint': 'api.asia.omaya.com', 'priority': 3},
    'us-west-2': {'endpoint': 'api.us-west.omaya.com', 'priority': 4}
}
```

#### audit_trails.py (`backend/audit_trails.py`)

**Purpose**: Audit trail logging for compliance and security.

**Key Features**:
- Event logging
- User action tracking
- Data change history
- SHA-256 integrity verification
- Compliance reporting

**Logging**:
```python
def log_audit_event(event: AuditEvent):
    event_data = {
        'timestamp': datetime.utcnow(),
        'user_id': event.user_id,
        'action': event.action,
        'resource': event.resource,
        'details': event.details,
        'ip_address': event.ip_address,
        'hash': calculate_sha256(event)
    }
    store_audit_log(event_data)
```

#### secrets_manager.py (`backend/secrets_manager.py`)

**Purpose**: Vault secrets management for secure credential storage.

**Key Features**:
- Secret storage
- Secret retrieval
- Secret rotation
- Access control
- Audit logging

**Operations**:
```python
class SecretsManager:
    def store_secret(self, path: str, secret: dict):
        self.client.write(path, secret)
    
    def get_secret(self, path: str) -> dict:
        secret = self.client.read(path)
        return secret['data'] if secret else None
    
    def rotate_secret(self, path: str):
        old_secret = self.get_secret(path)
        new_secret = generate_new_secret()
        self.store_secret(path, new_secret)
        return new_secret
```

### Monitoring Modules

#### prometheus_metrics.py (`backend/prometheus_metrics.py`)

**Purpose**: Prometheus metrics exporter for system observability.

**Key Features**:
- Counter metrics
- Gauge metrics
- Histogram metrics
- Summary metrics
- Custom labels

**Metrics**:
```python
from prometheus_client import Counter, Gauge, Histogram, Summary

# Counters
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
machine_failures_total = Counter('machine_failures_total', 'Total machine failures', ['machine_id'])

# Gauges
active_machines = Gauge('active_machines', 'Number of active machines')
system_temperature = Gauge('system_temperature', 'System temperature', ['machine_id'])

# Histograms
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint'])

# Summaries
prediction_confidence = Summary('prediction_confidence', 'Prediction confidence', ['model'])
```

---

## Monitoring Modules

### Prometheus

**Purpose**: Metrics collection and storage.

**Configuration File**: `backend/monitoring/prometheus.yml`

**Key Features**:
- Multi-target scraping
- Custom metrics collection
- Alert rule evaluation
- Data retention management
- Remote storage support

**Scrape Config**:
```yaml
scrape_configs:
  - job_name: 'omaya-api'
    static_configs:
      - targets: ['omaya-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana

**Purpose**: Visualization and dashboards.

**Configuration**: `backend/monitoring/grafana/provisioning/`

**Key Features**:
- Pre-built dashboards
- Custom panel types
- Alert visualization
- Data source management
- User authentication

**Dashboards**:
- Fleet Overview Dashboard
- Machine Performance Dashboard
- AI Model Performance Dashboard
- System Health Dashboard

### Alertmanager

**Purpose**: Alert routing and notification management.

**Configuration File**: `backend/monitoring/alertmanager.yml`

**Key Features**:
- Alert grouping
- Alert routing
- Notification channels (Email, Slack, PagerDuty)
- Alert inhibition
- Alert silencing

**Route Config**:
```yaml
route:
  receiver: 'default'
  group_by: ['alertname', 'machine_id']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
```

---

## Security Modules

### TLS Configuration

**Purpose**: TLS 1.3 encryption for secure communication.

**Configuration**: `backend/tls_config.py`

**Key Features**:
- Certificate management
- Cipher suite configuration
- Perfect Forward Secrecy
- HSTS support
- Certificate rotation

**Configuration**:
```python
TLS_CONFIG = {
    'certfile': '/path/to/cert.pem',
    'keyfile': '/path/to/key.pem',
    'cafile': '/path/to/ca.pem',
    'verify_mode': 'required',
    'protocol': 'TLSv1.3'
}
```

### Service Mesh

**Purpose**: Istio/Linkerd configuration for microservice communication.

**Configuration**: `backend/service_mesh.py`

**Key Features**:
- Service discovery
- Load balancing
- Circuit breaking
- Retry logic
- Timeout management

**Configuration**:
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: omaya-api
spec:
  hosts:
  - omaya-api
  http:
  - route:
    - destination:
        host: omaya-api
        subset: v1
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
