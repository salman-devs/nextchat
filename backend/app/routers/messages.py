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