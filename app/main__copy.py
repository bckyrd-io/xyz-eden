
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import Optional

app = FastAPI()

# Configure CORS
origins = ["*"]  # Update with the origin of your web page
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory where you want to save the uploaded images
upload_directory = "img"  # Updated directory path without the leading "/"

# MySQL database URL
DATABASE_URL = "mysql+mysqlconnector://root@localhost/db_python"

# Create an SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create an SQLAlchemy session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the CapturedImage model for image storage
Base = declarative_base()

class CapturedImage(Base):
    __tablename__ = 'captured_images'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(length=255), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Endpoint to capture and save images
@app.post("/capture")
async def capture_image(file: UploadFile = File(...)):
    try:
        # Generate a unique filename using uuid
        unique_filename = str(uuid.uuid4()) + file.filename
        filename = os.path.join(upload_directory, unique_filename)

        # Ensure the directory exists; create it if it doesn't
        os.makedirs(upload_directory, exist_ok=True)

        # Log the filename for debugging purposes
        print("Received file:", filename)

        # Save the uploaded file to the specified directory
        with open(filename, "wb") as image_file:
            image_file.write(file.file.read())

        # Create a database record for the captured image
        db = SessionLocal()
        db_image = CapturedImage(filename=unique_filename)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        db.close()

        # Return a success message or perform further processing
        return {"message": "Image captured and saved successfully"}

    except Exception as e:
        # Log any exceptions for debugging purposes
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Image capture error")

# Endpoint to retrieve captured images
@app.get("/images")
async def get_images():
    db = SessionLocal()
    images = db.query(CapturedImage).all()
    db.close()
    return [{"id": image.id, "filename": image.filename, "timestamp": image.timestamp} for image in images]

# Define the UserRoleEnum for user roles
class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"

# Define the User model for user management
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=50), unique=True, index=True)
    hashed_password = Column(String(length=60))
    role = Column(String(length=60), default="user")

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Pydantic model for user registration
class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[UserRoleEnum] = UserRoleEnum.user

# Registration endpoint
@app.post("/register")
async def register_user(user: UserCreate):
    try:
        # Check if username already exists
        db = SessionLocal()
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            db.close()
            raise HTTPException(
                status_code=400, detail="Username already exists")

        # Hash the password
        hashed_password = hash_password(user.password)

        # Create a new user with the specified user role
        db_user = User(username=user.username,
                       hashed_password=hashed_password, role=user.role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()

        return {"message": "User registered successfully"}
    except Exception as e:
        # Log any exceptions for debugging purposes
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="User registration error")

# Create the database table
Base.metadata.create_all(bind=engine)

# Pydantic model for user login
class UserLogin(BaseModel):
    username: str
    password: str

# JWT Settings
SECRET_KEY = "24f8c5e5-fcb5-bdfc-aac0-7bff0e800334"  # Replace with your actual secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Create a function to generate JWT tokens
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Authenticate and generate token
async def authenticate_user(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if user and verify_password(password, user.hashed_password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    return None

# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Token validation error")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token validation error")

# Login endpoint
@app.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_token = await authenticate_user(form_data.username, form_data.password)
    if user_token is None:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    return user_token

# Edit user role endpoint (Requires admin privileges)
@app.put("/user/{user_id}/edit-role")
async def edit_user_role(user_id: int, new_role: UserRoleEnum, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.username == current_user).first()
    db.close()

    if user.role != UserRoleEnum.admin:
        raise HTTPException(
            status_code=403, detail="Only admin users can edit roles")

    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    db_user.role = new_role
    db.commit()
    db.close()

    return {"message": "User role updated successfully"}

# Delete user endpoint (Requires admin privileges)
@app.delete("/user/{user_id}/delete")
async def delete_user(user_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.username == current_user).first()
    db.close()

    if user.role != UserRoleEnum.admin:
        raise HTTPException(
            status_code=403, detail="Only admin users can delete users")

    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    db.close()

    return {"message": "User deleted successfully"}
