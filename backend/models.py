from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


# -------------------------
# USER MODEL
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="team_member", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects_created = relationship(
        "Project",
        back_populates="created_by",
    )

    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    assigned_tasks = relationship(
        "Task",
        back_populates="assigned_user",
    )

    comments = relationship(
        "TaskComment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
    )


# -------------------------
# PROJECT MODEL
# -------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)

    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    created_by = relationship(
        "User",
        back_populates="projects_created",
    )

    members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    activity_logs = relationship(
        "ActivityLog",
        back_populates="project",
        cascade="all, delete-orphan",
    )


# -------------------------
# PROJECT MEMBER MODEL
# -------------------------
class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    role = Column(String(50), default="team_member", nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    project = relationship(
        "Project",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="project_memberships",
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "user_id",
            name="unique_project_member",
        ),
    )


# -------------------------
# TASK MODEL
# -------------------------
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    status = Column(String(50), default="pending", nullable=False)
    priority = Column(String(50), default="medium", nullable=False)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    assigned_to_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship(
        "Project",
        back_populates="tasks",
    )

    assigned_user = relationship(
        "User",
        back_populates="assigned_tasks",
    )

    comments = relationship(
        "TaskComment",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    activity_logs = relationship(
        "ActivityLog",
        back_populates="task",
        cascade="all, delete-orphan",
    )


# -------------------------
# TASK COMMENT MODEL
# -------------------------
class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text, nullable=False)

    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship(
        "Task",
        back_populates="comments",
    )

    user = relationship(
        "User",
        back_populates="comments",
    )


# -------------------------
# ACTIVITY LOG MODEL
# -------------------------
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=True,
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True,
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="activity_logs",
    )

    project = relationship(
        "Project",
        back_populates="activity_logs",
    )

    task = relationship(
        "Task",
        back_populates="activity_logs",
    )
    
    