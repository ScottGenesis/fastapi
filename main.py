from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

DOCS_SCOPE = "https://www.googleapis.com/auth/documents"
DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"
SCOPES = [DOCS_SCOPE, DRIVE_SCOPE]

app = FastAPI(title="Personal Connector")

class CreateDocIn(BaseModel):
    title: str
    content: str

@app.get("/")
def root():
    return {"message": "OK", "service": "personal-connector"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

def get_google_creds():
    cid = os.environ.get("GOOGLE_CLIENT_ID")
    csec = os.environ.get("GOOGLE_CLIENT_SECRET")
    rtok = os.environ.get("GOOGLE_REFRESH_TOKEN")
    if not all([cid, csec, rtok]):
        raise RuntimeError("Missing Google OAuth env vars")
    creds = Credentials(
        None,
        refresh_token=rtok,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cid,
        client_secret=csec,
        scopes=SCOPES,
    )
    # exchange refresh token for an access token
    creds.refresh(Request())
    return creds

@app.post("/createDocument")
def create_document(payload: CreateDocIn):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is required")

    try:
        creds = get_google_creds()
        docs = build("docs", "v1", credentials=creds)
        drive = build("drive", "v3", credentials=creds)

        # 1) Create a new Google Doc
        doc = docs.documents().create(body={"title": payload.title}).execute()
        doc_id = doc["documentId"]

        # 2) Insert content at the top
        requests = [{
            "insertText": {
                "location": {"index": 1},
                "text": payload.content
            }
        }]
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

        # 3) Return a nice link
        meta = drive.files().get(fileId=doc_id, fields="id,name,webViewLink").execute()
        return {
            "status": "created",
            "doc_id": meta["id"],
            "name": meta["name"],
            "link": meta["webViewLink"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google API error: {e}")
