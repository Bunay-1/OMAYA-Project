"""
Kafka Producer for OMAYA Machine Events
Publishes machine telemetry and alerts to Kafka topics
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class MachineEventProducer:
    """Produces machine events to Kafka topics"""
    
    def __init__(self):
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks="all",  # Wait for all replicas
                retries=3,
                linger_ms=10,  # Batch messages for 10ms
            )
            logger.info(f"✅ Kafka producer connected: {bootstrap_servers}")
        except Exception as e:
            logger.warning(f"⚠️ Kafka not available: {e}")
            self.producer = None
    
    def publish_telemetry(self, machine_id: str, telemetry: Dict[str, Any]) -> bool:
        """
        Publish machine telemetry to 'machine-telemetry' topic
        
        Args:
            machine_id: Machine identifier
            telemetry: Telemetry data (temperature, vibration, etc.)
            
        Returns:
            bool: Success status
        """
        if not self.producer:
            return False
        
        try:
            event = {
                "machine_id": machine_id,
                "timestamp": datetime.now().isoformat(),
                "data": telemetry,
                "event_type": "telemetry"
            }
            
            future = self.producer.send("machine-telemetry", value=event)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Telemetry published: {machine_id} to partition {record_metadata.partition}"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error publishing telemetry: {e}")
            return False
    
    def publish_alert(
        self,
        machine_id: str,
        severity: str,
        title: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Publish alert event to 'machine-alerts' topic
        
        Args:
            machine_id: Machine identifier
            severity: Alert severity (critical, error, warning, info)
            title: Alert title
            message: Alert message
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        if not self.producer:
            return False
        
        try:
            event = {
                "machine_id": machine_id,
                "severity": severity,
                "title": title,
                "message": message,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "event_type": "alert"
            }
            
            future = self.producer.send("machine-alerts", value=event)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Alert published: {machine_id} ({severity}) to partition {record_metadata.partition}"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error publishing alert: {e}")
            return False
    
    def publish_prediction(
        self,
        machine_id: str,
        prediction_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Publish AI prediction to 'machine-predictions' topic
        
        Args:
            machine_id: Machine identifier
            prediction_type: Type of prediction (failure, rul, anomaly)
            data: Prediction data
            
        Returns:
            bool: Success status
        """
        if not self.producer:
            return False
        
        try:
            event = {
                "machine_id": machine_id,
                "prediction_type": prediction_type,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "event_type": "prediction"
            }
            
            future = self.producer.send("machine-predictions", value=event)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Prediction published: {machine_id} ({prediction_type}) to partition {record_metadata.partition}"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error publishing prediction: {e}")
            return False
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")


# Singleton instance
producer = MachineEventProducer()
