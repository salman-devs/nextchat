from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import Workspace, WorkspaceMember, RoleEnum, User
from app.schemas.schemas import WorkspaceCreate, WorkspaceResponse
from app.auth.auth import get_current_user
from app.schemas.schemas import MemberRoleUpdate

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.post("/", response_model=WorkspaceResponse)
def create_workspace(
    workspace: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create workspace
    new_workspace = Workspace(
        name=workspace.name,
        owner_id=current_user.id
    )
    db.add(new_workspace)
    db.commit()
    db.refresh(new_workspace)

    # Add creator as owner member
    member = WorkspaceMember(
        workspace_id=new_workspace.id,
        user_id=current_user.id,
        role=RoleEnum.owner
    )
    db.add(member)
    db.commit()

    return new_workspace

@router.get("/", response_model=List[WorkspaceResponse])
def get_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all workspaces where user is a member
    workspaces = db.query(Workspace).join(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).all()
    return workspaces

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Only owner can delete
    if workspace.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete workspace")
    
    db.delete(workspace)
    db.commit()
    return {"message": "Workspace deleted successfully"}

@router.post("/{workspace_id}/join")
def join_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if already a member
    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already a member")

    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=current_user.id,
        role=RoleEnum.member
    )
    db.add(member)
    db.commit()
    return {"message": "Joined workspace successfully"}

@router.get("/{workspace_id}/members")
def get_workspace_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is member
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="You are not a member of this workspace")

    members = db.query(WorkspaceMember, User).join(
        User, WorkspaceMember.user_id == User.id
    ).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).all()

    return [
        {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": member.role,
            "is_online": user.is_online
        }
        for member, user in members
    ]

@router.patch("/{workspace_id}/members/{user_id}/role")
def update_member_role(
    workspace_id: int,
    user_id: int,
    role_update: MemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is owner
    current_member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not current_member or current_member.role != RoleEnum.owner:
        raise HTTPException(status_code=403, detail="Only owner can update roles")

    # Find target member
    target_member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    if not target_member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Owner cannot be demoted
    if target_member.role == RoleEnum.owner:
        raise HTTPException(status_code=400, detail="Cannot change owner's role")

    target_member.role = role_update.role
    db.commit()
    return {"message": f"Role updated to {role_update.role}"}

@router.delete("/{workspace_id}/members/{user_id}")
def remove_member(
    workspace_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is owner or admin
    current_member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not current_member or current_member.role not in [RoleEnum.owner, RoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Find target member
    target_member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    if not target_member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Cannot remove owner
    if target_member.role == RoleEnum.owner:
        raise HTTPException(status_code=400, detail="Cannot remove workspace owner")

    db.delete(target_member)
    db.commit()
    return {"message": "Member removed successfully"}