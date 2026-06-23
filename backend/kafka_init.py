"""
Kafka Topic Initialization
Creates required topics with proper configurations
"""
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import os
import logging

logger = logging.getLogger(__name__)

def create_topics():
    """Create Kafka topics with appropriate configurations"""
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers.split(','),
            client_id='omaya-topic-creator'
        )
        
        topics = [
            NewTopic(
                name="machine-telemetry",
                num_partitions=10,  # High throughput
                replication_factor=1,
                topic_configs={
                    "retention.ms": "604800000",  # 7 days
                    "compression.type": "snappy"
                }
            ),
            NewTopic(
                name="machine-alerts",
                num_partitions=5,
                replication_factor=1,
                topic_configs={
                    "retention.ms": "2592000000",  # 30 days
                    "compression.type": "snappy"
                }
            ),
            NewTopic(
                name="machine-predictions",
                num_partitions=5,
                replication_factor=1,
                topic_configs={
                    "retention.ms": "1209600000",  # 14 days
                    "compression.type": "snappy"
                }
            ),
            NewTopic(
                name="machine-maintenance",
                num_partitions=3,
                replication_factor=1,
                topic_configs={
                    "retention.ms": "7776000000",  # 90 days
                    "compression.type": "snappy"
                }
            )
        ]
        
        try:
            admin_client.create_topics(new_topics=topics, validate_only=False)
            logger.info(f"✅ Created {len(topics)} Kafka topics")
        except TopicAlreadyExistsError:
            logger.info("Topics already exist")
        
        admin_client.close()
        
    except Exception as e:
        logger.error(f"Error creating topics: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_topics()
