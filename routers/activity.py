from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import ActivityLog, Project, ProjectMember, User
from schemas.activity import ActivityResponse
from routers.auth import get_current_user


router = APIRouter(
    prefix="/activity",
    tags=["Activity Logs"]
)


# VIEW ALL ACTIVITIES
@router.get("/", response_model=list[ActivityResponse])
def get_all_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    activities = (
        db.query(ActivityLog)
        .outerjoin(
            Project,
            ActivityLog.project_id == Project.id
        )
        .outerjoin(
            ProjectMember,
            Project.id == ProjectMember.project_id
        )
        .filter(
            (Project.created_by_id == current_user.id)
            | (ProjectMember.user_id == current_user.id)
            | (ActivityLog.user_id == current_user.id)
        )
        .distinct()
        .order_by(ActivityLog.created_at.desc())
        .all()
    )

    return activities


# VIEW ACTIVITIES FOR A PROJECT
@router.get(
    "/projects/{project_id}",
    response_model=list[ActivityResponse]
)
def get_project_activities(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = (
        db.query(Project)
        .outerjoin(
            ProjectMember,
            Project.id == ProjectMember.project_id
        )
        .filter(
            Project.id == project_id,
            (
                (Project.created_by_id == current_user.id)
                | (ProjectMember.user_id == current_user.id)
            )
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found or access denied"
        )

    activities = db.query(ActivityLog).filter(
        ActivityLog.project_id == project_id
    ).order_by(
        ActivityLog.created_at.desc()
    ).all()

    return activities

