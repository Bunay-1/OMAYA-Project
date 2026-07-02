# API Reference

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
- [WebSocket API](#websocket-api)
- [GraphQL API](#graphql-api)
- [Rate Limiting](#rate-limiting)

---

## Overview

The OMAYA Platform provides a comprehensive REST API for machine monitoring, data collection, and system management. All endpoints follow RESTful principles and return JSON responses.

### API Features

- **RESTful Design**: Standard HTTP methods (GET, POST, PUT, DELETE)
- **JSON Responses**: All data in JSON format
- **Authentication**: JWT-based authentication
- **Rate Limiting**: Configurable rate limits per endpoint
- **Pagination**: Built-in pagination for list endpoints
- **Filtering**: Query parameter filtering
- **Sorting**: Configurable sorting options
- **Real-time Updates**: WebSocket support for live data

---

## Authentication

### JWT Authentication

Most endpoints require authentication using JSON Web Tokens (JWT).

#### Obtain Token

```http
POST /api/auth/login HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "username": "admin",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Use Token

```http
GET /api/machines HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Refresh Token

```http
POST /api/auth/refresh HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Base URL

### Development
```
http://localhost:8000
```

### Production
```
https://api.omaya-platform.com
```

---

## Response Format

### Success Response

```json
{
  "data": { ... },
  "meta": {
    "status": "success",
    "timestamp": "2024-06-19T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... },
    "timestamp": "2024-06-19T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

### Error Codes

| Code | Description |
|------|-------------|
| VALIDATION_ERROR | Input validation failed |
| AUTHENTICATION_ERROR | Authentication failed |
| AUTHORIZATION_ERROR | Insufficient permissions |
| NOT_FOUND_ERROR | Resource not found |
| CONFLICT_ERROR | Resource conflict |
| RATE_LIMIT_ERROR | Rate limit exceeded |
| INTERNAL_ERROR | Internal server error |

---

## Endpoints

### Health & Status

#### GET /

Get service information.

```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "service": "OMAYA Fleet Monitoring API",
  "version": "3.1.0",
  "status": "operational"
}
```

#### GET /health

Health check endpoint.

```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-06-19T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "kafka": "connected"
  }
}
```

#### GET /api/self-test

System self-test endpoint.

```http
GET /api/self-test HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
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

---

### Machine Management

#### GET /api/machines

List all machines with optional filtering and pagination.

```http
GET /api/machines?page=1&limit=20&zone=Zone%20A&status=operational HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)
- `zone` (optional): Filter by zone
- `status` (optional): Filter by status
- `sort` (optional): Sort field (default: id)
- `order` (optional): Sort order (asc/desc, default: asc)

**Response:**
```json
{
  "data": [
    {
      "id": "M001",
      "name": "OMAYA-5X #1",
      "zone": "Zone A",
      "status": "operational",
      "spindle_speed": 10500,
      "temperature": 42.5,
      "vibration": 1.2,
      "tool_wear": 35,
      "cycle_time": 120,
      "uptime": 95.5,
      "last_updated": "2024-06-19T10:30:00Z"
    }
  ],
  "meta": {
    "total": 120,
    "page": 1,
    "limit": 20,
    "pages": 6
  }
}
```

#### GET /api/machines/{id}

Get detailed information about a specific machine.

```http
GET /api/machines/M001 HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Response:**
```json
{
  "data": {
    "id": "M001",
    "name": "OMAYA-5X #1",
    "zone": "Zone A",
    "status": "operational",
    "specifications": {
      "manufacturer": "DMG Mori",
      "model": "DMU 50",
      "year": 2020,
      "spindle_max_rpm": 12000,
      "axis_count": 5
    },
    "current_state": {
      "spindle_speed": 10500,
      "temperature": 42.5,
      "vibration": 1.2,
      "tool_wear": 35,
      "cycle_time": 120,
      "uptime": 95.5
    },
    "sensors": [
      {
        "id": "S001",
        "type": "temperature",
        "location": "spindle_bearing",
        "status": "active"
      }
    ],
    "maintenance": {
      "last_maintenance": "2024-06-01T00:00:00Z",
      "next_maintenance": "2024-07-01T00:00:00Z",
      "maintenance_type": "preventive"
    }
  }
}
```

#### POST /api/machines

Create a new machine.

```http
POST /api/machines HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "OMAYA-5X #2",
  "zone": "Zone A",
  "manufacturer": "DMG Mori",
  "model": "DMU 50",
  "year": 2020,
  "specifications": {
    "spindle_max_rpm": 12000,
    "axis_count": 5
  }
}
```

**Response:**
```json
{
  "data": {
    "id": "M121",
    "name": "OMAYA-5X #2",
    "zone": "Zone A",
    "status": "offline",
    "created_at": "2024-06-19T10:30:00Z"
  }
}
```

#### PUT /api/machines/{id}

Update machine information.

```http
PUT /api/machines/M001 HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "OMAYA-5X #1 (Updated)",
  "zone": "Zone B"
}
```

**Response:**
```json
{
  "data": {
    "id": "M001",
    "name": "OMAYA-5X #1 (Updated)",
    "zone": "Zone B",
    "updated_at": "2024-06-19T10:30:00Z"
  }
}
```

#### DELETE /api/machines/{id}

Delete a machine.

```http
DELETE /api/machines/M001 HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Response:**
```json
{
  "data": {
    "id": "M001",
    "deleted": true,
    "deleted_at": "2024-06-19T10:30:00Z"
  }
}
```

#### POST /api/machines/{id}/status

Update machine status.

```http
POST /api/machines/M001/status HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "maintenance",
  "reason": "Scheduled preventive maintenance"
}
```

**Response:**
```json
{
  "data": {
    "id": "M001",
    "status": "maintenance",
    "reason": "Scheduled preventive maintenance",
    "updated_at": "2024-06-19T10:30:00Z"
  }
}
```

---

### Telemetry Data

#### GET /api/telemetry

Get telemetry data with filtering.

```http
GET /api/telemetry?machine_id=M001&sensor_type=temperature&start=2024-06-19T00:00:00Z&end=2024-06-19T23:59:59Z HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Query Parameters:**
- `machine_id` (optional): Filter by machine ID
- `sensor_type` (optional): Filter by sensor type
- `start` (optional): Start timestamp (ISO 8601)
- `end` (optional): End timestamp (ISO 8601)
- `limit` (optional): Maximum number of records (default: 1000)

**Response:**
```json
{
  "data": [
    {
      "id": "T001",
      "machine_id": "M001",
      "sensor_id": "S001",
      "sensor_type": "temperature",
      "value": 42.5,
      "unit": "°C",
      "timestamp": "2024-06-19T10:30:00Z",
      "quality": "good"
    }
  ],
  "meta": {
    "total": 1000,
    "limit": 1000
  }
}
```

#### POST /api/telemetry

Submit telemetry data (for external data sources).

```http
POST /api/telemetry HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "machine_id": "M001",
  "sensor_type": "temperature",
  "value": 42.5,
  "unit": "°C",
  "timestamp": "2024-06-19T10:30:00Z"
}
```

**Response:**
```json
{
  "data": {
    "id": "T001",
    "status": "accepted",
    "timestamp": "2024-06-19T10:30:00Z"
  }
}
```

---

### Alerts

#### GET /api/alerts

List alerts with filtering.

```http
GET /api/alerts?severity=critical&machine_id=M001&status=active HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Query Parameters:**
- `severity` (optional): Filter by severity (info, warning, error, critical)
- `machine_id` (optional): Filter by machine ID
- `status` (optional): Filter by status (active, acknowledged, resolved)
- `start` (optional): Start timestamp
- `end` (optional): End timestamp
- `page` (optional): Page number
- `limit` (optional): Items per page

**Response:**
```json
{
  "data": [
    {
      "id": "A001",
      "machine_id": "M001",
      "machine_name": "OMAYA-5X #1",
      "severity": "critical",
      "type": "overheating",
      "title": "Critical: OMAYA-5X #1 requires immediate attention",
      "message": "Temperature exceeding safe limits. Immediate shutdown recommended.",
      "timestamp": "2024-06-19T10:30:00Z",
      "acknowledged": false,
      "acknowledged_by": null,
      "acknowledged_at": null,
      "resolved": false,
      "resolved_at": null
    }
  ],
  "meta": {
    "total": 5,
    "page": 1,
    "limit": 20
  }
}
```

#### POST /api/alerts

Create a new alert.

```http
POST /api/alerts HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "machine_id": "M001",
  "severity": "warning",
  "type": "vibration",
  "title": "Elevated vibration detected",
  "message": "Vibration levels indicate potential bearing wear"
}
```

**Response:**
```json
{
  "data": {
    "id": "A006",
    "status": "created",
    "timestamp": "2024-06-19T10:30:00Z"
  }
}
```

#### PUT /api/alerts/{id}

Update alert status.

```http
PUT /api/alerts/A001 HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "acknowledged",
  "notes": "Investigating the issue"
}
```

**Response:**
```json
{
  "data": {
    "id": "A001",
    "status": "acknowledged",
    "acknowledged_by": "admin",
    "acknowledged_at": "2024-06-19T10:30:00Z",
    "notes": "Investigating the issue"
  }
}
```

#### POST /api/alerts/{id}/escalate

Escalate an alert.

```http
POST /api/alerts/A001/escalate HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "escalation_level": 2,
  "reason": "Requires immediate attention",
  "assigned_to": "supervisor"
}
```

**Response:**
```json
{
  "data": {
    "id": "A001",
    "escalation_level": 2,
    "assigned_to": "supervisor",
    "escalated_at": "2024-06-19T10:30:00Z"
  }
}
```

---

### AI Predictions

#### POST /api/predict/failure

Predict machine failure probability.

```http
POST /api/predict/failure HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "machine_id": "M001",
  "features": {
    "temperature": 68.5,
    "vibration": 2.1,
    "tool_wear": 75,
    "operating_hours": 3200
  }
}
```

**Response:**
```json
{
  "data": {
    "machine_id": "M001",
    "failure_probability": 0.78,
    "confidence": 0.92,
    "estimated_time_to_failure": 48,
    "risk_level": "high",
    "recommended_action": "Schedule maintenance within 48 hours",
    "model_version": "v3.2",
    "timestamp": "2024-06-19T10:30:00Z"
  }
}
```

#### GET /api/predict/rul/{machine_id}

Get Remaining Useful Life (RUL) prediction.

```http
GET /api/predict/rul/M001 HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Response:**
```json
{
  "data": {
    "machine_id": "M001",
    "rul_hours": 245,
    "confidence_interval": {
      "lower": 200,
      "upper": 290
    },
    "confidence": 0.89,
    "model_version": "v3.2",
    "last_updated": "2024-06-19T10:30:00Z"
  }
}
```

#### GET /api/predict/batch

Get predictions for multiple machines.

```http
GET /api/predict/batch?machine_ids=M001,M002,M003 HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Response:**
```json
{
  "data": [
    {
      "machine_id": "M001",
      "failure_probability": 0.78,
      "rul_hours": 245
    },
    {
      "machine_id": "M002",
      "failure_probability": 0.12,
      "rul_hours": 890
    },
    {
      "machine_id": "M003",
      "failure_probability": 0.45,
      "rul_hours": 410
    }
  ]
}
```

---

### Maintenance

#### GET /api/maintenance

List maintenance events.

```http
GET /api/maintenance?machine_id=M001&type=preventive&status=scheduled HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Query Parameters:**
- `machine_id` (optional): Filter by machine ID
- `type` (optional): Filter by type (preventive, corrective, predictive)
- `status` (optional): Filter by status (scheduled, in_progress, completed)
- `start` (optional): Start date
- `end` (optional): End date

**Response:**
```json
{
  "data": [
    {
      "id": "MAINT001",
      "machine_id": "M001",
      "type": "preventive",
      "status": "scheduled",
      "scheduled_date": "2024-07-01T00:00:00Z",
      "estimated_duration": 4,
      "description": "Regular preventive maintenance",
      "assigned_to": "tech_team_a"
    }
  ]
}
```

#### POST /api/maintenance

Schedule maintenance.

```http
POST /api/maintenance HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "machine_id": "M001",
  "type": "preventive",
  "scheduled_date": "2024-07-01T00:00:00Z",
  "estimated_duration": 4,
  "description": "Regular preventive maintenance",
  "assigned_to": "tech_team_a"
}
```

**Response:**
```json
{
  "data": {
    "id": "MAINT002",
    "status": "scheduled",
    "created_at": "2024-06-19T10:30:00Z"
  }
}
```

#### PUT /api/maintenance/{id}

Update maintenance event.

```http
PUT /api/maintenance/MAINT001 HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "in_progress",
  "notes": "Started maintenance procedure"
}
```

**Response:**
```json
{
  "data": {
    "id": "MAINT001",
    "status": "in_progress",
    "updated_at": "2024-06-19T10:30:00Z"
  }
}
```

---

### KPIs

#### GET /api/kpis

Get Key Performance Indicators.

```http
GET /api/kpis?machine_id=M001&start=2024-06-19T00:00:00Z&end=2024-06-19T23:59:59Z HTTP/1.1
Host: localhost:8000
Authorization: Bearer {token}
```

**Query Parameters:**
- `machine_id` (optional): Filter by machine ID
- `zone` (optional): Filter by zone
- `start` (optional): Start timestamp
- `end` (optional): End timestamp

**Response:**
```json
{
  "data": {
    "oee": 87.5,
    "uptime": 95.5,
    "defect_rate": 2.3,
    "throughput": 450,
    "mtbf": 120,
    "mttr": 4.5,
    "period": {
      "start": "2024-06-19T00:00:00Z",
      "end": "2024-06-19T23:59:59Z"
    }
  }
}
```

---

## WebSocket API

### Connection

Connect to the WebSocket endpoint for real-time updates.

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('WebSocket connected');
  
  // Subscribe to machine updates
  ws.send(JSON.stringify({
    action: 'subscribe',
    topic: 'machines',
    machine_id: 'M001'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

### Subscription Topics

- `machines`: Machine status updates
- `telemetry`: Real-time sensor data
- `alerts`: New alerts
- `predictions`: AI prediction updates

### Message Format

#### Subscribe

```json
{
  "action": "subscribe",
  "topic": "machines",
  "machine_id": "M001"
}
```

#### Unsubscribe

```json
{
  "action": "unsubscribe",
  "topic": "machines",
  "machine_id": "M001"
}
```

#### Data Update

```json
{
  "topic": "machines",
  "machine_id": "M001",
  "data": {
    "temperature": 42.5,
    "vibration": 1.2,
    "status": "operational"
  },
  "timestamp": "2024-06-19T10:30:00Z"
}
```

---

## GraphQL API

### Endpoint

```
http://localhost:8000/graphql
```

### Query Example

```graphql
query GetMachine($id: ID!) {
  machine(id: $id) {
    id
    name
    zone
    status
    current_state {
      temperature
      vibration
      spindle_speed
    }
    sensors {
      id
      type
      location
    }
  }
}
```

### Variables

```json
{
  "id": "M001"
}
```

### Response

```json
{
  "data": {
    "machine": {
      "id": "M001",
      "name": "OMAYA-5X #1",
      "zone": "Zone A",
      "status": "operational",
      "current_state": {
        "temperature": 42.5,
        "vibration": 1.2,
        "spindle_speed": 10500
      },
      "sensors": [
        {
          "id": "S001",
          "type": "temperature",
          "location": "spindle_bearing"
        }
      ]
    }
  }
}
```

---

## Rate Limiting

### Rate Limits

| Endpoint | Rate Limit |
|----------|------------|
| Public endpoints | 100 requests/minute |
| Authenticated endpoints | 1000 requests/minute |
| WebSocket connections | 10 connections/user |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1718791200
```

### Rate Limit Exceeded

```json
{
  "error": {
    "code": "RATE_LIMIT_ERROR",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "reset": 1718791200
    }
  }
}
```

---

## Interactive API Documentation

The platform provides interactive API documentation powered by Swagger/OpenAPI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all available endpoints
- Test API calls directly from the browser
- View request/response schemas
- Download API specifications

---

## Support

For additional help:
- Documentation: [https://docs.omaya-platform.com](https://docs.omaya-platform.com)
- Issues: [https://github.com/Bunay-1/OMAYA-Project/issues](https://github.com/Bunay-1/OMAYA-Project/issues)
- Email: api-support@omaya-platform.com

---

**Version**: 3.1.0
**Last Updated**: June 2026
