"""
LAN Chat Server
================
A minimal WebSocket-based chat server for local network communication.
Run with: python server.py
    or:   uvicorn server:app --host 0.0.0.0 --port 8000
"""

import json
import logging
import socket
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lan-chat")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HOST = "0.0.0.0"
PORT = 8000

# ---------------------------------------------------------------------------
# Connection manager
# ---------------------------------------------------------------------------

class ConnectionManager:
    """Keeps track of active WebSocket connections and broadcasts messages."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            "Client connected  (%s)  — %d active",
            websocket.client.host if websocket.client else "unknown",
            len(self.active_connections),
        )

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(
            "Client disconnected — %d active", len(self.active_connections)
        )

    async def broadcast(self, message: str):
        """Send a message to every connected client.

        Connections that fail during send are silently removed so the
        server never crashes because of a stale socket.
        """
        stale: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


manager = ConnectionManager()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_lan_ip() -> str:
    """Return the best-guess LAN IP of the host machine."""
    try:
        # Open a UDP socket to an external address (no data is sent).
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    ip = get_lan_ip()
    logger.info("=" * 50)
    logger.info("  LAN Chat Server started")
    logger.info("  Local:   http://127.0.0.1:%d", PORT)
    logger.info("  Network: http://%s:%d", ip, PORT)
    logger.info("=" * 50)
    print(f"\n  Open in browser:  http://{ip}:{PORT}\n")
    yield
    logger.info("Server shutting down")

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(title="LAN Chat", lifespan=lifespan)

# Static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the chat page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle a single WebSocket connection for the lifetime of the client."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            # Validate incoming JSON
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue

            # Handle heartbeat pings from the client
            if payload.get("type") == "ping":
                try:
                    await websocket.send_text(json.dumps({"type": "pong"}))
                except Exception:
                    break
                continue

            # Regular chat message — attach a server timestamp and broadcast
            outgoing = {
                "type": "message",
                "text": payload.get("text", ""),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
            await manager.broadcast(json.dumps(outgoing))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        logger.exception("Unexpected error on WebSocket: %s", exc)
        manager.disconnect(websocket)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=HOST, port=PORT, log_level="info")
