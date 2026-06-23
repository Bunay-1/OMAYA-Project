"""
Kafka Consumer for OMAYA Machine Events
Consumes and processes machine events in real-time
"""

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
import threading
from typing import Callable, Optional, Dict, Any
import os
from kafka_streams import (
    process_telemetry_event,
    process_alert_event,
    process_prediction_event,
    telemetry_aggregator,
    alert_aggregator,
    prediction_tracker
)

logger = logging.getLogger(__name__)


class MachineEventConsumer:
    """Consumes machine events from Kafka topics"""
    
    def __init__(self, group_id: str = "omaya-monitoring"):
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        
        self.group_id = group_id
        self.consumer = None
        self.running = False
        self.thread = None
        
        try:
            self.consumer = KafkaConsumer(
                bootstrap_servers=bootstrap_servers.split(","),
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                session_timeout_ms=30000,
            )
            logger.info(f"✅ Kafka consumer initialized: {bootstrap_servers}")
        except Exception as e:
            logger.warning(f"⚠️ Kafka not available: {e}")
            self.consumer = None
    
    def subscribe(self, topics: list):
        """
        Subscribe to Kafka topics
        
        Args:
            topics: List of topic names
        """
        if not self.consumer:
            logger.warning("Kafka consumer not initialized")
            return
        
        try:
            self.consumer.subscribe(topics)
            logger.info(f"Subscribed to topics: {topics}")
        except Exception as e:
            logger.error(f"Error subscribing to topics: {e}")
    
    def start_consuming(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Start consuming events in background thread
        
        Args:
            callback: Function to call for each event
        """
        if not self.consumer:
            logger.warning("Kafka consumer not initialized")
            return
        
        if self.running:
            logger.warning("Consumer already running")
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._consume_loop,
            args=(callback,),
            daemon=True
        )
        self.thread.start()
        logger.info("Started consuming events")
    
    def _consume_loop(self, callback: Callable):
        """
        Consume loop - processes messages indefinitely
        
        Args:
            callback: Function to process each message
        """
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    callback(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except KafkaError as e:
            logger.error(f"Kafka error in consume loop: {e}")
        finally:
            self.running = False
            logger.info("Consume loop ended")
    
    def stop_consuming(self):
        """Stop consuming events"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Stopped consuming events")
    
    def close(self):
        """Close consumer connection"""
        self.stop_consuming()
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")


class KafkaStreamProcessor:
    """Process Kafka streams for analytics and storage"""
    
    def __init__(self):
        self.telemetry_callbacks = []
        self.alert_callbacks = []
        self.prediction_callbacks = []
    
    def register_telemetry_handler(self, handler: Callable):
        """Register handler for telemetry events"""
        self.telemetry_callbacks.append(handler)
    
    def register_alert_handler(self, handler: Callable):
        """Register handler for alert events"""
        self.alert_callbacks.append(handler)
    
    def register_prediction_handler(self, handler: Callable):
        """Register handler for prediction events"""
        self.prediction_callbacks.append(handler)
    
    def process_event(self, event: Dict[str, Any]):
        """
        Route event to appropriate handlers
        
        Args:
            event: Event data from Kafka
        """
        event_type = event.get("event_type", "unknown")
        
        if event_type == "telemetry":
            process_telemetry_event(event)
            for handler in self.telemetry_callbacks:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in telemetry handler: {e}")
        
        elif event_type == "alert":
            process_alert_event(event)
            for handler in self.alert_callbacks:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
        
        elif event_type == "prediction":
            process_prediction_event(event)
            for handler in self.prediction_callbacks:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in prediction handler: {e}")


# Singleton instances
consumer = MachineEventConsumer()
stream_processor = KafkaStreamProcessor()
