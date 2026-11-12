from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Project, ProjectMember, User


# CHECK PROJECT ACCESS
def check_project_access(
    project_id: int,
    current_user: User,
    db: Session
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Admin has access to every project
    if current_user.role == "admin":
        return project

    # Project owner has access
    if project.created_by_id == current_user.id:
        return project

    # Project members have access
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this project"
        )

    return project


# CHECK PROJECT MANAGER PERMISSION
def check_project_manager(
    project_id: int,
    current_user: User,
    db: Session
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Admin can manage all projects
    if current_user.role == "admin":
        return project

    # Project owner is automatically a manager
    if project.created_by_id == current_user.id:
        return project

    # Check project-specific manager role
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if membership is None or membership.role != "project_manager":
        raise HTTPException(
            status_code=403,
            detail="Only project managers can perform this action"
        )

    return project


# CHECK ADMIN PERMISSION
def check_admin(current_user: User):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin permission required"
        )

    return current_user
