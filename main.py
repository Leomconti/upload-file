import os
import uuid

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

# Load URL prefix from environment variable, default if not set
BASE_URL = os.getenv("URL", "https://utils.mosmn.com.br")
UPLOAD_DIR = "uploads"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles file uploads, saves the file with a unique name,
    and returns the download URL.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    try:
        # Extract file extension
        _, extension = os.path.splitext(file.filename)
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the file asynchronously
        with open(file_path, "wb") as buffer:
            content = await file.read()  # Read file content
            buffer.write(content)  # Write to disk

        download_url = f"{BASE_URL}/files/{unique_filename}"
        return {"filename": unique_filename, "download_url": download_url}
    except Exception as e:
        # Basic error handling
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")
    finally:
        # Ensure the file pointer is closed
        await file.close()


@app.get("/files/{filename}")
async def get_file(filename: str):
    """
    Serves a previously uploaded file for download.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Check for directory traversal attempts (basic check)
    if not filename.startswith(str(uuid.UUID(filename.split(".")[0]))):
        raise HTTPException(status_code=403, detail="Invalid filename format")

    # Return file response
    return FileResponse(path=file_path, filename=filename)


if __name__ == "__main__":
    # Run the app with uvicorn
    # Use reload=True for development to automatically reload on code changes
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
