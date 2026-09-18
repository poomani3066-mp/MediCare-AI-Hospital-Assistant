from fastapi import FastAPI
from pydantic import BaseModel
from assistant import health_assistant

app = FastAPI(title="MediCare AI Hospital Assistant")


class SymptomRequest(BaseModel):
    symptom: str


@app.get("/")
def home():
    return {
        "message": "MediCare AI Hospital Assistant is running",
        "version": "1.0"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/assistant")
def assistant(request: SymptomRequest):
    return health_assistant(request.symptom)
