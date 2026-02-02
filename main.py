from fastapi import FastAPI, HTTPException, Depends #FastAPI
from pydantic import BaseModel #Allow us to create classes for Therapist/Patients

#------------------------------------------------------------------#
# Connecting to the database
# Things for PostgreSQL
# Added 'ForeignKey' to imports so we can link tables!
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, declarative_base

db_user: str = 'postgres'
db_port: int = 5432
db_host: str = 'localhost'
db_password: str = '052003'

uri: str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/RESTORE-API'

engine = create_engine(uri)
session_local = sessionmaker(bind=engine, autoflush=True)

#session
def get_db():
    db = session_local() # Open the door
    try:
        yield db # Let the endpoint do the work
    finally:
        db.close() # Close the door

#------------------------------------------------------------------#
# Models
BASE = declarative_base()

#Creating our model or table
class TherapistsModel(BASE):
    __tablename__ = "therapists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class PatientsModel(BASE):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True) #db will handle the id's
    name = Column(String)
    age = Column(Integer)
    descriptions = Column(String)
    # This is the "Tag" that links a patient to a therapist!
    therapist_id = Column(Integer, ForeignKey("therapists.id"), nullable=True)

BASE.metadata.create_all(bind=engine) #Tells the db to build the tables based on my classes

#------------------------------------------------------------------#
#CRUD mindset
#When we create data we want to be able to:
#1. Create
#2. Read
#3. Update
#4. Delete
#------------------------------------------------------------------#

#Temporary in-memory db -> DELETED (We are using real DB now!)

#------------------------------------------------------------------#
#Big Idea We want Data Stored in a Database
#Endpoints of Therapist and Patients
#------------------------------------------------------------------#

#Step 1: What Are Therapists and Patients? (The Pydantic Schemas)
class TherapistsSchema(BaseModel):
    name: str
    # patients: list... -> Removed for now, simpler to query directly

class PatientsSchema(BaseModel):
    name: str
    # patient_id: int -> Removed, DB handles this
    descriptions: str | None = None
    age: int
    # therapists: list... -> Removed, we use Foreign Key now

#------------------------------------------------------------------#
app = FastAPI()

# Step 2:
# Simple Creating New Therapist & Patients
@app.post("/therapists/")
async def create_therapist(therapist: TherapistsSchema, db: Session = Depends(get_db)):
    #Creating the Db model using the data from the class we have
    new_therapist = TherapistsModel(name=therapist.name) 
    db.add(new_therapist)
    db.commit()
    db.refresh(new_therapist)
    return new_therapist

@app.post("/patients/")
async def create_patient(patient: PatientsSchema, db: Session = Depends(get_db)):
    # Create the model
    new_patient = PatientsModel(
        name=patient.name,
        age=patient.age,
        descriptions=patient.descriptions
    )
    # Save to DB
    db.add(new_patient) 
    db.commit()
    db.refresh(new_patient)
    return new_patient

