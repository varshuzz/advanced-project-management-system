from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Task, Project, ProjectMember, User
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from routers.auth import get_current_user
from utils.activity import log_activity
from utils.permissions import check_project_manager


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# CHECK PROJECT ACCESS
def get_user_project(
    project_id: int,
    current_user: User,
    db: Session
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
                | (current_user.role == "admin")
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


# CREATE TASK
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_user_project(
        task_data.project_id,
        current_user,
        db
    )

    if task_data.assigned_to_id is not None:
        assigned_user = db.query(User).filter(
            User.id == task_data.assigned_to_id
        ).first()

        if assigned_user is None:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

        if current_user.role != "admin":
            membership = db.query(ProjectMember).filter(
                ProjectMember.project_id == task_data.project_id,
                ProjectMember.user_id == assigned_user.id
            ).first()

            project = db.query(Project).filter(
                Project.id == task_data.project_id
            ).first()

            if (
                assigned_user.id != project.created_by_id
                and membership is None
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Assigned user is not a project member"
                )

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id,
        assigned_to_id=task_data.assigned_to_id,
        priority=task_data.priority,
        due_date=task_data.due_date
    )

    db.add(new_task)
    db.flush()

    log_activity(
        db,
        action="task_created",
        details=f"Task '{new_task.title}' was created",
        user_id=current_user.id,
        project_id=new_task.project_id,
        task_id=new_task.id
    )

    db.commit()
    db.refresh(new_task)

    return new_task


# VIEW ALL TASKS
@router.get("/", response_model=list[TaskResponse])
def get_all_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        db.query(Task)
        .join(Project, Task.project_id == Project.id)
    )

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


# VIEW TASK BY ID
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    get_user_project(
        task.project_id,
        current_user,
        db
    )

    return task


# UPDATE TASK
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    get_user_project(
        task.project_id,
        current_user,
        db
    )

    # CHECK WHETHER USER IS A PROJECT MANAGER
    is_manager = False

    if current_user.role == "admin":
        is_manager = True

    elif task.project.created_by_id == current_user.id:
        is_manager = True

    else:
        project_manager = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id,
            ProjectMember.role == "project_manager"
        ).first()

        if project_manager:
            is_manager = True

    # TEAM MEMBERS CAN UPDATE ONLY THEIR ASSIGNED TASKS
    if not is_manager and task.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update tasks assigned to you"
        )

    update_data = task_data.dict(exclude_unset=True)

    if update_data.get("assigned_to_id") is not None:
        assigned_user = db.query(User).filter(
            User.id == update_data["assigned_to_id"]
        ).first()

        if assigned_user is None:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

        if current_user.role != "admin":
            membership = db.query(ProjectMember).filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == assigned_user.id
            ).first()

            if (
                assigned_user.id != task.project.created_by_id
                and membership is None
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Assigned user is not a project member"
                )

    for key, value in update_data.items():
        setattr(task, key, value)

    log_activity(
        db,
        action="task_updated",
        details=f"Task '{task.title}' was updated",
        user_id=current_user.id,
        project_id=task.project_id,
        task_id=task.id
    )

    db.commit()
    db.refresh(task)

    return task


# DELETE TASK
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    check_project_manager(
        task.project_id,
        current_user,
        db
    )

    log_activity(
        db,
        action="task_deleted",
        details=f"Task '{task.title}' was deleted",
        user_id=current_user.id,
        project_id=task.project_id
    )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }

