from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.models import RoleEnum

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    profile_picture: Optional[str]
    is_online: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChannelCreate(BaseModel):
    name: str
    workspace_id: int

class ChannelResponse(BaseModel):
    id: int
    name: str
    workspace_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str
    channel_id: int

class MessageResponse(BaseModel):
    id: int
    content: str
    channel_id: int
    sender_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MemberRoleUpdate(BaseModel):
    role: RoleEnum

class WorkspaceMemberResponse(BaseModel):
    id: int
    user_id: int
    workspace_id: int
    role: RoleEnum

    class Config:
        from_attributes = True