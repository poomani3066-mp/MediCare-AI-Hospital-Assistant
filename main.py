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
            appointment_date TEXT
        )
    """)

    columns = [
        row[1] for row in cursor.execute(
            "PRAGMA table_info(appointments)"
        ).fetchall()
    ]

    if "date" not in columns:
        cursor.execute(
            "ALTER TABLE appointments ADD COLUMN date TEXT"
        )

    if "time" not in columns:
        cursor.execute(
            "ALTER TABLE appointments ADD COLUMN time TEXT"
        )

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
    return {
        "message": "MediCare AI Hospital Assistant is running",
        "version": "2.0"
    }


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
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
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
            (patient_name, date, time, department)
            VALUES (?, ?, ?, ?)
        """, (
            appointment.patient_name,
            appointment.date,
            appointment.time,
            appointment.department
        ))

        conn.commit()

        return {
            "message": "Appointment booked successfully",
            "appointment": appointment.model_dump()
        }

    finally:
        conn.close()


@app.get("/appointments")
def get_appointments():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_name, date, time, department
        FROM appointments
    """)

    rows = cursor.fetchall()
    conn.close()

    appointments = [
        {
            "patient_name": row[0],
            "date": row[1],
            "time": row[2],
            "department": row[3]
        }
        for row in rows
    ]

    return {"appointments": appointments}


@app.get("/patients")
def get_patients():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()

    return {"patients": patients}
