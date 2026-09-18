def health_assistant(symptom: str):
    symptom = symptom.lower()

    if "fever" in symptom or "temperature" in symptom:
        return {
            "category": "General Medicine",
            "message": "Fever detected. Please stay hydrated and consult a doctor if symptoms persist."
        }

    if "headache" in symptom:
        return {
            "category": "General Medicine",
            "message": "For a headache, rest and stay hydrated. Consult a doctor if it is severe or persistent."
        }

    if "chest pain" in symptom:
        return {
            "category": "Emergency",
            "message": "Chest pain can require urgent medical attention. Please seek emergency medical care."
        }

    if "cough" in symptom:
        return {
            "category": "General Medicine",
            "message": "For cough symptoms, consider consulting a doctor if symptoms are severe or continue."
        }

    return {
        "category": "General Consultation",
        "message": "Please consult a qualified healthcare professional for proper evaluation."
    }
