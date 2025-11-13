from fastapi import FastAPI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server is running"}

@app.post("/createDocument")
def create_document():
    try:
        # Load Google credentials from environment variables
        creds = Credentials(
            None,
            refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        )

        # Initialize Google Drive API
        drive_service = build("drive", "v3", credentials=creds)

        # Fetch a small list of files to confirm the connection
        results = drive_service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get("files", [])

        if not files:
            return {"status": "success", "message": "Connected to Google API, but no files found."}
        else:
            return {"status": "success", "files": files}

    except Exception as e:
        return {"status": "error", "details": str(e)}

