from sqlalchemy import or_
from app.models.models import Channel
from fastapi import APIRouter, Depends, WebSocket, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import Message, User
from app.schemas.schemas import MessageResponse
from app.auth.auth import get_current_user
from app.websocket.connection import websocket_endpoint

router = APIRouter(tags=["Messages"])

@router.websocket("/ws/channel/{channel_id}")
async def websocket_route(
    websocket: WebSocket,
    channel_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    await websocket_endpoint(websocket, channel_id, token, db)

@router.get("/messages/{channel_id}", response_model=List[MessageResponse])
def get_messages(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        Message.channel_id == channel_id
    ).order_by(Message.created_at.asc()).all()
    return messages

@router.get("/messages/search/{workspace_id}")
def search_messages(
    workspace_id: int,
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Search messages in all channels of a workspace
    results = db.query(Message).join(Channel).filter(
        Channel.workspace_id == workspace_id,
        Message.content.ilike(f"%{q}%")
    ).order_by(Message.created_at.desc()).all()
    
    if not results:
        return {"results": [], "message": "No messages found"}
    
    return {"results": [
        {
            "id": msg.id,
            "content": msg.content,
            "channel_id": msg.channel_id,
            "sender_id": msg.sender_id,
            "created_at": str(msg.created_at)
        } for msg in results
    ]}