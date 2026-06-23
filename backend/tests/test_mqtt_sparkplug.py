"""
Tests for MQTT Sparkplug B Adapter
"""
import pytest
from backend.mqtt_sparkplug import SparkplugBAdapter
from unittest.mock import Mock, patch
import json


@pytest.fixture
def mqtt_adapter():
    """Create MQTT Sparkplug B adapter instance."""
    return SparkplugBAdapter(
        broker_host="localhost",
        broker_port=1883,
        client_id="test-client",
        group_id="OMAYA"
    )


def test_mqtt_adapter_init(mqtt_adapter):
    """Test MQTT adapter initialization."""
    assert mqtt_adapter.broker_host == "localhost"
    assert mqtt_adapter.broker_port == 1883
    assert mqtt_adapter.group_id == "OMAYA"
    assert mqtt_adapter.connected is False


@patch('backend.mqtt_sparkplug.mqtt.Client')
def test_mqtt_connect_success(mock_client_class, mqtt_adapter):
    """Test successful connection to MQTT broker."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    # Simulate immediate connection
    mqtt_adapter._on_connect(mock_client, None, {}, 0)
    
    assert mqtt_adapter.connected is True


@patch('backend.mqtt_sparkplug.mqtt.Client')
def test_mqtt_connect_failure(mock_client_class, mqtt_adapter):
    """Test failed connection to MQTT broker."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    mqtt_adapter._on_connect(mock_client, None, {}, 1)
    
    assert mqtt_adapter.connected is False
    assert mqtt_adapter.last_error is not None


@patch('backend.mqtt_sparkplug.mqtt.Client')
def test_mqtt_disconnect(mock_client_class, mqtt_adapter):
    """Test disconnection from MQTT broker."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mqtt_adapter.client = mock_client
    mqtt_adapter.connected = True
    
    result = mqtt_adapter.disconnect()
    
    assert result is True
    assert mqtt_adapter.connected is False
    mock_client.loop_stop.assert_called_once()


def test_create_birth_payload(mqtt_adapter):
    """Test creating NBIRTH payload."""
    edge_node_id = "EDGE-001"
    metrics = [
        {"name": "temperature", "value": 25.5, "dataType": "Float"},
        {"name": "pressure", "value": 101.3, "dataType": "Float"}
    ]
    
    payload = mqtt_adapter.create_birth_payload(edge_node_id, metrics)
    
    assert payload is not None
    assert 'timestamp' in payload
    assert 'metrics' in payload
    assert 'seq' in payload
    assert len(payload['metrics']) == 2


def test_create_data_payload(mqtt_adapter):
    """Test creating DDATA payload."""
    edge_node_id = "EDGE-001"
    device_id = "DEVICE-001"
    metrics = [
        {"name": "speed", "value": 1500, "dataType": "Int32"}
    ]
    
    payload = mqtt_adapter.create_data_payload(edge_node_id, device_id, metrics)
    
    assert payload is not None
    assert 'timestamp' in payload
    assert 'metrics' in payload
    assert len(payload['metrics']) == 1


def test_create_metric(mqtt_adapter):
    """Test creating a metric."""
    metric = mqtt_adapter.create_metric(
        name="temperature",
        value=25.5,
        data_type="Float",
        quality=192
    )
    
    assert metric is not None
    assert metric['name'] == "temperature"
    assert metric['value'] == 25.5
    assert metric['dataType'] == "Float"
    assert metric['quality'] == 192


def test_register_callback(mqtt_adapter):
    """Test registering callback."""
    def callback(topic, payload):
        pass
    
    mqtt_adapter.register_callback("NCMD", "EDGE-001", callback)
    
    assert "NCMD/EDGE-001" in mqtt_adapter.message_callbacks


def test_sequence_number_increment(mqtt_adapter):
    """Test sequence number increment."""
    initial_seq = mqtt_adapter.sequence_number
    mqtt_adapter._get_next_sequence_number()
    
    assert mqtt_adapter.sequence_number == (initial_seq + 1) % 256


def test_sequence_number_wrap(mqtt_adapter):
    """Test sequence number wrapping at 256."""
    mqtt_adapter.sequence_number = 255
    seq = mqtt_adapter._get_next_sequence_number()
    
    assert seq == 0


@patch('backend.mqtt_sparkplug.mqtt.Client')
def test_publish_node_birth(mock_client_class, mqtt_adapter):
    """Test publishing NBIRTH message."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    mqtt_adapter.connected = True
    mqtt_adapter.client = mock_client
    
    mock_result = Mock()
    mock_result.rc = 0
    mock_client.publish.return_value = mock_result
    
    edge_node_id = "EDGE-001"
    metrics = [{"name": "temperature", "value": 25.5, "dataType": "Float"}]
    
    result = mqtt_adapter.publish_node_birth(edge_node_id, metrics)
    
    assert result is True
    mock_client.publish.assert_called_once()


