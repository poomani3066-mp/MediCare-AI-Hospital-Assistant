from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from assistant import health_assistant
import sqlite3

app = FastAPI(title="MediCare AI Hospital Assistant")

# Frontend and Backend Connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database Connection
def get_db():
    return sqlite3.connect("hospital.db")


# Create Database Tables
def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            email TEXT UNIQUE,
            phone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            date TEXT,
            time TEXT,
            department TEXT
        )
    """)

    conn.commit()
    conn.close()


create_tables()


# Request Models
class Patient(BaseModel):
    patient_name: str
    email: EmailStr
    phone: str


class Appointment(BaseModel):
    patient_name: str
    date: str
    time: str
    department: str


class SymptomRequest(BaseModel):
    symptom: str


# Home Page
@app.get("/")
def home():
    return {
        "message": "Welcome to MediCare AI Hospital Assistant",
        "status": "Running"
    }


# Health Check
@app.get("/health")
def health():
    return {"status": "Healthy"}


# AI Assistant
@app.post("/assistant")
def assistant(request: SymptomRequest):
    try:
        result = health_assistant(request.symptom)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Patient Registration
@app.post("/register")
def register(patient: Patient):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO patients (patient_name, email, phone) VALUES (?, ?, ?)",
            (patient.patient_name, patient.email, patient.phone)
        )
        conn.commit()
        return {"message": "Patient registered successfully"}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")

    finally:
        conn.close()


# Book Appointment
@app.post("/appointments")
def book_appointment(appointment: Appointment):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO appointments
        (patient_name, date, time, department)
        VALUES (?, ?, ?, ?)""",
        (
            appointment.patient_name,
            appointment.date,
            appointment.time,
            appointment.department
        )
    )

    conn.commit()
    conn.close()

    return {"message": "Appointment booked successfully"}


# View Appointments
@app.get("/appointments")
def get_appointments():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments")
    data = cursor.fetchall()

    conn.close()

    return {"appointments": data}


# View Patients
@app.get("/patients")
def get_patients():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()

    conn.close()

    return {"patients": data}