#------------------------------------------------------------------#
#Step 3:
# Assigning Therapist to Patients
@app.post("/therapists/{therapist_id}/patients/{patient_id}")
async def assign_patient(therapist_id: int, patient_id: int, db: Session = Depends(get_db)): 

    # 1. Find the Therapist (Check if they exist)
    therapist = db.query(TherapistsModel).filter(TherapistsModel.id == therapist_id).first()
    if therapist is None:
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")
    
    # 2. Find the Patient
    patient = db.query(PatientsModel).filter(PatientsModel.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient with the id: {patient_id} doesn't exist")
    
    # 3. The "Assignment" Logic 
    # Instead of appending to a list, we just set the Foreign Key ID
    patient.therapist_id = therapist.id 
    
    db.commit() # Save the stamp
    db.refresh(patient)

    return {"message": f"Patient {patient.name} is now assigned to Therapist {therapist.name}"}

#------------------------------------------------------------------#
#Step 4:
# Getting Info From the Patients

@app.get("/patients/{patient_id}")
async def get_patient_info(patient_id: int, db: Session = Depends(get_db)):
    
    patient = db.query(PatientsModel).filter(PatientsModel.id == patient_id).first()

    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient with the id: {patient_id} doesn't exist")
    
    return patient

# Getting Info From the Therapists
@app.get("/therapists/{therapist_id}")
async def get_therapist_info(therapist_id: int, db: Session = Depends(get_db)):
    
    #Select * From therapist where id = therapist_id
    therapist = db.query(TherapistsModel).filter(TherapistsModel.id == therapist_id).first()

    # check if it even exists
    if therapist is None:
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")
    
    return therapist

@app.get("/patients/")
async def get_all_patients(db: Session = Depends(get_db)):
    # Select * from patients
    patients = db.query(PatientsModel).all()
    if not patients:
         # Optional: You can return empty list instead of 404 if you prefer
         raise HTTPException(status_code=404, detail=f"Currently No Patients Exist")
    return patients

@app.get("/therapists/")
async def get_all_therapists(db: Session = Depends(get_db)):
    # Select * from therapists
    therapists = db.query(TherapistsModel).all()
    if not therapists:
        raise HTTPException(status_code=404, detail=f"Currently No Therapists Exist")
    return therapists

#------------------------------------------------------------------#
#Step 5: Pull all of the Patients from a therapist
@app.get("/therapists/{therapist_id}/patients")
async def get_therapist_patients(therapist_id: int, db: Session = Depends(get_db)):

    # making sure that the therapist exists
    therapist = db.query(TherapistsModel).filter(TherapistsModel.id == therapist_id).first()
    if therapist is None:
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")

    # SQL Logic: SELECT * FROM patients WHERE therapist_id = {therapist_id}
    patients = db.query(PatientsModel).filter(PatientsModel.therapist_id == therapist_id).all()

    return patients

#------------------------------------------------------------------#
# Recap of where were at right now
# [x] We can create therapists
# [x] We can create patients
# [x] We can retrieve information from the specific therapist/patient based on id
# [x] Pull Patients from a therapist

#------------------------------------------------------------------#
# Completed 1/31/2026 
# [x] Deleting a Therapist from a Patient (Unassigning)

@app.delete("/therapists/{therapist_id}/patients/{patient_id}")
async def remove_patient_from_therapist(therapist_id: int, patient_id: int, db: Session = Depends(get_db)):

    # Find the patient
    patient = db.query(PatientsModel).filter(PatientsModel.id == patient_id).first()
    
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    # Check if they are actually assigned to this therapist
    if patient.therapist_id != therapist_id:
         raise HTTPException(status_code=404, detail="Patient is not assigned to this therapist")

    # The "Un-Assign" Logic
    patient.therapist_id = None # Remove the stamp
    
    db.commit()
    
    return {"message": "Patient unassigned successfully"}

#------------------------------------------------------------------#
# What needs to be done:
# [x] Deleting a Patient from a Therapist (Same logic as above essentially)

@app.delete("/patients/{patient_id}/therapists/{therapist_id}")
async def remove_therapist_from_patient(therapist_id: int, patient_id: int, db: Session = Depends(get_db)):
    # This is effectively the same as the function above, just named differently!
    # Reuse the logic
    return await remove_patient_from_therapist(therapist_id, patient_id, db)

#------------------------------------------------------------------#
#Step 6: Updating information

@app.patch("/therapists/{therapist_id}/name/{name}")
async def change_therapist_name(therapist_id: int, name:str, db: Session = Depends(get_db)):

    therapist_info = db.query(TherapistsModel).filter(TherapistsModel.id == therapist_id).first()

    #check if they exist
    if therapist_info is None:
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")
    
    #change the name value
    therapist_info.name = name

    #stage changes
    db.commit()
    db.refresh(therapist_info)
    return therapist_info

@app.patch("/patients/{patient_id}/name/{name}")
async def change_patient_name(patient_id: int, name:str, db: Session = Depends(get_db)):

    patient_info = db.query(PatientsModel).filter(PatientsModel.id == patient_id).first()

    #check if they exist
    if patient_info is None:
        raise HTTPException(status_code=404, detail=f"Patient with the id: {patient_id} doesn't exist")
    
    #change the name
    patient_info.name = name

    #stage change
    db.commit()
    db.refresh(patient_info)
    return patient_info