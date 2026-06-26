"""
MQTT Sparkplug B Adapter for OMAYA
Enterprise implementation of Sparkplug B specification
"""
import json
import logging
import time
from typing import Dict, Any, List, Optional, Callable
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class SparkplugBAdapter:
    """Enterprise Sparkplug B Adapter"""
    
    def __init__(self, broker_host: str, broker_port: int, client_id: str, group_id: str):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.group_id = group_id
        self.connected = False
        self.last_error = None
        self.sequence_number = 0
        self.message_callbacks: Dict[str, Callable] = {}
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connected to MQTT broker: {self.broker_host}")
            # Subscribe to command topics
            self.client.subscribe(f"spBv1.0/{self.group_id}/#")
        else:
            self.connected = False
            self.last_error = f"Connection failed with code {rc}"
            logger.error(self.last_error)

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.info("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, msg):
        topic_parts = msg.topic.split('/')
        if len(topic_parts) >= 4:
            message_type = topic_parts[2]
            edge_node_id = topic_parts[3]
            callback_key = f"{message_type}/{edge_node_id}"
            
            if callback_key in self.message_callbacks:
                try:
                    payload = json.loads(msg.payload.decode())
                    self.message_callbacks[callback_key](msg.topic, payload)
                except Exception as e:
                    logger.error(f"Error in Sparkplug message callback: {e}")

    def _get_next_sequence_number(self) -> int:
        current_seq = self.sequence_number
        self.sequence_number = (self.sequence_number + 1) % 256
        return current_seq

    def create_birth_payload(self, edge_node_id: str, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create NBIRTH or DBIRTH payload"""
        return {
            "timestamp": int(time.time() * 1000),
            "metrics": metrics,
            "seq": self._get_next_sequence_number()
        }

    def create_data_payload(self, edge_node_id: str, device_id: str, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create DDATA payload"""
        return {
            "timestamp": int(time.time() * 1000),
            "metrics": metrics,
            "seq": self._get_next_sequence_number()
        }

    def create_metric(self, name: str, value: Any, data_type: str, quality: int = 192) -> Dict[str, Any]:
        """Create a Sparkplug metric object"""
        return {
            "name": name,
            "value": value,
            "dataType": data_type,
            "quality": quality,
            "timestamp": int(time.time() * 1000)
        }

    def register_callback(self, message_type: str, edge_node_id: str, callback: Callable):
        """Register callback for specific message types (NCMD, DCMD)"""
        self.message_callbacks[f"{message_type}/{edge_node_id}"] = callback

    def publish_node_birth(self, edge_node_id: str, metrics: List[Dict[str, Any]]) -> bool:
        if not self.connected: return False
        topic = f"spBv1.0/{self.group_id}/NBIRTH/{edge_node_id}"
        payload = self.create_birth_payload(edge_node_id, metrics)
        res = self.client.publish(topic, json.dumps(payload), qos=0)
        return res.rc == 0

    def publish_device_birth(self, edge_node_id: str, device_id: str, metrics: List[Dict[str, Any]]) -> bool:
        if not self.connected: return False
        topic = f"spBv1.0/{self.group_id}/DBIRTH/{edge_node_id}/{device_id}"
        payload = self.create_birth_payload(edge_node_id, metrics)
        res = self.client.publish(topic, json.dumps(payload), qos=0)
        return res.rc == 0

    def publish_device_data(self, edge_node_id: str, device_id: str, metrics: List[Dict[str, Any]]) -> bool:
        if not self.connected: return False
        topic = f"spBv1.0/{self.group_id}/DDATA/{edge_node_id}/{device_id}"
        payload = self.create_data_payload(edge_node_id, device_id, metrics)
        res = self.client.publish(topic, json.dumps(payload), qos=0)
        return res.rc == 0

    def publish_node_death(self, edge_node_id: str) -> bool:
        if not self.connected: return False
        topic = f"spBv1.0/{self.group_id}/NDEATH/{edge_node_id}"
        payload = {"timestamp": int(time.time() * 1000)}
        res = self.client.publish(topic, json.dumps(payload), qos=0)
        return res.rc == 0

    def get_last_error(self) -> Optional[str]:
        return self.last_error

    def is_connected(self) -> bool:
        return self.connected
