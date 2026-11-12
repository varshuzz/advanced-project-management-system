from fastapi import FastAPI

from database import engine, Base

import models
from routers import auth, projects, tasks, comments, members, activity, users


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="Advanced Project & Team Management System",
    description="Backend API for managing projects, teams, and tasks",
    version="1.0.0"
)


# Register Authentication Router
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(members.router)
app.include_router(activity.router)
app.include_router(users.router)

# Home Endpoint
@app.get("/")
def home():
    return {
        "message": "Advanced Project & Team Management System API",
        "status": "Running successfully"
    }


# Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
    