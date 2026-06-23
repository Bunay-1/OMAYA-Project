"""
MQTT Sparkplug B Adapter for OMAYA Platform
Industrial IoT messaging standard with rich metadata.
"""
from typing import Dict, Any, Optional, List, Callable
import logging
import json
import uuid
from datetime import datetime
import paho.mqtt.client as mqtt
from threading import Thread
import time

logger = logging.getLogger(__name__)

class SparkplugBAdapter:
    """
    MQTT Sparkplug B Adapter
    Implements Sparkplug B payload encoding for industrial IoT
    """
    
    def __init__(self, broker_host: str, broker_port: int = 1883,
                 client_id: str = None, username: str = None,
                 password: str = None, group_id: str = "OMAYA"):
        """
        Initialize MQTT Sparkplug B adapter.
        
        Args:
            broker_host: MQTT broker hostname/IP
            broker_port: MQTT broker port

            client_id: Unique client ID
            username: MQTT username
            password: MQTT password
            group_id: Sparkplug B group ID
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id or f"omaya-{uuid.uuid4().hex[:8]}"
        self.username = username
        self.password = password
        self.group_id = group_id
        self.client = None
        self.connected = False
        self.last_error: Optional[str] = None
        self.message_callbacks: Dict[str, Callable] = {}
        self.sequence_number = 0
        
    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            
            self.client = mqtt.Client(
                client_id=self.client_id,
                protocol=mqtt.MQTTv311,
                transport="tcp"
            )
            
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                logger.info(f"Successfully connected to MQTT broker")
                return True
            else:
                self.last_error = "Connection timeout"
                logger.error(f"Failed to connect to MQTT broker: timeout")
                return False
                
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            logger.error(f"Error connecting to MQTT broker: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from MQTT broker."""
        try:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
                self.connected = False
                logger.info("Disconnected from MQTT broker")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            self.connected = True
            self.last_error = None
            logger.info("MQTT client connected")
            
            # Subscribe to Sparkplug B topics
            self._subscribe_to_topics()
        else:
            self.connected = False
            self.last_error = f"Connection failed with code {rc}"
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        self.connected = False
        logger.warning(f"MQTT client disconnected (rc={rc})")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Parse Sparkplug B topic
            topic_parts = topic.split('/')
            if len(topic_parts) >= 4:
                namespace = topic_parts[0]
                group_id = topic_parts[1]
                message_type = topic_parts[2]
                edge_node_id = topic_parts[3]
                
                # Call registered callback
                callback_key = f"{message_type}/{edge_node_id}"
                if callback_key in self.message_callbacks:
                    self.message_callbacks[callback_key](topic, payload)
                
                logger.debug(f"Received Sparkplug B message: {topic}")
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _subscribe_to_topics(self):
        """Subscribe to Sparkplug B topics."""
        try:
            # Subscribe to NCMD (Node Command) messages
            self.client.subscribe(f"spBv1.0/{self.group_id}/NCMD/#", qos=1)
            # Subscribe to DCMD (Device Command) messages
            self.client.subscribe(f"spBv1.0/{self.group_id}/DCMD/#", qos=1)
            logger.info("Subscribed to Sparkplug B command topics")
        except Exception as e:
            logger.error(f"Error subscribing to topics: {e}")
    
    def register_callback(self, message_type: str, edge_node_id: str, callback: Callable):
        """
        Register callback for specific message type and edge node.
        
        Args:
            message_type: Message type (NCMD, DCMD, etc.)
            edge_node_id: Edge node identifier
            callback: Callback function
        """
        callback_key = f"{message_type}/{edge_node_id}"
        self.message_callbacks[callback_key] = callback
        logger.debug(f"Registered callback for {callback_key}")
    
    def _get_next_sequence_number(self) -> int:
        """Get next sequence number (wraps at 256)."""
        self.sequence_number = (self.sequence_number + 1) % 256
        return self.sequence_number
    
    def create_birth_payload(self, edge_node_id: str, 
                           metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create Sparkplug B NBIRTH (Node Birth) payload.
        
        Args:
            edge_node_id: Edge node identifier
            metrics: List of metrics to include
            
        Returns:
            Sparkplug B payload dictionary
        """
        payload = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metrics": [],
            "seq": self._get_next_sequence_number(),
            "uuid": str(uuid.uuid4())
        }
        
        for metric in metrics:
            payload["metrics"].append({
                "name": metric["name"],
                "value": metric.get("value"),
                "timestamp": metric.get("timestamp", payload["timestamp"]),
                "dataType": metric.get("dataType", "Int32"),
                "quality": metric.get("quality", 192)  # 192 = Good
            })
        
        return payload
    
    def create_data_payload(self, edge_node_id: str, device_id: str,
                           metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create Sparkplug B DDATA (Device Data) payload.
        
        Args:
            edge_node_id: Edge node identifier
            device_id: Device identifier
            metrics: List of metrics to include
            
        Returns:
            Sparkplug B payload dictionary
        """
        payload = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metrics": [],
            "seq": self._get_next_sequence_number(),
            "uuid": str(uuid.uuid4())
        }
        
        for metric in metrics:
            payload["metrics"].append({
                "name": metric["name"],
                "value": metric.get("value"),
                "timestamp": metric.get("timestamp", payload["timestamp"]),
                "dataType": metric.get("dataType", "Int32"),
                "quality": metric.get("quality", 192)
            })
        
        return payload
    
    def publish_node_birth(self, edge_node_id: str, metrics: List[Dict[str, Any]]) -> bool:
        """
        Publish NBIRTH (Node Birth) message.
        
        Args:
            edge_node_id: Edge node identifier
            metrics: List of metrics to publish
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            payload = self.create_birth_payload(edge_node_id, metrics)
            topic = f"spBv1.0/{self.group_id}/NBIRTH/{edge_node_id}"
            
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=1,
                retain=True
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published NBIRTH for {edge_node_id}")
                return True
            else:
                self.last_error = f"Publish failed with code {result.rc}"
                logger.error(f"Failed to publish NBIRTH: {result.rc}")
                return False
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error publishing NBIRTH: {e}")
            return False
    
    def publish_device_birth(self, edge_node_id: str, device_id: str,
                           metrics: List[Dict[str, Any]]) -> bool:
        """
        Publish DBIRTH (Device Birth) message.
        
        Args:
            edge_node_id: Edge node identifier
            device_id: Device identifier
            metrics: List of metrics to publish
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            payload = self.create_data_payload(edge_node_id, device_id, metrics)
            topic = f"spBv1.0/{self.group_id}/DBIRTH/{edge_node_id}/{device_id}"
            
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=1,
                retain=True
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published DBIRTH for {device_id}")
                return True
            else:
                self.last_error = f"Publish failed with code {result.rc}"
                logger.error(f"Failed to publish DBIRTH: {result.rc}")
                return False
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error publishing DBIRTH: {e}")
            return False
    
    def publish_device_data(self, edge_node_id: str, device_id: str,
                           metrics: List[Dict[str, Any]]) -> bool:
        """
        Publish DDATA (Device Data) message.
        
        Args:
            edge_node_id: Edge node identifier
            device_id: Device identifier
            metrics: List of metrics to publish
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            payload = self.create_data_payload(edge_node_id, device_id, metrics)
            topic = f"spBv1.0/{self.group_id}/DDATA/{edge_node_id}/{device_id}"
            
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=1,
                retain=False
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published DDATA for {device_id}")
                return True
            else:
                self.last_error = f"Publish failed with code {result.rc}"
                logger.error(f"Failed to publish DDATA: {result.rc}")
                return False
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error publishing DDATA: {e}")
            return False
    
    def publish_node_death(self, edge_node_id: str) -> bool:
        """
        Publish NDEATH (Node Death) message.
        
        Args:
            edge_node_id: Edge node identifier
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            payload = {
                "timestamp": int(datetime.now().timestamp() * 1000),
                "seq": self._get_next_sequence_number(),
                "uuid": str(uuid.uuid4())
            }
            topic = f"spBv1.0/{self.group_id}/NDEATH/{edge_node_id}"
            
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=1,
                retain=True
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published NDEATH for {edge_node_id}")
                return True
            else:
                self.last_error = f"Publish failed with code {result.rc}"
                logger.error(f"Failed to publish NDEATH: {result.rc}")
                return False
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error publishing NDEATH: {e}")
            return False
    
    def create_metric(self, name: str, value: Any, data_type: str = "Int32",
                     quality: int = 192) -> Dict[str, Any]:
        """
        Create a metric dictionary.
        
        Args:
            name: Metric name
            value: Metric value
            data_type: Sparkplug B data type
            quality: Quality code (192 = Good)
            
        Returns:
            Metric dictionary
        """
        return {
            "name": name,
            "value": value,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "dataType": data_type,
            "quality": quality
        }
    
    def is_connected(self) -> bool:
        """Check if connected to MQTT broker."""
        return self.connected
    
    def get_last_error(self) -> Optional[str]:
        """Get last error message."""
        return self.last_error
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
