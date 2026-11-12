from database import SessionLocal
from models import User

db = SessionLocal()

try:
    email = input("Enter your registered email: ")

    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:
        print("User not found!")

    else:
        user.role = "admin"
        db.commit()

        print("\nAdmin role assigned successfully!")
        print("Name:", user.name)
        print("Email:", user.email)
        print("Role:", user.role)

finally:
    db.close()
    
    