@patch('backend.mqtt_sparkplug.mqtt.Client')
def test_publish_device_birth(mock_client_class, mqtt_adapter):
    """Test publishing DBIRTH message."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    mqtt_adapter.connected = True
    mqtt_adapter.client = mock_client
    
    mock_result = Mock()
    mock_result.rc = 0
    mock_client.publish.return_value = mock_result
    
    edge_node_id = "EDGE-001"
    device_id = "DEVICE-001"
    metrics = [{"name": "speed", "value": 1500, "dataType": "Int32"}]
    
    result = mqtt_adapter.publish_device_birth(edge_node_id, device_id, metrics)
    
    assert result is True
    mock_client.publish.assert_called_once()


@patch('backend.mqtt_sparkplug.mqtt.Client')
def test_publish_device_data(mock_client_class, mqtt_adapter):
    """Test publishing DDATA message."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    mqtt_adapter.connected = True
    mqtt_adapter.client = mock_client
    
    mock_result = Mock()
    mock_result.rc = 0
    mock_client.publish.return_value = mock_result
    
    edge_node_id = "EDGE-001"
    device_id = "DEVICE-001"
    metrics = [{"name": "speed", "value": 1500, "dataType": "Int32"}]
    
    result = mqtt_adapter.publish_device_data(edge_node_id, device_id, metrics)
    
    assert result is True


@patch('backend.mqtt_sparkplug.mqtt.Client')
def test_publish_node_death(mock_client_class, mqtt_adapter):
    """Test publishing NDEATH message."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    mqtt_adapter.connected = True
    mqtt_adapter.client = mock_client
    
    mock_result = Mock()
    mock_result.rc = 0
    mock_client.publish.return_value = mock_result
    
    edge_node_id = "EDGE-001"
    
    result = mqtt_adapter.publish_node_death(edge_node_id)
    
    assert result is True
    mock_client.publish.assert_called_once()


def test_on_message(mqtt_adapter):
    """Test message callback."""
    mock_client = Mock()
    mock_msg = Mock()
    mock_msg.topic = "spBv1.0/OMAYA/NCMD/EDGE-001"
    mock_msg.payload = b'{"test": "data"}'
    
    callback_called = []
    
    def test_callback(topic, payload):
        callback_called.append(True)
    
    mqtt_adapter.register_callback("NCMD", "EDGE-001", test_callback)
    mqtt_adapter._on_message(mock_client, None, mock_msg)
    
    assert len(callback_called) > 0


def test_get_last_error(mqtt_adapter):
    """Test getting last error."""
    mqtt_adapter.last_error = "Test error"
    assert mqtt_adapter.get_last_error() == "Test error"


def test_is_connected(mqtt_adapter):
    """Test connection status."""
    mqtt_adapter.connected = True
    assert mqtt_adapter.is_connected() is True
    
    mqtt_adapter.connected = False
    assert mqtt_adapter.is_connected() is False
