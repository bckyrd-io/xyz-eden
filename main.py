from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import uuid  # Import the uuid library for generating unique filenames
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

# Directory where you want to save the uploaded images
upload_directory = "img"  # Updated directory path without the leading "/"

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

        # Return a success message or perform further processing
        return {"message": "Image captured and saved successfully"}

    except Exception as e:
        # Log any exceptions for debugging purposes
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Image capture error")
