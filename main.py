from fastapi import FastAPI
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

app = FastAPI()

# ✅ Define the request body model so Swagger shows editable fields
class DocumentRequest(BaseModel):
    title: str
    content: str

@app.get("/")
def root():
    return {"message": "Server is running"}

@app.post("/createDocument")
async def create_document(data: DocumentRequest):
    try:
        # ✅ Load Google credentials from environment variables
        creds = Credentials(
            None,
            refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        )

        # ✅ Initialize Google Docs and Drive APIs
        docs_service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)

        # ✅ Create a new Google Doc
        document = docs_service.documents().create(body={"title": data.title}).execute()
        document_id = document.get("documentId")

        # ✅ Insert content into the newly created Doc
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": data.content
                        }
                    }
                ]
            },
        ).execute()

        # ✅ Get the shareable document link
        document_link = f"https://docs.google.com/document/d/{document_id}/edit"

        return {
            "status": "success",
            "documentId": document_id,
            "documentLink": document_link
        }

    except Exception as e:
        return {"status": "error", "details": str(e)}



