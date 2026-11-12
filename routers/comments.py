from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Task, TaskComment, User
from schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse
)
from routers.auth import get_current_user
from routers.tasks import get_user_project
from utils.activity import log_activity


router = APIRouter(
    prefix="/tasks",
    tags=["Task Comments"]
)


# CREATE COMMENT
@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
    task_id: int,
    comment_data: CommentCreate,
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

    get_user_project(task.project_id, current_user, db)

    new_comment = TaskComment(
        comment=comment_data.comment,
        task_id=task_id,
        user_id=current_user.id
    )

    db.add(new_comment)

    log_activity(
        db,
        action="comment_added",
        details="A new comment was added to a task",
        user_id=current_user.id,
        project_id=task.project_id,
        task_id=task.id
    )

    db.commit()
    db.refresh(new_comment)

    return new_comment


# VIEW COMMENTS
@router.get(
    "/{task_id}/comments",
    response_model=list[CommentResponse]
)
def get_task_comments(
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

    get_user_project(task.project_id, current_user, db)

    comments = db.query(TaskComment).filter(
        TaskComment.task_id == task_id
    ).all()

    return comments


# UPDATE COMMENT
@router.put(
    "/{task_id}/comments/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    task_id: int,
    comment_id: int,
    comment_data: CommentUpdate,
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

    get_user_project(task.project_id, current_user, db)

    comment = db.query(TaskComment).filter(
        TaskComment.id == comment_id,
        TaskComment.task_id == task_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own comments"
        )

    comment.comment = comment_data.comment

    log_activity(
        db,
        action="comment_updated",
        details="A task comment was updated",
        user_id=current_user.id,
        project_id=task.project_id,
        task_id=task.id
    )

    db.commit()
    db.refresh(comment)

    return comment


# DELETE COMMENT
@router.delete(
    "/{task_id}/comments/{comment_id}"
)
def delete_comment(
    task_id: int,
    comment_id: int,
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

    get_user_project(task.project_id, current_user, db)

    comment = db.query(TaskComment).filter(
        TaskComment.id == comment_id,
        TaskComment.task_id == task_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comments"
        )

    log_activity(
        db,
        action="comment_deleted",
        details="A task comment was deleted",
        user_id=current_user.id,
        project_id=task.project_id,
        task_id=task.id
    )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }
    