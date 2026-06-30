"""
Database Connection Manager
Handles connections to TimescaleDB (PostgreSQL)
"""
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any, Generator
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL/TimescaleDB connections"""

    def __init__(self):
        self.host = os.getenv("TIMESCALE_HOST", "localhost")
        self.port = os.getenv("TIMESCALE_PORT", "5432")
        self.user = os.getenv("TIMESCALE_USER", "omaya_user")
        self.password = os.getenv("TIMESCALE_PASSWORD", "omaya_password")
        self.dbname = os.getenv("TIMESCALE_DB", "omaya_monitoring")
        self.connection_string = f"host={self.host} port={self.port} user={self.user} password={self.password} dbname={self.dbname}"
        self._conn = None

    def get_connection(self):
        """Get or create database connection"""
        if self._conn is None or self._conn.closed:
            try:
                self._conn = psycopg2.connect(self.connection_string)
                logger.info(f"Connected to database {self.dbname} at {self.host}")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise e
        return self._conn

    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise e
        finally:
            cur.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dicts"""
        with self.get_cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchall()
            return []

    def execute_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute a query and return one result"""
        with self.get_cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchone()
            return None

# Singleton instance
db = DatabaseManager()
