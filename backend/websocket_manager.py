"""
WebSocket Connection Manager
Handles real-time connections to frontend clients
"""
from fastapi import WebSocket, status
from typing import List, Dict
import json
import time
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.message_counts: Dict[str, List[float]] = {}
        self.rate_limit = 50  # messages per minute
        self.rate_window = 60  # seconds

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    def check_rate_limit(self, client_id: str) -> bool:
        """
        Simple rate limiting for incoming WebSocket messages
        """
        now = time.time()
        if client_id not in self.message_counts:
            self.message_counts[client_id] = []

        # Remove old timestamps
        self.message_counts[client_id] = [
            t for t in self.message_counts[client_id]
            if now - t < self.rate_window
        ]

        if len(self.message_counts[client_id]) >= self.rate_limit:
            return False

        self.message_counts[client_id].append(now)
        return True

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
