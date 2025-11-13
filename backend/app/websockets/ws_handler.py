"""WebSocket endpoint handler"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
import json
import logging
from typing import Optional

from app.websockets.manager import ConnectionManager
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()
manager = ConnectionManager()


async def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Authenticate user from JWT token"""
    try:
        payload = decode_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        logger.error(f"Error authenticating WebSocket: {e}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time data streaming
    
    Query parameters:
    - token: JWT access token for authentication
    
    Message format (JSON):
    {
        "type": "subscribe|unsubscribe|message",
        "channel": "sensors|machines|production|energy",
        "data": {...}
    }
    """
    # Authenticate user
    user = await get_user_from_token(token, db)
    
    if not user:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    user_id = str(user.id)
    
    # Accept connection
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Genesis Twin WebSocket",
            "user": user.username
        })
        
        # Message loop
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "subscribe":
                    # Subscribe to a channel
                    channel = message.get("channel")
                    if channel:
                        await manager.join_room(websocket, channel)
                        await websocket.send_json({
                            "type": "subscribed",
                            "channel": channel
                        })
                
                elif message_type == "unsubscribe":
                    # Unsubscribe from a channel
                    channel = message.get("channel")
                    if channel:
                        await manager.leave_room(websocket, channel)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "channel": channel
                        })
                
                elif message_type == "ping":
                    # Heartbeat
                    await websocket.send_json({"type": "pong"})
                
                elif message_type == "message":
                    # Echo message back (can be extended for chat, commands, etc.)
                    await websocket.send_json({
                        "type": "message",
                        "data": message.get("data"),
                        "user": user.username
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
            
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Error processing message"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"Client {user_id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)

