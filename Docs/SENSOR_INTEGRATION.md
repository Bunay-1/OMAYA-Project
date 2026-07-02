# Sensor Integration Guide

## Table of Contents

- [Overview](#overview)
- [Supported Sensor Types](#supported-sensor-types)
- [Communication Protocols](#communication-protocols)
- [PLC Integration](#plc-integration)
- [Hardware Setup](#hardware-setup)
- [Configuration](#configuration)
- [Data Collection](#data-collection)
- [Calibration](#calibration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

The OMAYA Platform supports integration with various industrial sensors and data collection devices. This guide covers the complete process of connecting sensors to the platform, from hardware setup to data ingestion.

### Sensor Architecture

```
Sensors → Data Acquisition → Edge Gateway → Kafka → OMAYA Platform
```

### Key Components

- **Sensors**: Physical devices measuring machine parameters
- **Data Acquisition**: Hardware/software collecting sensor data
- **Edge Gateway**: Processing and transmitting data
- **Kafka**: Message broker for data streaming
- **OMAYA Platform**: Data processing and visualization

---

## Supported Sensor Types

### Temperature Sensors

#### PT100/PT1000 Resistance Temperature Detectors (RTDs)

- **Range**: -200°C to +850°C
- **Accuracy**: ±0.1°C to ±0.3°C
- **Applications**: Motor windings, bearings, hydraulic systems
- **Wiring**: 2-wire, 3-wire, or 4-wire configurations

#### Thermocouples

- **Types**: J, K, T, E, N, B, R, S
- **Range**: -200°C to +2300°C (depending on type)
- **Accuracy**: ±0.5°C to ±2°C
- **Applications**: High-temperature environments, furnaces

#### Infrared Temperature Sensors

- **Range**: -50°C to +3000°C
- **Accuracy**: ±1% of reading
- **Applications**: Non-contact temperature measurement

### Vibration Sensors

#### Accelerometers

- **Types**: Piezoelectric, MEMS
- **Range**: 0.1 Hz to 20 kHz
- **Sensitivity**: 10 mV/g to 1000 mV/g
- **Applications**: Bearing monitoring, imbalance detection

#### Velocity Sensors

- **Range**: 10 Hz to 2 kHz
- **Sensitivity**: 20 mV/mm/s to 500 mV/mm/s
- **Applications**: General vibration monitoring

#### Displacement Sensors

- **Range**: 0 to 25 mm
- **Resolution**: 0.001 mm
- **Applications**: Shaft alignment, position monitoring

### Pressure Sensors

#### Industrial Pressure Transducers

- **Range**: 0 to 10,000 psi
- **Accuracy**: ±0.1% to ±0.5% FS
- **Output**: 4-20 mA, 0-10 V, digital
- **Applications**: Hydraulic systems, pneumatic systems

### Flow Sensors

#### Flow Meters

- **Types**: Turbine, magnetic, ultrasonic, Coriolis
- **Range**: 0.1 to 10,000 L/min
- **Accuracy**: ±0.1% to ±0.5%
- **Applications**: Coolant flow, lubrication systems

### Position Sensors

#### Encoders

- **Types**: Incremental, absolute
- **Resolution**: Up to 20 bits
- **Applications**: Motor position, spindle speed

#### Linear Scales

- **Resolution**: 0.001 mm to 0.0001 mm
- **Applications**: Axis positioning, tool positioning

### Electrical Sensors

#### Current Sensors

- **Range**: 0 to 1000 A
- **Accuracy**: ±0.5%
- **Applications**: Motor current monitoring

#### Voltage Sensors

- **Range**: 0 to 1000 V
- **Accuracy**: ±0.5%
- **Applications**: Power supply monitoring

---

## Communication Protocols

### Modbus TCP/IP

#### Overview

Modbus TCP/IP is the most widely used protocol in industrial automation. It's simple, reliable, and supported by most industrial devices.

#### Configuration

```python
# Modbus TCP configuration example
MODBUS_CONFIG = {
    'host': '192.168.1.100',
    'port': 502,
    'unit_id': 1,
    'timeout': 5
}
```

#### Register Mapping

```python
# Example register mapping
REGISTER_MAP = {
    'temperature': {'address': 40001, 'count': 2, 'scale': 0.1},
    'vibration': {'address': 40003, 'count': 2, 'scale': 0.01},
    'pressure': {'address': 40005, 'count': 1, 'scale': 1.0},
    'flow_rate': {'address': 40006, 'count': 1, 'scale': 0.1}
}
```

#### Implementation

```python
from pymodbus.client import ModbusTcpClient

def read_modbus_data(config, register_map):
    client = ModbusTcpClient(
        host=config['host'],
        port=config['port'],
        timeout=config['timeout']
    )
    
    try:
        client.connect()
        data = {}
        
        for sensor, mapping in register_map.items():
            result = client.read_holding_registers(
                address=mapping['address'] - 1,  # Modbus is 0-based
                count=mapping['count'],
                unit=config['unit_id']
            )
            
            if not result.isError():
                raw_value = result.registers[0]
                data[sensor] = raw_value * mapping['scale']
        
        return data
    finally:
        client.close()
```

### OPC UA

#### Overview

OPC UA is a modern, secure industrial communication protocol with built-in security and data modeling capabilities.

#### Configuration

```python
OPC_UA_CONFIG = {
    'url': 'opc.tcp://192.168.1.100:4840',
    'security': 'None',  # or 'Sign', 'SignAndEncrypt'
    'username': 'user',
    'password': 'password'
}
```

#### Node IDs

```python
OPC_UA_NODES = {
    'temperature': 'ns=2;s=Machine1.Temperature',
    'vibration': 'ns=2;s=Machine1.Vibration',
    'pressure': 'ns=2;s=Machine1.Pressure',
    'flow_rate': 'ns=2;s=Machine1.FlowRate'
}
```

#### Implementation

```python
from opcua import Client

def read_opc_ua_data(config, node_ids):
    client = Client(url=config['url'])
    
    try:
        client.connect()
        data = {}
        
        for sensor, node_id in node_ids.items():
            node = client.get_node(node_id)
            value = node.get_value()
            data[sensor] = value
        
        return data
    finally:
        client.disconnect()
```

### MQTT

#### Overview

MQTT is a lightweight publish/subscribe messaging protocol ideal for IoT applications.

#### Configuration

```python
MQTT_CONFIG = {
    'broker': '192.168.1.100',
    'port': 1883,
    'username': 'sensor_user',
    'password': 'sensor_password',
    'topic_prefix': 'omaya/sensors'
}
```

#### Topic Structure

```
omaya/sensors/{machine_id}/{sensor_type}/{sensor_id}
```

#### Implementation

```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode()
    
    # Parse topic: omaya/sensors/M001/temperature/S001
    parts = topic.split('/')
    machine_id = parts[2]
    sensor_type = parts[3]
    sensor_id = parts[4]
    
    # Process data
    process_sensor_data(machine_id, sensor_type, sensor_id, payload)

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'])
client.subscribe(f"{MQTT_CONFIG['topic_prefix']}/#")
client.loop_forever()
```

### HTTP/REST API

#### Overview

Modern sensors often provide REST APIs for data access.

---

## PLC Integration

### Siemens S7 Protocol

#### Overview
Direct connection to Siemens S7-1200, S7-1500, S7-300, and S7-400 PLCs using the S7 communication protocol.

#### Configuration
```python
S7_CONFIG = {
    'ip': '192.168.1.10',
    'rack': 0,
    'slot': 1,
    'db_number': 10,
    'start_offset': 0,
    'size': 100
}
```

### Fanuc FOCAS

#### Overview
Deep integration with Fanuc OMAYA controllers for retrieving machine state, tool wear, and execution data.

#### Key Data Points
- Tool Life Management data
- Spindle load and temperature
- Part count and cycle time
- Alarm history and current status

### Heidenhain LSV2

#### Overview
Communication with Heidenhain TNC controllers for high-precision monitoring of axis positions and spindle parameters.

#### Configuration

```python
HTTP_CONFIG = {
    'base_url': 'http://192.168.1.100/api',
    'api_key': 'your-api-key',
    'timeout': 10
}
```

#### Implementation

```python
import requests

def read_http_data(config, endpoints):
    headers = {
        'Authorization': f"Bearer {config['api_key']}",
        'Content-Type': 'application/json'
    }
    
    data = {}
    for sensor, endpoint in endpoints.items():
        url = f"{config['base_url']}/{endpoint}"
        response = requests.get(url, headers=headers, timeout=config['timeout'])
        
        if response.status_code == 200:
            data[sensor] = response.json()
    
    return data
```

---

## Hardware Setup

### Wiring Guidelines

#### Signal Wiring

- Use shielded twisted-pair cables for analog signals
- Keep signal wires away from power cables
- Use proper grounding techniques
- Follow manufacturer's wiring diagrams

#### Power Supply

- Use regulated power supplies
- Ensure proper voltage and current ratings
- Include surge protection
- Use UPS for critical sensors

#### Network Wiring

- Use industrial-grade Ethernet cables (Cat6a or higher)
- Use IP67 rated connectors for harsh environments
- Implement network redundancy for critical systems
- Use managed switches with VLAN support

### Installation Steps

#### 1. Sensor Mounting

- Mount sensors according to manufacturer specifications
- Ensure proper mechanical coupling
- Use appropriate mounting hardware
- Consider environmental protection

#### 2. Cable Routing

- Route cables away from heat sources
- Use cable trays or conduits
- Label all cables at both ends
- Maintain minimum bend radius

#### 3. Connection

- Terminate connections according to standards
- Use proper crimping tools
- Test continuity before energizing
- Document all connections

#### 4. Grounding

- Establish proper ground reference
- Connect sensor grounds to system ground
- Avoid ground loops
- Test ground resistance

---

## Configuration

### Sensor Registration

#### Add Sensor to Database

```python
from backend.database import SessionLocal, Sensor

def register_sensor(sensor_data):
    db = SessionLocal()
    try:
        sensor = Sensor(
            machine_id=sensor_data['machine_id'],
            sensor_type=sensor_data['sensor_type'],
            model=sensor_data['model'],
            manufacturer=sensor_data['manufacturer'],
            serial_number=sensor_data['serial_number'],
            protocol=sensor_data['protocol'],
            connection_params=sensor_data['connection_params'],
            calibration_params=sensor_data['calibration_params']
        )
        db.add(sensor)
        db.commit()
        return sensor.id
    finally:
        db.close()
```

#### Sensor Configuration Example

```json
{
    "machine_id": "M001",
    "sensor_type": "temperature",
    "model": "PT100-RTD",
    "manufacturer": "Siemens",
    "serial_number": "SN123456",
    "protocol": "modbus_tcp",
    "connection_params": {
        "host": "192.168.1.100",
        "port": 502,
        "unit_id": 1,
        "register_address": 40001,
        "register_count": 2,
        "scale_factor": 0.1
    },
    "calibration_params": {
        "offset": 0.0,
        "gain": 1.0,
        "calibration_date": "2024-01-15"
    }
}
```

### Data Collection Configuration

#### Sampling Rate Configuration

```python
SAMPLING_CONFIG = {
    'temperature': {'interval': 1000, 'unit': 'ms'},  # 1 second
    'vibration': {'interval': 100, 'unit': 'ms'},     # 100 ms
    'pressure': {'interval': 500, 'unit': 'ms'},       # 500 ms
    'flow_rate': {'interval': 1000, 'unit': 'ms'}       # 1 second
}
```

#### Data Quality Checks

```python
def validate_sensor_data(sensor_type, value):
    """Validate sensor data against expected ranges"""
    RANGES = {
        'temperature': (-50, 300),      # °C
        'vibration': (0, 100),          # mm/s
        'pressure': (0, 10000),         # psi
        'flow_rate': (0, 10000)         # L/min
    }
    
    min_val, max_val = RANGES.get(sensor_type, (None, None))
    
    if min_val is not None and value < min_val:
        return False, f"Value {value} below minimum {min_val}"
    
    if max_val is not None and value > max_val:
        return False, f"Value {value} above maximum {max_val}"
    
    return True, "Valid"
```

---

## Edge Resilience & Synchronization

### Store-and-Forward Mechanism

To ensure zero data loss during network outages, the OMAYA Edge Layer implements a Store-and-Forward mechanism:

1. **Local Buffering**: When the connection to Kafka/Cloud is lost, data is automatically diverted to a local high-performance buffer (SQLite or LevelDB).
2. **Health Monitoring**: The Edge Gateway continuously pings the cloud endpoint.
3. **Automatic Recovery**: Once connectivity is restored, the gateway begins streaming buffered data in chronological order with a rate limit to prevent network congestion.

### Conflict Resolution

In multi-edge scenarios where the same machine might be monitored by redundant gateways:

- **Last Write Wins (LWW)**: Each telemetry packet includes a high-precision UTC timestamp from the source sensor. The platform uses these timestamps to resolve conflicts, ensuring the most recent state is preserved.
- **Deduplication**: Kafka consumers use a 5-second sliding window to deduplicate messages with identical machine IDs and timestamps.

---

## Data Collection

### Data Acquisition Service

#### Service Architecture

```python
class DataAcquisitionService:
    def __init__(self, config):
        self.config = config
        self.sensors = self.load_sensors()
        self.kafka_producer = KafkaProducer(config['kafka'])
    
    def load_sensors(self):
        """Load sensor configurations from database"""
        # Implementation
        pass
    
    def collect_data(self):
        """Collect data from all sensors"""
        for sensor in self.sensors:
            try:
                data = self.read_sensor(sensor)
                validated = self.validate_data(sensor, data)
                if validated:
                    self.publish_data(sensor, data)
            except Exception as e:
                self.log_error(sensor, e)
    
    def read_sensor(self, sensor):
        """Read data from a single sensor"""
        protocol = sensor.protocol
        
        if protocol == 'modbus_tcp':
            return self.read_modbus(sensor)
        elif protocol == 'opc_ua':
            return self.read_opc_ua(sensor)
        elif protocol == 'mqtt':
            return self.read_mqtt(sensor)
        elif protocol == 'http':
            return self.read_http(sensor)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
    
    def publish_data(self, sensor, data):
        """Publish data to Kafka"""
        message = {
            'sensor_id': sensor.id,
            'machine_id': sensor.machine_id,
            'sensor_type': sensor.sensor_type,
            'timestamp': datetime.utcnow().isoformat(),
            'value': data,
            'quality': 'good'
        }
        
        self.kafka_producer.send(
            'telemetry',
            key=sensor.machine_id.encode(),
            value=json.dumps(message).encode()
        )
```

### Data Processing Pipeline

#### Kafka Consumer

```python
from kafka import KafkaConsumer

def process_telemetry():
    consumer = KafkaConsumer(
        'telemetry',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode())
    )
    
    for message in consumer:
        data = message.value
        process_sensor_data(data)

def process_sensor_data(data):
    """Process incoming sensor data"""
    # Store in TimescaleDB
    store_telemetry(data)
    
    # Check for alerts
    check_thresholds(data)
    
    # Update real-time cache
    update_cache(data)
    
    # Trigger AI predictions if needed
    if should_predict(data):
        trigger_prediction(data)
```

---

## Calibration

### Calibration Procedures

#### Temperature Sensor Calibration

```python
def calibrate_temperature_sensor(sensor_id, reference_points):
    """
    Calibrate temperature sensor using reference points
    
    Args:
        sensor_id: Sensor identifier
        reference_points: List of (reference_temp, sensor_reading) tuples
    """
    # Linear regression to find offset and gain
    import numpy as np
    
    reference_temps = [p[0] for p in reference_points]
    sensor_readings = [p[1] for p in reference_points]
    
    # Fit linear model: reference = gain * sensor + offset
    coeffs = np.polyfit(sensor_readings, reference_temps, 1)
    gain = coeffs[0]
    offset = coeffs[1]
    
    # Update sensor calibration
    update_sensor_calibration(sensor_id, {
        'gain': gain,
        'offset': offset,
        'calibration_date': datetime.now().isoformat(),
        'reference_points': reference_points
    })
```

#### Vibration Sensor Calibration

```python
def calibrate_vibration_sensor(sensor_id, reference_vibration):
    """
    Calibrate vibration sensor using reference source
    
    Args:
        sensor_id: Sensor identifier
        reference_vibration: Known vibration level (mm/s)
    """
    # Take multiple readings
    readings = []
    for _ in range(10):
        reading = read_sensor(sensor_id)
        readings.append(reading)
        time.sleep(0.1)
    
    avg_reading = sum(readings) / len(readings)
    
    # Calculate correction factor
    correction_factor = reference_vibration / avg_reading
    
    # Update sensor calibration
    update_sensor_calibration(sensor_id, {
        'correction_factor': correction_factor,
        'calibration_date': datetime.now().isoformat(),
        'reference_value': reference_vibration
    })
```

### Calibration Schedule

#### Recommended Calibration Intervals

- **Temperature Sensors**: Every 6 months
- **Vibration Sensors**: Every 12 months
- **Pressure Sensors**: Every 12 months
- **Flow Sensors**: Every 12 months
- **Position Sensors**: Every 24 months

#### Calibration Tracking

```python
def schedule_calibration(sensor_id, interval_days):
    """Schedule automatic calibration reminders"""
    next_calibration = datetime.now() + timedelta(days=interval_days)
    
    # Store in database
    store_calibration_schedule(sensor_id, next_calibration)
    
    # Set up reminder
    schedule_reminder(sensor_id, next_calibration)
```

---

## Troubleshooting

### Common Issues

#### No Data from Sensor

**Possible Causes:**
- Sensor not powered
- Incorrect wiring
- Wrong IP address
- Firewall blocking connection
- Sensor malfunction

**Troubleshooting Steps:**
1. Check power supply to sensor
2. Verify wiring connections
3. Ping sensor IP address
4. Check firewall rules
5. Test with manufacturer's software
6. Replace sensor if necessary

#### Inaccurate Readings

**Possible Causes:**
- Sensor not calibrated
- Environmental interference
- Wiring issues
- Incorrect scaling factors

**Troubleshooting Steps:**
1. Recalibrate sensor
2. Check for electromagnetic interference
3. Verify wiring integrity
4. Review scaling configuration
5. Compare with reference sensor

#### Intermittent Connection

**Possible Causes:**
- Loose connections
- Network issues
- Cable damage
- Power fluctuations

**Troubleshooting Steps:**
1. Check all connections
2. Test network stability
3. Inspect cables for damage
4. Check power supply stability
5. Use shielded cables if needed

---

## Best Practices

### Sensor Selection

1. **Match sensor to application**
   - Consider environmental conditions
   - Ensure appropriate measurement range
   - Verify accuracy requirements

2. **Choose appropriate protocol**
   - Modbus for simple installations
   - OPC UA for complex systems
   - MQTT for remote/IoT applications

3. **Plan for maintenance**
   - Select sensors with easy calibration
   - Consider replacement availability
   - Plan for spare parts

### Installation Best Practices

1. **Follow manufacturer guidelines**
   - Read installation manuals
   - Use recommended mounting hardware
   - Follow torque specifications

2. **Implement proper grounding**
   - Establish single-point ground
   - Avoid ground loops
   - Use star grounding topology

3. **Document everything**
   - Create wiring diagrams
   - Label all connections
   - Maintain configuration records

### Data Quality Best Practices

1. **Implement data validation**
   - Range checking
   - Rate of change checking
   - Consistency checking

2. **Handle missing data**
   - Implement interpolation
   - Use last known good value
   - Flag data quality issues

3. **Monitor sensor health**
   - Track calibration status
   - Monitor communication errors
   - Detect sensor degradation

---

## Support

For additional help:
- Documentation: [https://docs.omaya-platform.com](https://docs.omaya-platform.com)
- Issues: [https://github.com/Bunay-1/OMAYA-Project/issues](https://github.com/Bunay-1/OMAYA-Project/issues)
- Email: support@omaya-platform.com

---

**Version**: 3.1.0
**Last Updated**: June 2026
