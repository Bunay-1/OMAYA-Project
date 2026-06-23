//! OMAYA Edge Connectors - Rust implementation
//! High-performance industrial protocol connectors for edge devices

pub mod modbus_connector;
pub mod mqtt_sparkplug;
pub mod store_forward;

pub use modbus_connector::{ModbusConnector, ModbusConfig, ModbusConnectionType};
pub use mqtt_sparkplug::{MqttSparkplugConnector, MqttConfig, Metric, MetricValue, DataType, SparkplugBPayload};
pub use store_forward::{StoreForwardManager, StoreForwardConfig, BufferedData, TelemetryData, AlertData, EventData, BufferStats};

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        let result = 2 + 2;
        assert_eq!(result, 4);
    }
}
