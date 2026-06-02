from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Message, User
from app.websocket.manager import manager
from app.auth.auth import get_current_user
from jose import jwt, JWTError
from app.config import settings

async def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        user = db.query(User).filter(User.email == email).first()
        return user
    except JWTError:
        return None

async def websocket_endpoint(websocket: WebSocket, channel_id: int, token: str, db: Session):
    # Authenticate user
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008)
        return

    # Connect
    await manager.connect(websocket, channel_id, user.id)

    # Set user online
    user.is_online = True
    db.commit()
    await manager.broadcast_online_status(user.id, True)

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")

            if event == "message":
                # Save message to database
                new_message = Message(
                    content=data["content"],
                    channel_id=channel_id,
                    sender_id=user.id
                )
                db.add(new_message)
                db.commit()
                db.refresh(new_message)

                # Broadcast to channel
                await manager.broadcast_to_channel({
                    "event": "message",
                    "id": new_message.id,
                    "content": new_message.content,
                    "channel_id": channel_id,
                    "sender_id": user.id,
                    "username": user.username,
                    "created_at": str(new_message.created_at)
                }, channel_id)

            elif event == "typing":
                # Broadcast typing indicator
                await manager.broadcast_to_channel({
                    "event": "typing",
                    "user_id": user.id,
                    "username": user.username,
                    "is_typing": data.get("is_typing", False)
                }, channel_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id, user.id)
        # Set user offline
        user.is_online = False
        db.commit()
        await manager.broadcast_online_status(user.id, False)