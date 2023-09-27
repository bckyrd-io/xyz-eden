from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models import SessionLocal, User
from enum import Enum
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "24f8c5e5-fcb5-bdfc-aac0-7bff0e800334"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# users.py
async def authenticate_user(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user or not verify_password(password, user.hashed_password):
        return None

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return access_token


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

# Add the get_current_user function here
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Token validation error")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token validation error")

def edit_user_role(user_id: int, new_role: UserRoleEnum, current_user: str):
    # Implement the edit_user_role functionality here
    pass

def delete_user(user_id: int, current_user: str):
    # Implement the delete_user functionality here
    pass
