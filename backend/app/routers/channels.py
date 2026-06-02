from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import Channel, WorkspaceMember, User
from app.schemas.schemas import ChannelCreate, ChannelResponse
from app.auth.auth import get_current_user

router = APIRouter(prefix="/channels", tags=["Channels"])

@router.post("/", response_model=ChannelResponse)
def create_channel(
    channel: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user is a member of the workspace
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == channel.workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")

    # Check if channel name already exists in workspace
    existing = db.query(Channel).filter(
        Channel.name == channel.name,
        Channel.workspace_id == channel.workspace_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Channel name already exists")

    new_channel = Channel(
        name=channel.name,
        workspace_id=channel.workspace_id
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    return new_channel

@router.get("/workspace/{workspace_id}", response_model=List[ChannelResponse])
def get_channels(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user is a member of the workspace
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")

    channels = db.query(Channel).filter(
        Channel.workspace_id == workspace_id
    ).all()
    return channels

@router.delete("/{channel_id}")
def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Check if user is owner or admin of the workspace
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == channel.workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()