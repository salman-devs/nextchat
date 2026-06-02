from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # {channel_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # {user_id: websocket}
        self.user_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, channel_id: int, user_id: int):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        
        # Remove any existing connection for this user in this channel
        if user_id in self.user_connections:
            old_ws = self.user_connections[user_id]
            if old_ws in self.active_connections.get(channel_id, []):
                self.active_connections[channel_id].remove(old_ws)

        self.active_connections[channel_id].append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, channel_id: int, user_id: int):
        if channel_id in self.active_connections:
            self.active_connections[channel_id].remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def broadcast_to_channel(self, message: dict, channel_id: int):
        if channel_id in self.active_connections:
            for connection in self.active_connections[channel_id]:
                await connection.send_json(message)

    async def broadcast_online_status(self, user_id: int, is_online: bool):
        message = {
            "event": "online_status",
            "user_id": user_id,
            "is_online": is_online
        }
        # Broadcast to all connected users
        for websocket in self.user_connections.values():
            await websocket.send_json(message)

manager = ConnectionManager()