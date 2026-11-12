from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Project, ProjectMember, User
from schemas.member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse
)
from routers.auth import get_current_user
from utils.activity import log_activity
from utils.permissions import (
    check_project_manager,
    check_project_access
)


router = APIRouter(
    prefix="/projects",
    tags=["Project Members"]
)


# ADD PROJECT MEMBER
@router.post(
    "/{project_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED
)
def add_member(
    project_id: int,
    member_data: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_project_manager(project_id, current_user, db)

    user = db.query(User).filter(
        User.id == member_data.user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Project owner is already a project member"
        )

    existing_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_data.user_id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="User is already a project member"
        )

    if member_data.role not in ["project_manager", "team_member"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid project role"
        )

    new_member = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role
    )

    db.add(new_member)

    log_activity(
        db,
        action="member_added",
        details=f"User {user.name} was added to the project",
        user_id=current_user.id,
        project_id=project_id
    )

    db.commit()
    db.refresh(new_member)

    return new_member


# VIEW PROJECT MEMBERS
@router.get(
    "/{project_id}/members",
    response_model=list[MemberResponse]
)
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_project_access(project_id, current_user, db)

    members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()

    return members


# UPDATE MEMBER ROLE
@router.put(
    "/{project_id}/members/{user_id}",
    response_model=MemberResponse
)
def update_member_role(
    project_id: int,
    user_id: int,
    member_data: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_project_manager(project_id, current_user, db)

    if member_data.role not in ["project_manager", "team_member"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid project role"
        )

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Project member not found"
        )

    member.role = member_data.role

    log_activity(
        db,
        action="member_role_updated",
        details=f"User {user_id}'s project role was updated to {member_data.role}",
        user_id=current_user.id,
        project_id=project_id
    )

    db.commit()
    db.refresh(member)

    return member


# REMOVE PROJECT MEMBER
@router.delete("/{project_id}/members/{user_id}")
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_project_manager(project_id, current_user, db)

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Project member not found"
        )

    log_activity(
        db,
        action="member_removed",
        details=f"User {user_id} was removed from the project",
        user_id=current_user.id,
        project_id=project_id
    )

    db.delete(member)
    db.commit()

    return {
        "message": "Project member removed successfully"
    }
    
    