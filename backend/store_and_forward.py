"""
Store-and-Forward Mechanism for OMAYA Platform
Local buffering for edge devices during connectivity loss.
"""
from typing import Dict, Any, Optional, List
import logging
import sqlite3
import json
import threading
from datetime import datetime
from pathlib import Path
import asyncio
from queue import Queue

logger = logging.getLogger(__name__)

class StoreAndForward:
    """
    Store-and-Forward mechanism for edge devices
    Buffers data locally during connectivity loss and syncs when connection restored
    """
    
    def __init__(self, db_path: str = "edge_buffer.db", max_buffer_size: int = 100000):
        """
        Initialize Store-and-Forward buffer.
        
        Args:
            db_path: Path to SQLite database file
            max_buffer_size: Maximum number of records to buffer
        """
        self.db_path = db_path
        self.max_buffer_size = max_buffer_size
        self.connection = None
        self.lock = threading.Lock()
        self.sync_queue = Queue()
        self.is_syncing = False
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database schema."""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            cursor = self.connection.cursor()
            
            # Create telemetry buffer table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_buffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    machine_id TEXT NOT NULL,
                    data JSON NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    synced BOOLEAN DEFAULT FALSE,
                    sync_attempts INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)
            
            # Create alerts buffer table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts_buffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    machine_id TEXT NOT NULL,
                    alert_data JSON NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    synced BOOLEAN DEFAULT FALSE,
                    sync_attempts INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)
            
            # Create events buffer table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events_buffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data JSON NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    synced BOOLEAN DEFAULT FALSE,
                    sync_attempts INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_telemetry_synced 
                ON telemetry_buffer(synced, timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_synced 
                ON alerts_buffer(synced, timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_synced 
                ON events_buffer(synced, timestamp)
            """)
            
            self.connection.commit()
            logger.info(f"Store-and-Forward database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def store_telemetry(self, machine_id: str, data: Dict[str, Any]) -> bool:
        """
        Store telemetry data in local buffer.
        
        Args:
            machine_id: Machine identifier
            data: Telemetry data dictionary
            
        Returns:
            True on success, False on error
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                
                # Check buffer size
                cursor.execute("SELECT COUNT(*) FROM telemetry_buffer WHERE synced = FALSE")
                count = cursor.fetchone()[0]
                
                if count >= self.max_buffer_size:
                    logger.warning(f"Telemetry buffer full ({count} records). Oldest records will be purged.")
                    self._purge_old_records('telemetry_buffer', int(self.max_buffer_size * 0.1))
                
                cursor.execute("""
                    INSERT INTO telemetry_buffer (machine_id, data, synced)
                    VALUES (?, ?, FALSE)
                """, (machine_id, json.dumps(data)))
                
                self.connection.commit()
                logger.debug(f"Stored telemetry for machine {machine_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error storing telemetry: {e}")
                return False
    
    def store_alert(self, machine_id: str, alert_data: Dict[str, Any]) -> bool:
        """
        Store alert in local buffer.
        
        Args:
            machine_id: Machine identifier
            alert_data: Alert data dictionary
            
        Returns:
            True on success, False on error
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                
                # Check buffer size
                cursor.execute("SELECT COUNT(*) FROM alerts_buffer WHERE synced = FALSE")
                count = cursor.fetchone()[0]
                
                if count >= self.max_buffer_size:
                    logger.warning(f"Alerts buffer full ({count} records). Oldest records will be purged.")
                    self._purge_old_records('alerts_buffer', int(self.max_buffer_size * 0.1))
                
                cursor.execute("""
                    INSERT INTO alerts_buffer (machine_id, alert_data, synced)
                    VALUES (?, ?, FALSE)
                """, (machine_id, json.dumps(alert_data)))
                
                self.connection.commit()
                logger.debug(f"Stored alert for machine {machine_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error storing alert: {e}")
                return False
    
    def store_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Store event in local buffer.
        
        Args:
            event_type: Type of event
            event_data: Event data dictionary
            
        Returns:
            True on success, False on error
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                
                # Check buffer size
                cursor.execute("SELECT COUNT(*) FROM events_buffer WHERE synced = FALSE")
                count = cursor.fetchone()[0]
                
                if count >= self.max_buffer_size:
                    logger.warning(f"Events buffer full ({count} records). Oldest records will be purged.")
                    self._purge_old_records('events_buffer', int(self.max_buffer_size * 0.1))
                
                cursor.execute("""
                    INSERT INTO events_buffer (event_type, event_data, synced)
                    VALUES (?, ?, FALSE)
                """, (event_type, json.dumps(event_data)))
                
                self.connection.commit()
                logger.debug(f"Stored event of type {event_type}")
                return True
                
            except Exception as e:
                logger.error(f"Error storing event: {e}")
                return False
    
    def _purge_old_records(self, table: str, limit: int):
        """Purge oldest unsynced records from buffer."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                DELETE FROM {table}
                WHERE id IN (
                    SELECT id FROM {table}
                    WHERE synced = FALSE
                    ORDER BY timestamp ASC
                    LIMIT ?
                )
            """, (limit,))
            self.connection.commit()
            logger.info(f"Purged {limit} old records from {table}")
        except Exception as e:
            logger.error(f"Error purging records: {e}")
    
    def get_unsynced_telemetry(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get unsynced telemetry records.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of telemetry records
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT id, machine_id, data, timestamp
                    FROM telemetry_buffer
                    WHERE synced = FALSE
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (limit,))
                
                records = []
                for row in cursor.fetchall():
                    records.append({
                        'id': row['id'],
                        'machine_id': row['machine_id'],
                        'data': json.loads(row['data']),
                        'timestamp': row['timestamp']
                    })
                
                return records
                
            except Exception as e:
                logger.error(f"Error getting unsynced telemetry: {e}")
                return []
    
    def get_unsynced_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get unsynced alert records.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of alert records
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT id, machine_id, alert_data, timestamp
                    FROM alerts_buffer
                    WHERE synced = FALSE
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (limit,))
                
                records = []
                for row in cursor.fetchall():
                    records.append({
                        'id': row['id'],
                        'machine_id': row['machine_id'],
                        'alert_data': json.loads(row['alert_data']),
                        'timestamp': row['timestamp']
                    })
                
                return records
                
            except Exception as e:
                logger.error(f"Error getting unsynced alerts: {e}")
                return []
    
    def get_unsynced_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get unsynced event records.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of event records
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT id, event_type, event_data, timestamp
                    FROM events_buffer
                    WHERE synced = FALSE
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (limit,))
                
                records = []
                for row in cursor.fetchall():
                    records.append({
                        'id': row['id'],
                        'event_type': row['event_type'],
                        'event_data': json.loads(row['event_data']),
                        'timestamp': row['timestamp']
                    })
                
                return records
                
            except Exception as e:
                logger.error(f"Error getting unsynced events: {e}")
                return []
    
    def mark_as_synced(self, table: str, record_ids: List[int]) -> bool:
        """
        Mark records as synced.
        
        Args:
            table: Table name
            record_ids: List of record IDs to mark as synced
            
        Returns:
            True on success, False on error
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                
                placeholders = ','.join(['?'] * len(record_ids))
                cursor.execute(f"""
                    UPDATE {table}
                    SET synced = TRUE, sync_attempts = sync_attempts + 1
                    WHERE id IN ({placeholders})
                """, record_ids)
                
                self.connection.commit()
                logger.info(f"Marked {len(record_ids)} records as synced in {table}")
                return True
                
            except Exception as e:
                logger.error(f"Error marking records as synced: {e}")
                return False
    
    def mark_sync_failed(self, table: str, record_id: int, error_message: str) -> bool:
        """
        Mark a record as failed to sync.
        
        Args:
            table: Table name
            record_id: Record ID
            error_message: Error message
            
        Returns:
            True on success, False on error
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"""
                    UPDATE {table}
                    SET sync_attempts = sync_attempts + 1, error_message = ?
                    WHERE id = ?
                """, (error_message, record_id))
                
                self.connection.commit()
                return True
                
            except Exception as e:
                logger.error(f"Error marking sync failure: {e}")
                return False
    
    def get_buffer_stats(self) -> Dict[str, Any]:
        """
        Get buffer statistics.
        
        Returns:
            Dictionary with buffer statistics
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                
                stats = {
                    'telemetry': {},
                    'alerts': {},
                    'events': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Telemetry stats
                cursor.execute("SELECT COUNT(*) FROM telemetry_buffer WHERE synced = FALSE")
                stats['telemetry']['unsynced'] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM telemetry_buffer WHERE synced = TRUE")
                stats['telemetry']['synced'] = cursor.fetchone()[0]
                
                # Alerts stats
                cursor.execute("SELECT COUNT(*) FROM alerts_buffer WHERE synced = FALSE")
                stats['alerts']['unsynced'] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM alerts_buffer WHERE synced = TRUE")
                stats['alerts']['synced'] = cursor.fetchone()[0]
                
                # Events stats
                cursor.execute("SELECT COUNT(*) FROM events_buffer WHERE synced = FALSE")
                stats['events']['unsynced'] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM events_buffer WHERE synced = TRUE")
                stats['events']['synced'] = cursor.fetchone()[0]
                
                return stats
                
            except Exception as e:
                logger.error(f"Error getting buffer stats: {e}")
                return {}
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """
        Clean up old synced records.
        
        Args:
            days: Number of days to keep records
            
        Returns:
            Number of records deleted
        """
        with self.lock:
            try:
                cursor = self.connection.cursor()
                
                total_deleted = 0
                
                for table in ['telemetry_buffer', 'alerts_buffer', 'events_buffer']:
                    cursor.execute(f"""
                        DELETE FROM {table}
                        WHERE synced = TRUE AND timestamp < datetime('now', '-{days} days')
                    """)
                    deleted = cursor.rowcount
                    total_deleted += deleted
                    logger.info(f"Deleted {deleted} old records from {table}")
                
                self.connection.commit()
                return total_deleted
                
            except Exception as e:
                logger.error(f"Error cleaning up old records: {e}")
                return 0
    
    def clear_all_data(self) -> bool:
        """Clear all buffered data (use with caution)."""
        with self.lock:
            try:
                cursor = self.connection.cursor()
                
                for table in ['telemetry_buffer', 'alerts_buffer', 'events_buffer']:
                    cursor.execute(f"DELETE FROM {table}")
                
                self.connection.commit()
                logger.warning("All buffered data cleared")
                return True
                
            except Exception as e:
                logger.error(f"Error clearing data: {e}")
                return False
    
    def close(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Store-and-Forward database closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
