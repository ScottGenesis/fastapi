from fastapi import FastAPI, Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server is running"}

@app.post("/createDocument")
async def create_document(request: Request):
    try:
        data = await request.json()
        title = data.get("title", "Untitled Document")
        content = data.get("content", "")

        # Load credentials
        creds = Credentials(
            None,
            refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"]
        )

        # Build Docs API service
        docs_service = build("docs", "v1", credentials=creds)

        # Create a new document
        document = docs_service.documents().create(body={"title": title}).execute()
        doc_id = document.get("documentId")

        # Insert content into the doc
        requests = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": content
                }
            }
        ]
        docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

        return {
            "status": "success",
            "documentId": doc_id,
            "documentLink": f"https://docs.google.com/document/d/{doc_id}/edit"
        }

    except Exception as e:
        return {"status": "error", "details": str(e)}


