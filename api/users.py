# users.py
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import SessionLocal, User
from enum import Enum 

class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(user_data):
    try:
        db = SessionLocal()
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return {"message": "User registered successfully"}
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="User registration error")

def get_user_by_username(username: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    return user

def edit_user_role(user_id: int, new_role: UserRoleEnum, current_user: str):
    # Implement the edit_user_role functionality here
    pass

def delete_user(user_id: int, current_user: str):
    # Implement the delete_user functionality here
    pass
