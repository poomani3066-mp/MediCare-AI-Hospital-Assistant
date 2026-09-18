from fastapi import FastAPI

app = FastAPI(title="MediCare AI Hospital Assistant")


@app.get("/")
def home():
    return {
        "message": "Welcome to MediCare AI Hospital Assistant",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
