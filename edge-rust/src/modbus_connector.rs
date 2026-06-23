//! Rust Modbus TCP/RTU Connector for OMAYA Edge
//! High-performance Modbus implementation for edge devices

use anyhow::{Context, Result};
use bytes::Bytes;
use log::{debug, error, info, warn};
use modbus::{prelude::*, Client};
use serde::{Deserialize, Serialize};
use std::time::Duration;

/// Modbus connector configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModbusConfig {
    /// Connection type (TCP or RTU)
    pub connection_type: ModbusConnectionType,
    /// Host address for TCP
    pub host: Option<String>,
    /// Port for TCP
    pub port: Option<u16>,
    /// Serial port for RTU
    pub serial_port: Option<String>,
    /// Baud rate for RTU
    pub baud_rate: Option<u32>,
    /// Slave ID
    pub slave_id: u8,
    /// Timeout in milliseconds
    pub timeout_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ModbusConnectionType {
    TCP,
    RTU,
}

/// Modbus connector implementation
pub struct ModbusConnector {
    config: ModbusConfig,
    client: Option<Client>,
}

impl ModbusConnector {
    /// Create a new Modbus connector
    pub fn new(config: ModbusConfig) -> Self {
        Self {
            config,
            client: None,
        }
    }

    /// Connect to Modbus device
    pub async fn connect(&mut self) -> Result<()> {
        info!("Connecting to Modbus device...");

        let timeout = Duration::from_millis(self.config.timeout_ms);

        let client = match &self.config.connection_type {
            ModbusConnectionType::TCP => {
                let host = self.config.host.as_ref().context("Host required for TCP")?;
                let port = self.config.port.context("Port required for TCP")?;
                debug!("Connecting to TCP {}:{}", host, port);
                Client::tcp_connect(host, *port).await?
            }
            ModbusConnectionType::RTU => {
                let port = self.config.serial_port.as_ref().context("Serial port required for RTU")?;
                let baud = self.config.baud_rate.context("Baud rate required for RTU")?;
                debug!("Connecting to RTU {} at {} baud", port, baud);
                Client::rtu_connect(port, *baud).await?
            }
        };

        self.client = Some(client);
        info!("Connected to Modbus device");
        Ok(())
    }

    /// Disconnect from Modbus device
    pub fn disconnect(&mut self) -> Result<()> {
        if let Some(client) = self.client.take() {
            info!("Disconnecting from Modbus device");
            // Client will be dropped here
        }
        Ok(())
    }

    /// Read holding registers
    pub async fn read_holding_registers(&self, address: u16, count: u16) -> Result<Vec<u16>> {
        let client = self.client.as_ref().context("Not connected")?;
        let result = client
            .read_holding_registers(self.config.slave_id, address, count)
            .await?;
        debug!("Read {} holding registers from {}", count, address);
        Ok(result)
    }

    /// Read input registers
    pub async fn read_input_registers(&self, address: u16, count: u16) -> Result<Vec<u16>> {
        let client = self.client.as_ref().context("Not connected")?;
        let result = client
            .read_input_registers(self.config.slave_id, address, count)
            .await?;
        debug!("Read {} input registers from {}", count, address);
        Ok(result)
    }

    /// Read coils
    pub async fn read_coils(&self, address: u16, count: u16) -> Result<Vec<bool>> {
        let client = self.client.as_ref().context("Not connected")?;
        let result = client.read_coils(self.config.slave_id, address, count).await?;
        debug!("Read {} coils from {}", count, address);
        Ok(result)
    }

    /// Read discrete inputs
    pub async fn read_discrete_inputs(&self, address: u16, count: u16) -> Result<Vec<bool>> {
        let client = self.client.as_ref().context("Not connected")?;
        let result = client
            .read_discrete_inputs(self.config.slave_id, address, count)
            .await?;
        debug!("Read {} discrete inputs from {}", count, address);
        Ok(result)
    }

    /// Write single register
    pub async fn write_single_register(&self, address: u16, value: u16) -> Result<()> {
        let client = self.client.as_ref().context("Not connected")?;
        client
            .write_single_register(self.config.slave_id, address, value)
            .await?;
        debug!("Wrote register {} = {}", address, value);
        Ok(())
    }

    /// Write multiple registers
    pub async fn write_multiple_registers(&self, address: u16, values: &[u16]) -> Result<()> {
        let client = self.client.as_ref().context("Not connected")?;
        client
            .write_multiple_registers(self.config.slave_id, address, values)
            .await?;
        debug!("Wrote {} registers starting at {}", values.len(), address);
        Ok(())
    }

    /// Write single coil
    pub async fn write_single_coil(&self, address: u16, value: bool) -> Result<()> {
        let client = self.client.as_ref().context("Not connected")?;
        client
            .write_single_coil(self.config.slave_id, address, value)
            .await?;
        debug!("Wrote coil {} = {}", address, value);
        Ok(())
    }

    /// Read float from two registers (big-endian)
    pub async fn read_float(&self, address: u16) -> Result<f32> {
        let registers = self.read_holding_registers(address, 2).await?;
        let bytes: [u8; 4] = [
            (registers[0] >> 8) as u8,
            registers[0] as u8,
            (registers[1] >> 8) as u8,
            registers[1] as u8,
        ];
        let value = f32::from_be_bytes(bytes);
        debug!("Read float {} from {}", value, address);
        Ok(value)
    }

    /// Write float to two registers (big-endian)
    pub async fn write_float(&self, address: u16, value: f32) -> Result<()> {
        let bytes = value.to_be_bytes();
        let registers = vec![
            u16::from_be_bytes([bytes[0], bytes[1]]),
            u16::from_be_bytes([bytes[2], bytes[3]]),
        ];
        self.write_multiple_registers(address, &registers).await
    }

    /// Read int32 from two registers (big-endian)
    pub async fn read_int32(&self, address: u16) -> Result<i32> {
        let registers = self.read_holding_registers(address, 2).await?;
        let bytes: [u8; 4] = [
            (registers[0] >> 8) as u8,
            registers[0] as u8,
            (registers[1] >> 8) as u8,
            registers[1] as u8,
        ];
        let value = i32::from_be_bytes(bytes);
        debug!("Read int32 {} from {}", value, address);
        Ok(value)
    }

    /// Write int32 to two registers (big-endian)
    pub async fn write_int32(&self, address: u16, value: i32) -> Result<()> {
        let bytes = value.to_be_bytes();
        let registers = vec![
            u16::from_be_bytes([bytes[0], bytes[1]]),
            u16::from_be_bytes([bytes[2], bytes[3]]),
        ];
        self.write_multiple_registers(address, &registers).await
    }
}

impl Drop for ModbusConnector {
    fn drop(&mut self) {
        if self.client.is_some() {
            let _ = self.disconnect();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_modbus_config() {
        let config = ModbusConfig {
            connection_type: ModbusConnectionType::TCP,
            host: Some("127.0.0.1".to_string()),
            port: Some(502),
            serial_port: None,
            baud_rate: None,
            slave_id: 1,
            timeout_ms: 1000,
        };

        let connector = ModbusConnector::new(config);
        assert!(connector.client.is_none());
    }
}
