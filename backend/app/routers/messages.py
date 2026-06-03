import os
import uuid
from fastapi import File, UploadFile
import aiofiles
from app.models.models import File as FileModel
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
@router.post("/upload/{channel_id}")
async def upload_file(
    channel_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = f"uploads/{unique_filename}"

    # Save file to disk
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Save message with file
    new_message = Message(
        content=f"📎 {file.filename}",
        channel_id=channel_id,
        sender_id=current_user.id
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    # Save file record
    new_file = FileModel(
        file_url=file_path,
        message_id=new_message.id
    )
    db.add(new_file)
    db.commit()

    # Broadcast to channel
    from app.websocket.manager import manager
    await manager.broadcast_to_channel({
        "event": "message",
        "id": new_message.id,
        "content": new_message.content,
        "channel_id": channel_id,
        "sender_id": current_user.id,
        "username": current_user.username,
        "file_url": file_path,
        "created_at": str(new_message.created_at)
    }, channel_id)

    return {
        "message": "File uploaded successfully",
        "file_url": file_path,
        "filename": file.filename
    }