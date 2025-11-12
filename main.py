from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Personal Connector")

class CreateDocIn(BaseModel):
    title: str
    content: str

@app.get("/")
def root():
    return {"message": "OK", "service": "personal-connector"}

@app.post("/createDocument")
def create_document(payload: CreateDocIn):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="title required")
    return {
        "status": "received",
        "title": payload.title,
        "content_length": len(payload.content)
    }
