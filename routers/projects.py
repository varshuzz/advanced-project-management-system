from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Project, ProjectMember, User
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from routers.auth import get_current_user
from utils.activity import log_activity
from utils.permissions import check_project_manager


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# CREATE PROJECT
@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        created_by_id=current_user.id
    )

    db.add(new_project)
    db.flush()

    log_activity(
        db,
        action="project_created",
        details=f"Project '{new_project.name}' was created",
        user_id=current_user.id,
        project_id=new_project.id
    )

    db.commit()
    db.refresh(new_project)

    return new_project


# VIEW ALL PROJECTS
@router.get("/", response_model=list[ProjectResponse])
def get_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Project)

    if current_user.role != "admin":
        query = (
            query.outerjoin(
                ProjectMember,
                Project.id == ProjectMember.project_id
            )
            .filter(
                (Project.created_by_id == current_user.id)
                | (ProjectMember.user_id == current_user.id)
            )
        )

    return query.distinct().all()


# VIEW PROJECT BY ID
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        project = db.query(Project).filter(
            Project.id == project_id
        ).first()
    else:
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

    return project


# UPDATE PROJECT
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = check_project_manager(
        project_id,
        current_user,
        db
    )

    update_data = project_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(project, key, value)

    log_activity(
        db,
        action="project_updated",
        details=f"Project '{project.name}' was updated",
        user_id=current_user.id,
        project_id=project.id
    )

    db.commit()
    db.refresh(project)

    return project


# DELETE PROJECT
@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = check_project_manager(
        project_id,
        current_user,
        db
    )

    log_activity(
        db,
        action="project_deleted",
        details=f"Project '{project.name}' was deleted",
        user_id=current_user.id
    )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }
    
    