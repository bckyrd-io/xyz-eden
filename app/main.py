# app/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from database import SessionLocal
from models import CapturedImage
from datetime import datetime
import os
from fastapi.middleware.cors import CORSMiddleware


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

# Create this directory in your project folder
upload_directory = "captured"

@app.post("/capture")
async def capture_image(file: UploadFile = File(...), db: SessionLocal = Depends()):
    try:
        # Save the uploaded file to the specified directory
        filename = os.path.join(upload_directory, file.filename)
        with open(filename, "wb") as image_file:
            image_file.write(file.file.read())

        # Create a database record for the captured image
        db_image = CapturedImage(filename=file.filename, timestamp=datetime.now())
        db = SessionLocal()
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        # Return a success message or perform further processing
        return {"message": "Image captured and saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Image capture error")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
