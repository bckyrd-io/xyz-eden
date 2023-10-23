# main.py
from typing import Optional
from datetime import datetime, date, timedelta
from jose import JWTError, jwt
import os
# -
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Path, Query, UploadFile, Depends, Query, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
# -
from sqlalchemy import desc, func
from sqlalchemy.orm import Session  # Add this import
from pydantic import BaseModel
# -
from models import SessionLocal  # Add this import
from models import User, CapturedImage, ImagePrediction, ScheduleCapture
# -
from users import create_user, get_all_users, get_user_by_username, UserRoleEnum, hash_password
from users import authenticate_user, get_current_user
from capture import capture_and_save_image
from predict import predict_and_store_predictions  # Add this import


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


# Endpoint to capture and save images
@app.post("/capture")
async def capture_image(file: UploadFile = UploadFile(...)):
    # Capture and save the image
    image_data = capture_and_save_image(file)
    # Assuming the capture_and_save_image function returns the image ID
    image_id = image_data["id"]
    image_path = os.path.join("img", image_data["filename"])
    # Call the prediction function to make predictions on the saved image
    predict_and_store_predictions(image_id, image_path)  # Add this line

    return {"message": "Image captured, saved, and predictions made successfully"}


# Pydantic model for scheduling captures
class ScheduleCaptureCreate(BaseModel):
    interval: int
    times: int


@app.post("/schedule")
async def create_schedule(schedule_data: ScheduleCaptureCreate):
    db = SessionLocal()
    try:
        # Insert the schedule data into the database
        schedule = ScheduleCapture(**schedule_data.dict())
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create schedule")
    finally:
        db.close()


@app.get("/capture-settings")
async def get_capture_settings():
    db = SessionLocal()
    settings = db.query(ScheduleCapture).order_by(
        desc(ScheduleCapture.timestamp)).first()
    db.close()
    return {"interval": settings.interval, "times": settings.times}


@app.get("/images")
async def get_images():
    db = SessionLocal()
    images = db.query(CapturedImage).all()
    db.close()
    return [{"id": image.id, "filename": image.filename, "timestamp": image.timestamp} for image in images]


@app.get("/items")
async def get_all_items():
    db = SessionLocal()
    items = db.query(ImagePrediction).order_by(
        desc(ImagePrediction.id)).limit(10).all()
    return items


@app.get("/item/{item_id}")
async def get_item_by_id(item_id: int):
    db = SessionLocal()
    item = db.query(ImagePrediction).filter(
        ImagePrediction.id == item_id).first()
    if item is not None:
        return item
    raise HTTPException(status_code=404, detail="Item not found.")


@app.get("/diseases_today")
async def get_diseases_today():
    today = date.today()
    db = SessionLocal()
    # Query the database for predictions with diseases and timestamp for today
    predictions = db.query(ImagePrediction).join(CapturedImage).filter(
        ImagePrediction.disease.isnot(None),
        CapturedImage.timestamp >= today,
        CapturedImage.timestamp < today + timedelta(days=2)
    )
    # Get the results
    results = predictions.all()
    if not results:
        raise HTTPException(
            status_code=404, detail="No matching records found")
    return results


@app.get("/diseases")
async def get_diseases():
    db = SessionLocal()
    # Query the database for predictions with diseases and timestamp for today
    predictions = db.query(ImagePrediction).join(CapturedImage).filter(
        ImagePrediction.disease.isnot(None)
    )
    # Get the results
    results = predictions.all()
    if not results:
        raise HTTPException(
            status_code=404, detail="No matching records found")
    return results


@app.get("/growth_stage")
async def get_growth_stage():
    db = SessionLocal()
    try:
        # Query the database for all predictions with growth stage
        predictions = db.query(
            ImagePrediction.captured_image_id,
            ImagePrediction.plant_name,
            ImagePrediction.growth_stage,
            func.DATE(CapturedImage.timestamp).label("date")
        ).join(CapturedImage).filter(
            ImagePrediction.growth_stage.isnot(None)
        ).all()
        # Group data by date and plant name
        data_grouped = {}
        for prediction in predictions:
            date_key = prediction.date
            plant_name = prediction.plant_name
            growth_stage = prediction.growth_stage
            if date_key not in data_grouped:
                data_grouped[date_key] = {}
            if plant_name not in data_grouped[date_key]:
                data_grouped[date_key][plant_name] = []
            data_grouped[date_key][plant_name].append(growth_stage)
        return data_grouped
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error fetching data") from e
    finally:
        db.close()


# Registration endpoint
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[UserRoleEnum] = UserRoleEnum.user


@app.post("/register")
async def register_user(user: UserCreate):
    user_data = user.dict()
    user_data["hashed_password"] = hash_password(user.password)
    del user_data["password"]
    return create_user(user_data)


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
async def edit_user_role(user_id: int, new_role: UserRoleEnum):
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
async def delete_user(user_id: int):
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    db.close()
    return {"message": "User deleted successfully"}


@app.get("/users")
async def list_users():
    users = get_all_users()
    return {"users": users}
