import json
import uuid
import time
from locust import HttpUser, task, between, events
import websocket
import threading

class OMAYAWebSocketUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.machine_id = f"LOAD-TEST-{uuid.uuid4().hex[:8]}"
        self.ws_url = "ws://localhost:8000/ws/telemetry"
        self.ws = None
        self.ws_thread = None
        self._connect()

    def _connect(self):
        try:
            self.ws = websocket.create_connection(self.ws_url)
            self.ws_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.ws_thread.start()
        except Exception as e:
            events.request.fire(
                request_type="WS_CONNECT",
                name="WebSocket Connect",
                response_time=0,
                response_length=0,
                exception=e
            )

    def _receive_messages(self):
        while self.ws and self.ws.connected:
            try:
                self.ws.recv()
            except Exception:
                break

    @task
    def send_telemetry(self):
        if self.ws and self.ws.connected:
            payload = {
                "machine_id": self.machine_id,
                "temperature": 75.5,
                "vibration": 0.02,
                "timestamp": time.time()
            }
            start_time = time.time()
            try:
                self.ws.send(json.dumps(payload))
                events.request.fire(
                    request_type="WS_SEND",
                    name="WebSocket Telemetry",
                    response_time=(time.time() - start_time) * 1000,
                    response_length=len(json.dumps(payload)),
                )
            except Exception as e:
                events.request.fire(
                    request_type="WS_SEND",
                    name="WebSocket Telemetry",
                    response_time=0,
                    response_length=0,
                    exception=e
                )

    def on_stop(self):
        if self.ws:
            self.ws.close()
