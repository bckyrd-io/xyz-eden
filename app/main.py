from fastapi import FastAPI, UploadFile, File, HTTPException
# from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import Column, Integer, String, DateTime, create_engine



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

# Define the database model for CapturedImage
from sqlalchemy import Column, Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base



# app/models.py



Base = declarative_base()

class CapturedImage(Base):
    __tablename__ = 'captured_images'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(length=255), index=True)  # Specify the length (e.g., 255)
    timestamp = Column(DateTime, default=datetime.utcnow)



# Base = declarative_base()

# class CapturedImage(Base):
#     __tablename__ = 'captured_images'

#     id = Column(Integer, primary_key=True, index=True)
#     filename = Column(String, index=True)
#     timestamp = Column(DateTime, default=datetime.utcnow)

# Create the database table
Base.metadata.create_all(bind=engine)

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
