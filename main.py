from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from assistant import health_assistant
import sqlite3

app = FastAPI(title="MediCare AI Hospital Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    return sqlite3.connect("hospital.db")


def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            age INTEGER,
            gender TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            email TEXT,
            department TEXT,
            appointment_date TEXT,
            date TEXT,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()


create_tables()


class SymptomRequest(BaseModel):
    symptom: str


class PatientRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    age: int
    gender: str


class AppointmentRequest(BaseModel):
    patient_name: str
    date: str
    time: str
    department: str


@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/assistant")
def assistant(request: SymptomRequest):
    return health_assistant(request.symptom)


@app.post("/register")
def register_patient(patient: PatientRequest):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO patients
            (name, email, phone, age, gender)
            VALUES (?, ?, ?, ?, ?)
        """, (
            patient.name,
            patient.email,
            patient.phone,
            patient.age,
            patient.gender
        ))

        conn.commit()

        return {
            "message": "Patient registered successfully",
            "patient": patient.name
