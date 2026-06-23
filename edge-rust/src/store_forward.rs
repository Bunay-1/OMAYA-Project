//! Rust Store-and-Forward for OMAYA Edge
//! Local SQLite buffering for offline operation

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use log::{debug, error, info, warn};
use serde::{Deserialize, Serialize};
use sqlx::{SqlitePool, Row};
use std::path::Path;

/// Store-and-Forward configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StoreForwardConfig {
    /// Database file path
    pub db_path: String,
    /// Maximum buffer size (number of records)
    pub max_buffer_size: usize,
    /// Maximum age of records (in seconds)
    pub max_age_seconds: i64,
}

/// Data type for buffered records
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BufferedData {
    Telemetry(TelemetryData),
    Alert(AlertData),
    Event(EventData),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryData {
    pub machine_id: String,
    pub timestamp: DateTime<Utc>,
    pub data: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlertData {
    pub machine_id: String,
    pub alert_type: String,
    pub severity: String,
    pub message: String,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventData {
    pub machine_id: String,
    pub event_type: String,
    pub description: String,
    pub timestamp: DateTime<Utc>,
}

/// Store-and-Forward manager
pub struct StoreForwardManager {
    config: StoreForwardConfig,
    pool: SqlitePool,
}

impl StoreForwardManager {
    /// Create a new Store-and-Forward manager
    pub async fn new(config: StoreForwardConfig) -> Result<Self> {
        info!("Initializing Store-and-Forward with database: {}", config.db_path);

        // Ensure parent directory exists
        if let Some(parent) = Path::new(&config.db_path).parent() {
            std::fs::create_dir_all(parent)?;
        }

        let pool = SqlitePool::connect(&format!("sqlite:{}", config.db_path)).await?;

        let manager = Self { config, pool };
        manager.initialize_tables().await?;

        info!("Store-and-Forward initialized");
        Ok(manager)
    }

    /// Initialize database tables
    async fn initialize_tables(&self) -> Result<()> {
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL,
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // Create indexes
        sqlx::query("CREATE INDEX IF NOT EXISTS idx_telemetry_synced ON telemetry(synced)")
            .execute(&self.pool)
            .await?;

        sqlx::query("CREATE INDEX IF NOT EXISTS idx_alerts_synced ON alerts(synced)")
            .execute(&self.pool)
            .await?;

        sqlx::query("CREATE INDEX IF NOT EXISTS idx_events_synced ON events(synced)")
            .execute(&self.pool)
            .await?;

        Ok(())
    }

    /// Store telemetry data
    pub async fn store_telemetry(&self, data: TelemetryData) -> Result<i64> {
        let data JSON = serde_json::to_string(&data.data)?;
        let timestamp = data.timestamp.to_rfc3339();

        let result = sqlx::query(
            r#"
            INSERT INTO telemetry (machine_id, timestamp, data)
            VALUES (?, ?, ?)
            "#,
        )
        .bind(&data.machine_id)
        .bind(&timestamp)
        .bind(&data)
        .execute(&self.pool)
        .await?;

        let id = result.last_insert_rowid();
        debug!("Stored telemetry with ID {}", id);
        Ok(id)
    }

    /// Store alert data
    pub async fn store_alert(&self, data: AlertData) -> Result<i64> {
        let timestamp = data.timestamp.to_rfc3339();

        let result = sqlx::query(
            r#"
            INSERT INTO alerts (machine_id, alert_type, severity, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
            "#,
        )
        .bind(&data.machine_id)
        .bind(&data.alert_type)
        .bind(&data.severity)
        .bind(&data.message)
        .bind(&timestamp)
        .execute(&self.pool)
        .await?;

        let id = result.last_insert_rowid();
        debug!("Stored alert with ID {}", id);
        Ok(id)
    }

    /// Store event data
    pub async fn store_event(&self, data: EventData) -> Result<i64> {
        let timestamp = data.timestamp.to_rfc3339();

        let result = sqlx::query(
            r#"
            INSERT INTO events (machine_id, event_type, description, timestamp)
            VALUES (?, ?, ?, ?)
            "#,
        )
        .bind(&data.machine_id)
        .bind(&data.event_type)
        .bind(&data.description)
        .bind(&timestamp)
        .execute(&self.pool)
        .await?;

        let id = result.last_insert_rowid();
        debug!("Stored event with ID {}", id);
        Ok(id)
    }

    /// Get unsynced telemetry records
    pub async fn get_unsynced_telemetry(&self, limit: usize) -> Result<Vec<TelemetryData>> {
        let rows = sqlx::query(
            r#"
            SELECT machine_id, timestamp, data
            FROM telemetry
            WHERE synced = 0
            ORDER BY created_at ASC
            LIMIT ?
            "#,
        )
        .bind(limit as i64)
        .fetch_all(&self.pool)
        .await?;

        let mut results = Vec::new();
        for row in rows {
            let machine_id: String = row.get("machine_id");
            let timestamp_str: String = row.get("timestamp");
            let data_str: String = row.get("data");
            let data: serde_json::Value = serde_json::from_str(&data_str)?;
            let timestamp = DateTime::parse_from_rfc3339(&timestamp_str)?.with_timezone(&Utc);

            results.push(TelemetryData {
                machine_id,
                timestamp,
                data,
            });
        }

        debug!("Retrieved {} unsynced telemetry records", results.len());
        Ok(results)
    }

    /// Mark telemetry as synced
    pub async fn mark_telemetry_synced(&self, ids: &[i64]) -> Result<()> {
        if ids.is_empty() {
            return Ok(());
        }

        let query = format!(
            "UPDATE telemetry SET synced = 1 WHERE id IN ({})",
            ids.iter()
                .map(|_| "?")
                .collect::<Vec<_>>()
                .join(",")
        );

        let mut query_builder = sqlx::query(&query);
        for id in ids {
            query_builder = query_builder.bind(id);
        }

        query_builder.execute(&self.pool).await?;
        debug!("Marked {} telemetry records as synced", ids.len());
        Ok(())
    }

    /// Get buffer statistics
    pub async fn get_stats(&self) -> Result<BufferStats> {
        let telemetry_count: i64 = sqlx::query("SELECT COUNT(*) FROM telemetry WHERE synced = 0")
            .fetch_one(&self.pool)
            .await?
            .get(0);

        let alerts_count: i64 = sqlx::query("SELECT COUNT(*) FROM alerts WHERE synced = 0")
            .fetch_one(&self.pool)
            .await?
            .get(0);

        let events_count: i64 = sqlx::query("SELECT COUNT(*) FROM events WHERE synced = 0")
            .fetch_one(&self.pool)
            .await?
            .get(0);

        Ok(BufferStats {
            unsynced_telemetry: telemetry_count as usize,
            unsynced_alerts: alerts_count as usize,
            unsynced_events: events_count as usize,
        })
    }

    /// Clean up old synced records
    pub async fn cleanup_old_records(&self) -> Result<usize> {
        let cutoff = Utc::now() - chrono::Duration::seconds(self.config.max_age_seconds);
        let cutoff_str = cutoff.to_rfc3339();

        let result = sqlx::query(
            r#"
            DELETE FROM telemetry WHERE synced = 1 AND created_at < ?
            "#,
        )
        .bind(&cutoff_str)
        .execute(&self.pool)
        .await?;

        let deleted = result.rows_affected();
        info!("Cleaned up {} old telemetry records", deleted);
        Ok(deleted as usize)
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BufferStats {
    pub unsynced_telemetry: usize,
    pub unsynced_alerts: usize,
    pub unsynced_events: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[tokio::test]
    async fn test_store_forward_init() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("test.db").to_str().unwrap().to_string();

        let config = StoreForwardConfig {
            db_path,
            max_buffer_size: 1000,
            max_age_seconds: 86400,
        };

        let manager = StoreForwardManager::new(config).await.unwrap();
        let stats = manager.get_stats().await.unwrap();

        assert_eq!(stats.unsynced_telemetry, 0);
        assert_eq!(stats.unsynced_alerts, 0);
        assert_eq!(stats.unsynced_events, 0);
    }
}
