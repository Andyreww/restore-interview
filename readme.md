# Therapist/Paitient API 
A fast api project that manages therapists and patients that allows therapists and patients to be created, read, updated and deleted.

---

## Features
- Create Therapists and Patients
- Assigns Therapist to Patients (many to many relationship)
- Retrieve Therapists or Patient Information
- Retrieve all patients for a given therapist
- Remove a patient from a therapist or vise versa

---

## TEch Stack
- Python
- FastAPI
- Pydantic

Data currently stored in memory for simplicity to make sure the API logic and relationships work.

---

## Data Model
- A therapist can have many patients
- A patient can have many therapists

### Why?
My logic for having a many to many relationship was that in a real environment whether you are a doctor, therapist most of the time
they would have multiple patients since their schedules are vast. For the patients on why they could have many therapists, I thought that some patients could have different cases of problems wether that be physicial or mental problems that maybe 1 therapist can't solve directly, thus they would need to have more than 1 therapist. This is why I focused on the many to many relationships

---

## API Endpoints

### Therapists
- `POST /therapists/` – Create a therapist
- `GET /therapists/{therapist_id}` – Get therapist info
- `GET /therapists/{therapist_id}/patients` – Get all patients for a therapist
- `POST /therapists/{therapist_id}/patients/{patient_id}` – Assign patient to therapist
- `DELETE /therapists/{therapist_id}/patients/{patient_id}` – Remove patient from therapist
- `GET /therapists/` – Get all therapists
- `PATCH /therapists/{therapist_id}/name/{name}` - Updates the Therapists name

### Patients
- `POST /patients/` – Create a patient
- `GET /patients/{patient_id}` – Get patient info
- `GET /patients/` – Get all patients
- `PATCH /patients/{patient_id}/name/{name}"` - Updates the Patients name

---

## Running the Project

'pip install fastapi uvicorn'
'uvicorn main:app --reload'