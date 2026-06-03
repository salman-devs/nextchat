from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
import uuid
class RoleEnum(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    is_online = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspaces = relationship("WorkspaceMember", back_populates="user")
    messages = relationship("Message", back_populates="sender")

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User")
    members = relationship("WorkspaceMember", back_populates="workspace")
    channels = relationship("Channel", back_populates="workspace")
    invite_code = Column(String, unique=True, default=lambda: str(uuid.uuid4())[:8].upper())

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(Enum(RoleEnum), default=RoleEnum.member)

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspaces")

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("Workspace", back_populates="channels")
    messages = relationship("Message", back_populates="channel")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    channel = relationship("Channel", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    files = relationship("File", back_populates="message")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String, nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("Message", back_populates="files")