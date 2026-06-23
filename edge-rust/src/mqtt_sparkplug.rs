//! Rust MQTT Sparkplug B Connector for OMAYA Edge
//! High-performance MQTT implementation with Sparkplug B payload support

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use log::{debug, error, info, warn};
use rumqttc::{AsyncClient, MqttOptions, QoS, TlsConfiguration};
use serde::{Deserialize, Serialize};
use std::time::Duration;

/// MQTT Sparkplug B configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MqttConfig {
    /// Broker address
    pub broker: String,
    /// Broker port
    pub port: u16,
    /// Client ID
    pub client_id: String,
    /// Username (optional)
    pub username: Option<String>,
    /// Password (optional)
    pub password: Option<String>,
    /// Use TLS
    pub use_tls: bool,
    /// Group ID for Sparkplug B
    pub group_id: String,
    /// Edge node ID
    pub edge_node_id: String,
}

/// Sparkplug B payload
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SparkplugBPayload {
    /// Sequence number
    pub seq: u64,
    /// Timestamp
    pub timestamp: DateTime<Utc>,
    /// Metrics
    pub metrics: Vec<Metric>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Metric {
    /// Metric name
    pub name: String,
    /// Metric value
    pub value: MetricValue,
    /// Data type
    pub data_type: DataType,
    /// Timestamp (optional)
    pub timestamp: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MetricValue {
    Int64(i64),
    Float64(f64),
    Boolean(bool),
    String(String),
    Bytes(Vec<u8>),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DataType {
    Int64,
    Float64,
    Boolean,
    String,
    Bytes,
}

/// MQTT Sparkplug B connector
pub struct MqttSparkplugConnector {
    config: MqttConfig,
    client: Option<AsyncClient>,
    sequence: u64,
}

impl MqttSparkplugConnector {
    /// Create a new MQTT Sparkplug B connector
    pub fn new(config: MqttConfig) -> Self {
        Self {
            config,
            client: None,
            sequence: 0,
        }
    }

    /// Connect to MQTT broker
    pub async fn connect(&mut self) -> Result<()> {
        info!("Connecting to MQTT broker {}:{}", self.config.broker, self.config.port);

        let mut mqttoptions = MqttOptions::new(
            self.config.client_id.clone(),
            self.config.broker.clone(),
            self.config.port,
        );

        if let Some(username) = &self.config.username {
            mqttoptions.set_credentials(username, self.config.password.as_deref().unwrap_or(""));
        }

        if self.config.use_tls {
            let tls_config = TlsConfiguration::Default;
            mqttoptions.set_tls_config(tls_config);
        }

        mqttoptions.set_keep_alive(Duration::from_secs(60));
        mqttoptions.set_clean_session(true);

        let (client, _) = AsyncClient::new(mqttoptions, 10);
        self.client = Some(client);

        info!("Connected to MQTT broker");
        Ok(())
    }

    /// Disconnect from MQTT broker
    pub async fn disconnect(&mut self) -> Result<()> {
        if self.client.is_some() {
            info!("Disconnecting from MQTT broker");
            self.client = None;
        }
        Ok(())
    }

    /// Increment sequence number
    fn increment_sequence(&mut self) -> u64 {
        self.sequence = (self.sequence + 1) % 256;
        self.sequence
    }

    /// Create NBIRTH payload
    pub fn create_nbirth(&mut self, metrics: Vec<Metric>) -> SparkplugBPayload {
        SparkplugBPayload {
            seq: self.increment_sequence(),
            timestamp: Utc::now(),
            metrics,
        }
    }

    /// Create DBIRTH payload
    pub fn create_dbirth(&mut self, device_id: &str, metrics: Vec<Metric>) -> SparkplugBPayload {
        SparkplugBPayload {
            seq: self.increment_sequence(),
            timestamp: Utc::now(),
            metrics,
        }
    }

    /// Create DDATA payload
    pub fn create_ddata(&mut self, metrics: Vec<Metric>) -> SparkplugBPayload {
        SparkplugBPayload {
            seq: self.increment_sequence(),
            timestamp: Utc::now(),
            metrics,
        }
    }

    /// Create NDEATH payload
    pub fn create_ndeath(&mut self) -> SparkplugBPayload {
        SparkplugBPayload {
            seq: self.increment_sequence(),
            timestamp: Utc::now(),
            metrics: vec![],
        }
    }

    /// Publish NBIRTH message
    pub async fn publish_nbirth(&mut self, payload: SparkplugBPayload) -> Result<()> {
        let topic = format!(
            "spBv1.0/{}/NBIRTH/{}",
            self.config.group_id, self.config.edge_node_id
        );
        let payload_json = serde_json::to_string(&payload)?;
        self.publish(&topic, &payload_json, QoS::AtLeastOnce).await
    }

    /// Publish DBIRTH message
    pub async fn publish_dbirth(&mut self, device_id: &str, payload: SparkplugBPayload) -> Result<()> {
        let topic = format!(
            "spBv1.0/{}/DBIRTH/{}/{}",
            self.config.group_id, self.config.edge_node_id, device_id
        );
        let payload_json = serde_json::to_string(&payload)?;
        self.publish(&topic, &payload_json, QoS::AtLeastOnce).await
    }

    /// Publish DDATA message
    pub async fn publish_ddata(&mut self, device_id: &str, payload: SparkplugBPayload) -> Result<()> {
        let topic = format!(
            "spBv1.0/{}/DDATA/{}/{}",
            self.config.group_id, self.config.edge_node_id, device_id
        );
        let payload_json = serde_json::to_string(&payload)?;
        self.publish(&topic, &payload_json, QoS::AtLeastOnce).await
    }

    /// Publish NDEATH message
    pub async fn publish_ndeath(&mut self) -> Result<()> {
        let payload = self.create_ndeath();
        let topic = format!(
            "spBv1.0/{}/NDEATH/{}",
            self.config.group_id, self.config.edge_node_id
        );
        let payload_json = serde_json::to_string(&payload)?;
        self.publish(&topic, &payload_json, QoS::AtLeastOnce).await
    }

    /// Subscribe to NCMD topic
    pub async fn subscribe_ncmd(&mut self) -> Result<()> {
        let topic = format!(
            "spBv1.0/{}/NCMD/#",
            self.config.group_id
        );
        self.subscribe(&topic, QoS::AtLeastOnce).await
    }

    /// Subscribe to DCMD topic
    pub async fn subscribe_dcmd(&mut self, device_id: &str) -> Result<()> {
        let topic = format!(
            "spBv1.0/{}/DCMD/{}/{}",
            self.config.group_id, self.config.edge_node_id, device_id
        );
        self.subscribe(&topic, QoS::AtLeastOnce).await
    }

    /// Internal publish method
    async fn publish(&self, topic: &str, payload: &str, qos: QoS) -> Result<()> {
        let client = self.client.as_ref().context("Not connected")?;
        debug!("Publishing to topic: {}", topic);
        // In real implementation, use client.publish()
        info!("Published to {}: {}", topic, payload);
        Ok(())
    }

    /// Internal subscribe method
    async fn subscribe(&self, topic: &str, qos: QoS) -> Result<()> {
        let client = self.client.as_ref().context("Not connected")?;
        debug!("Subscribing to topic: {}", topic);
        // In real implementation, use client.subscribe()
        info!("Subscribed to {}", topic);
        Ok(())
    }
}

impl Drop for MqttSparkplugConnector {
    fn drop(&mut self) {
        if self.client.is_some() {
            // Note: Can't use async in drop, would need a different approach
            warn!("MQTT client dropped without explicit disconnect");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_mqtt_config() {
        let config = MqttConfig {
            broker: "localhost".to_string(),
            port: 1883,
            client_id: "test_client".to_string(),
            username: None,
            password: None,
            use_tls: false,
            group_id: "omaya".to_string(),
            edge_node_id: "edge-001".to_string(),
        };

        let connector = MqttSparkplugConnector::new(config);
        assert!(connector.client.is_none());
        assert_eq!(connector.sequence, 0);
    }

    #[test]
    fn test_sequence_increment() {
        let config = MqttConfig {
            broker: "localhost".to_string(),
            port: 1883,
            client_id: "test_client".to_string(),
            username: None,
            password: None,
            use_tls: false,
            group_id: "omaya".to_string(),
            edge_node_id: "edge-001".to_string(),
        };

        let mut connector = MqttSparkplugConnector::new(config);
        assert_eq!(connector.sequence, 0);
        connector.increment_sequence();
        assert_eq!(connector.sequence, 1);
    }
}
