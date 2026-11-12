from models import ActivityLog


def log_activity(
    db,
    action: str,
    details: str,
    user_id: int = None,
    project_id: int = None,
    task_id: int = None
):
    activity = ActivityLog(
        action=action,
        details=details,
        user_id=user_id,
        project_id=project_id,
        task_id=task_id
    )

    db.add(activity)

    return activity
