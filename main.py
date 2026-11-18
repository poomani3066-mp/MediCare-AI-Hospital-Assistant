from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
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

DATABASE = "hospital.db"


def get_db():
    return sqlite3.connect(DATABASE)


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
    email: str
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
    html_file = Path(__file__).parent / "index.html"

    if html_file.exists():
        return FileResponse(str(html_file))

    return {"message": "MediCare AI is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/assistant")
@app.post("/symptoms")
def assistant(request: SymptomRequest):
    try:
        result = health_assistant(request.symptom)

        if isinstance(result, dict):
            return result

        return {"response": str(result)}

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


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
            status_code=400,
            detail="Email already registered"
        )

    finally:
        conn.close()


@app.post("/appointments")
def book_appointment(appointment: AppointmentRequest):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO appointments
            (patient_name, department, appointment_date, date, time)
            VALUES (?, ?, ?, ?, ?)
        """, (
            appointment.patient_name,
            appointment.department,
            appointment.date,
            appointment.date,
            appointment.time
        ))

        conn.commit()

        return {
            "message": "Appointment booked successfully",
            "appointment": {
                "patient_name": appointment.patient_name,
                "date": appointment.date,
                "time": appointment.time,
                "department": appointment.department
            }
        }

    finally:
        conn.close()


@app.get("/appointments")
def get_appointments():
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, patient_name, date, time, department
            FROM appointments
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        appointments = [
            {
                "id": row[0],
                "patient_name": row[1],
                "date": row[2],
                "time": row[3],
                "department": row[4]
            }
            for row in rows
        ]

        return {"appointments": appointments}

    finally:
        conn.close()
