"""WebSocket connection manager"""
from fastapi import WebSocket
from typing import Dict, Set, Any
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store connections by room/channel
        self.rooms: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register new connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"Client {user_id} connected. Total connections: {self.get_total_connections()}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from all rooms
        for room in self.rooms.values():
            room.discard(websocket)
        
        logger.info(f"Client {user_id} disconnected. Total connections: {self.get_total_connections()}")
    
    async def send_personal_message(self, message: Any, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            message_json = json.dumps(message)
            
            # Send to all connections of this user
            disconnected = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.active_connections[user_id].discard(ws)
    
    async def broadcast(self, message: Any, exclude: Set[WebSocket] = None):
        """Broadcast message to all connected clients"""
        message_json = json.dumps(message)
        exclude = exclude or set()
        
        disconnected = set()
        
        for user_connections in self.active_connections.values():
            for websocket in user_connections:
                if websocket not in exclude:
                    try:
                        await websocket.send_text(message_json)
                    except Exception as e:
                        logger.error(f"Error broadcasting message: {e}")
                        disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            for user_id, connections in self.active_connections.items():
                connections.discard(ws)
    
    async def join_room(self, websocket: WebSocket, room: str):
        """Add connection to a room"""
        if room not in self.rooms:
            self.rooms[room] = set()
        
        self.rooms[room].add(websocket)
        logger.info(f"Client joined room: {room}")
    
    async def leave_room(self, websocket: WebSocket, room: str):
        """Remove connection from a room"""
        if room in self.rooms:
            self.rooms[room].discard(websocket)
            
            if not self.rooms[room]:
                del self.rooms[room]
        
        logger.info(f"Client left room: {room}")
    
    async def broadcast_to_room(self, message: Any, room: str):
        """Broadcast message to all clients in a room"""
        if room not in self.rooms:
            return
        
        message_json = json.dumps(message)
        
        disconnected = set()
        
        for websocket in self.rooms[room]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to room {room}: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.rooms[room].discard(ws)
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_user_connections(self, user_id: str) -> int:
        """Get number of connections for a specific user"""
        return len(self.active_connections.get(user_id, set()))

