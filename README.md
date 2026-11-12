# Advanced Project and Team Management System

A backend application developed using Python, FastAPI, and SQLite to manage projects, teams, tasks, and user roles.

## Technologies Used

- Python
- FastAPI
- SQLite
- SQLAlchemy
- JWT Authentication
- Bcrypt Password Hashing
- Swagger UI

## Project Structure

```text
Advanced-Project-Management-System/
│
├── backend/
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── activity.py
│   │   ├── auth.py
│   │   ├── comments.py
│   │   ├── members.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   └── users.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── activity.py
│   │   ├── comment.py
│   │   ├── member.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── user.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── activity.py
│   │   ├── permissions.py
│   │   └── security.py
│   │
│   ├── .gitignore
│   ├── database.py
│   ├── main.py
│   ├── make_admin.py
│   └── models.py
│
└── README.md
```

## Features

- User registration and login
- JWT-based authentication
- Password hashing
- Project creation and management
- Team member management
- Role-based access control
- Task creation and management
- Task assignment
- Comments
- Activity tracking

## How to Run the Project

1. Clone the repository.
2. Open the backend folder.
3. Install the required Python packages.
4. Start the FastAPI server.

Run:

```bash
uvicorn main:app --reload
```

## API Documentation

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI provides an interface to test the API endpoints.

## Database

The project uses SQLite with SQLAlchemy ORM.

## Project Type

Academic Project – Advanced Project and Team Management System.

