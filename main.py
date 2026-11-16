from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from assistant import health_assistant
import sqlite3

app = FastAPI(title="MediCare AI Hospital Assistant")

# Database connection
def get_db():
    return sqlite3.connect("hospital.db")


# Create database tables
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
            appointment_date TEXT
        )
    """)

    conn.commit()
    conn.close()


create_tables()


# Request Models
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
    email: EmailStr
    department: str
    appointment_date: str


# Home API
@app.get("/")
def home():
    return {
        "message": "MediCare AI Hospital Assistant is running",
        "version": "2.0"
    }


# Health API
@app.get("/health")
def health():
    return {"status": "healthy"}


# AI Assistant API
@app.post("/assistant")
def assistant(request: SymptomRequest):
    return health_assistant(request.symptom)


# Patient Registration API
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
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    finally:
        conn.close()


# Appointment Booking API
@app.post("/appointment")
def book_appointment(appointment: AppointmentRequest):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO appointments
        (patient_name, email, department, appointment_date)
        VALUES (?, ?, ?, ?)
    """, (
        appointment.patient_name,
        appointment.email,
        appointment.department,
        appointment.appointment_date
    ))

    conn.commit()
    conn.close()

    return {
        "message": "Appointment submitted successfully",
        "patient": appointment.patient_name,
        "department": appointment.department,
        "date": appointment.appointment_date
    }


# View Registered Patients
@app.get("/patients")
def get_patients():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()

    return {"patients": patients}


# View Appointments
@app.get("/appointments")
def get_appointments():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()

    conn.close()

    return {"appointments": appointments}
