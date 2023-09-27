# main.py
from fastapi import FastAPI, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from jose import JWTError, jwt
from capture import capture_and_save_image
from users import create_user, get_user_by_username, UserRoleEnum, hash_password

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

# ... Other middleware and configuration ...

# Endpoint to capture and save images


@app.post("/capture")
async def capture_image(file: UploadFile = UploadFile(...)):
    return capture_and_save_image(file)

# ... Other endpoints ...

# Registration endpoint


class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[UserRoleEnum] = UserRoleEnum.user


@app.post("/register")
async def register_user(user: UserCreate):
    user_data = user.dict()
    user_data["hashed_password"] = hash_password(user.password)
    del user_data["password"]
    return create_user(user_data)

# ... Other endpoints ...

# Define the remaining endpoints and dependencies as needed.
