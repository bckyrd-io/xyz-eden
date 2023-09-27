from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
from fastapi import FastAPI, Depends
# from fastapi_auth import login, logout, get_current_user
# from fastapi_auth.schemas import LoginSchema, ChangeRoleSchema


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


# i gues here is the models about capture_image
# and all the required
#  functions

# app/models.py
Base = declarative_base()

class CapturedImage(Base):
    __tablename__ = 'captured_images'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(length=255), index=True)  # Specify the length (e.g., 255)
    timestamp = Column(DateTime, default=datetime.utcnow)



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
        db_image = CapturedImage(filename=unique_filename)  # Save the unique filename
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
    

@app.get("/images")
async def get_images():
    db = SessionLocal()
    images = db.query(CapturedImage).all()
    db.close()
    return [{"id": image.id, "filename": image.filename, "timestamp": image.timestamp} for image in images]


# and also i think this is a model for 
# users and all its 
# functions 

# Define the User model
class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=50), unique=True, index=True)
    hashed_password = Column(String(length=60))
    role = Column(String(length=60), default="user")  # Store role as a string
    
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
    role: Optional[UserRoleEnum] = UserRoleEnum.user  # Default to "user"

# Registration endpoint
@app.post("/register")
async def register_user(user: UserCreate):
    try:
        # Check if username already exists
        db = SessionLocal()
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            db.close()
            raise HTTPException(status_code=400, detail="Username already exists")

        # Hash the password
        hashed_password = hash_password(user.password)

        # Create a new user with the specified user role
        db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
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

