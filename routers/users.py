from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas.user import UserUpdate, UserResponse, ChangePassword
from routers.auth import get_current_user
from utils.security import verify_password, hash_password
from utils.activity import log_activity
from utils.permissions import check_admin


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# GET ALL USERS (ADMIN ONLY)
@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin(current_user)

    return db.query(User).all()


# GET USER BY ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own profile"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# UPDATE OWN PROFILE
@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = user_data.dict(exclude_unset=True)

    if "email" in update_data:
        existing_user = db.query(User).filter(
            User.email == update_data["email"],
            User.id != current_user.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    for key, value in update_data.items():
        setattr(current_user, key, value)

    log_activity(
        db,
        action="profile_updated",
        details="User profile was updated",
        user_id=current_user.id
    )

    db.commit()
    db.refresh(current_user)

    return current_user


# CHANGE PASSWORD
@router.put("/change-password")
def change_password(
    password_data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # VERIFY CURRENT PASSWORD
    if not verify_password(
        password_data.current_password,
        current_user.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    # CHECK NEW PASSWORD AND CONFIRM PASSWORD
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="New password and confirm password do not match"
        )

    # CHECK WHETHER NEW PASSWORD IS SAME AS CURRENT PASSWORD
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password"
        )

    # HASH AND UPDATE NEW PASSWORD
    current_user.password = hash_password(
        password_data.new_password
    )

    log_activity(
        db,
        action="password_changed",
        details="User changed their password",
        user_id=current_user.id
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }
    
    