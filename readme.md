# Therapist/Patient API
A FastAPI project that manages therapists and patients, allowing them to be created, read, updated, and deleted (CRUD).

---

## Features
- Create Therapists and Patients
- Assigns Therapist to Patients (one to many relationship)
- Retrieve Therapists or Patient Information
- Retrieve all patients for a given therapist
- Remove a patient from a therapist or vise versa

---

## Tech Stack
- Python
- FastAPI
- Pydantic
- SQLAlchemy (ORM)
- PostgreSQL (database)
---

## Data Model

- A therapist can have many patients.
- A patient can have one therapist.
- The relationship is stored via `Patients.therapist_id` (foreign key to `therapists.id`).
---

## API Endpoints

### Therapists
- `POST /therapists/` – Create a therapist
- `GET /therapists/{therapist_id}` – Get therapist info
- `GET /therapists/{therapist_id}/patients` – Get all patients for a therapist
- `PATCH /therapist/{therapist_id}/{name}` – Update therapist name
- `DELETE /therapists/{therapist_id}` – Delete a therapist

### Patients
- `POST /patients/` – Create a patient
- `GET /patients/{patient_id}` – Get patient info
- `PATCH /patients/{patient_id}/{name}` – Update patient name
- `DELETE /patients/{patient_id}` – Delete a patient

### Patient-Therapist Assignment
- `POST /therapists/{therapist_id}/patients/{patient_id}` – Assign patient to therapist
- `DELETE /patients/{patient_id}/{therapist_id}` – Remove therapist from patient

---
## Running the Project

1. Install dependencies:

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary
```

2. Run the API:
`uvicorn main:app --reload`

3. Open Swagger UI at:
`http://127.0.0.1:8000/docs#/`

## Background

This project was built as part of a Python interview take‑home.  

Requirements included:
- Create and get therapists and patients.
- Assign a therapist to a patient.
- Retrieve all patients for a given therapist.
- (Bonus) Use PostgreSQL with an ORM, host on GitHub with a README.
